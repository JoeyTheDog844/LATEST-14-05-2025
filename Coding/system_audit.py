import psutil
import socket
import subprocess
import os
import platform
import requests
import winreg
from datetime import datetime

def get_public_ip():
    try:
        return requests.get("https://api64.ipify.org?format=text").text
    except:
        return "Could not retrieve"

def get_local_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "Could not retrieve"

def run_wmic_command(command):
    try:
        result = subprocess.run(["wmic", *command.split()], capture_output=True, text=True)
        lines = result.stdout.strip().split("\n")
        return lines[1].strip() if len(lines) > 1 else "Unknown"
    except:
        return "Could not retrieve"

def run_powershell_command(command):
    try:
        result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True, shell=True)
        return result.stdout.strip() if result.stdout.strip() else "Unknown"
    except:
        return "Could not retrieve"

def get_registry_value(key, subkey, value_name):
    try:
        with winreg.OpenKey(key, subkey) as reg_key:
            return winreg.QueryValueEx(reg_key, value_name)[0]
    except:
        return "Unknown"

def format_powershell_date(date_str):
    try:
        return datetime.strptime(date_str[:14], "%Y%m%d%H%M%S").strftime("%d %B %Y %H:%M:%S")
    except:
        return "Unknown"

def get_system_details():
    try:
        install_date_raw = run_powershell_command("(Get-ItemProperty 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion').InstallDate")
        install_date_timestamp = int(install_date_raw) if install_date_raw.isdigit() else None
        from datetime import datetime, timezone  # Ensure timezone is imported

        install_date_formatted = datetime.fromtimestamp(install_date_timestamp, timezone.utc).strftime("%d %B %Y %H:%M:%S") if install_date_timestamp else "Unknown"


        system_info = {
            "PC Name": socket.gethostname(),
            "OS Name": get_registry_value(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion", "ProductName"),
            "Local IP Address": get_local_ip(),
            "Public IP Address": get_public_ip(),
            "Processor": platform.processor(),
            "Machine": platform.machine(),
            "CPU Usage": f"{psutil.cpu_percent(interval=1)}%",
            "Memory Usage": f"{psutil.virtual_memory().percent}%",
            "System Serial Number": run_wmic_command("bios get SerialNumber"),
            "Service Pack": get_registry_value(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion", "DisplayVersion"),
            "Product ID": get_registry_value(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion", "ProductId"),
            "BIOS Version": run_powershell_command("(Get-CimInstance Win32_BIOS).SMBIOSBIOSVersion"),
            "Windows Directory": os.environ.get("WINDIR", "Unknown"),
            "System Directory": os.environ.get("SYSTEMROOT", "Unknown"),
            "OS Install Date": install_date_formatted
        }
        
        return system_info
    except Exception as e:
        print("Error in get_system_details():", str(e))
        return {"Error": str(e)}

def get_all_users():
    try:
        command = "wmic useraccount get name"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        users = result.stdout.strip().split("\n")[1:]
        return ", ".join([user.strip() for user in users if user.strip()])
    except:
        return "Could not retrieve"

def generate_system_report():
    system_info = get_system_details()
    all_users = get_all_users()

    return f"""
🔍 System Audit Report

📌 System Info:
PC Name: {system_info["PC Name"]}
OS Name: {system_info["OS Name"]}
Local IP Address: {system_info["Local IP Address"]}
Public IP Address: {system_info["Public IP Address"]}
Processor: {system_info["Processor"]}
Machine: {system_info["Machine"]}
CPU Usage: {system_info["CPU Usage"]}
Memory Usage: {system_info["Memory Usage"]}
System Serial Number: {system_info["System Serial Number"]}
Service Pack: {system_info["Service Pack"]}
Product ID: {system_info["Product ID"]}
BIOS Version: {system_info["BIOS Version"]}
Windows Directory: {system_info["Windows Directory"]}
System Directory: {system_info["System Directory"]}
OS Install Date: {system_info["OS Install Date"]}

📌 All User Accounts:
{all_users}
"""

if __name__ == "__main__":
    print(generate_system_report())
