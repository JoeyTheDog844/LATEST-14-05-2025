import winreg
import subprocess
from tkinter import messagebox

REG_PATH = r"SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters"
REG_NAME = "AutoShareWks"

def get_admin_share_status():
    """
    Returns True if default admin shares are disabled (AutoShareWks = 0),
    False if enabled (1 or key missing).
    """
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REG_PATH, 0, winreg.KEY_READ) as reg:
            value, _ = winreg.QueryValueEx(reg, REG_NAME)
            return value == 0
    except FileNotFoundError:
        return False
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read registry:\n{e}")
        return False

def set_admin_share_status(disable=True):
    """
    Sets AutoShareWks value to disable or enable default admin shares.
    """
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REG_PATH, 0, winreg.KEY_SET_VALUE) as reg:
            winreg.SetValueEx(reg, REG_NAME, 0, winreg.REG_DWORD, 0 if disable else 1)
        return "Default Admin Shares successfully " + ("disabled." if disable else "enabled.")
    except PermissionError:
        return "❌ Permission Denied: Please run the app as Administrator."
    except Exception as e:
        return f"❌ Error updating registry:\n{e}"

def is_server_service_available():
    try:
        output = subprocess.check_output(
            'powershell -Command "Get-Service -Name LanmanServer | Select-Object -ExpandProperty Status"',
            shell=True
        ).decode().strip().lower()
        return output in ["running", "stopped"]
    except:
        return False

def ensure_server_service_running():
    try:
        output = subprocess.check_output(
            'powershell -Command "Get-Service -Name LanmanServer | Select-Object -ExpandProperty Status"',
            shell=True
        ).decode().strip()
        return output.lower() == "running"
    except Exception:
        return False

def disable_shared_folders():
    if not is_server_service_available():
        return "❌ Cannot remove shared folders: 'Server' (LanmanServer) service is not available on this system."

    try:
        cmd = [
            "powershell",
            "-Command",
            "Get-SmbShare | Where-Object { $_.Name -notmatch '^[A-Za-z]+\\$$' } | ForEach-Object { Remove-SmbShare -Name $_.Name -Force }"
        ]
        subprocess.run(cmd, check=True)
        return "✅ All user-configured shared folders have been removed."
    except subprocess.CalledProcessError as e:
        return f"❌ Error disabling shared folders:\n{e.output.decode('utf-8') if e.output else str(e)}"

