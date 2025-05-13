import winreg

# Registry paths and keys
USBSTOR_PATH = r"SYSTEM\CurrentControlSet\Services\USBSTOR"
CDROM_PATH = r"SYSTEM\CurrentControlSet\Services\cdrom"
START_VALUE = "Start"

# Common helper to get the registry DWORD value
def get_reg_dword(path, name):
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, name)
            return value
    except Exception as e:
        print(f"[ERROR] Reading registry: {e}")
        return None

# Common helper to set a registry DWORD value
def set_reg_dword(path, name, value):
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
            return True
    except Exception as e:
        print(f"[ERROR] Writing registry: {e}")
        return False

# ---------------------- USB STORAGE CONTROL ----------------------
def get_usb_status():
    value = get_reg_dword(USBSTOR_PATH, START_VALUE)
    if value == 4:
        return False  # Disabled
    elif value in [0, 1, 2, 3]:  # Enabled cases
        return True
    return None  # Unknown/Error

def set_usb_status(disable=True):
    val = 4 if disable else 3
    if set_reg_dword(USBSTOR_PATH, START_VALUE, val):
        return f"USB storage access {'disabled' if disable else 'enabled'} successfully."
    return "Failed to update USB storage access."

# ---------------------- CD/DVD DRIVE CONTROL ----------------------
def get_cd_status():
    value = get_reg_dword(CDROM_PATH, START_VALUE)
    if value == 4:
        return False  # Disabled
    elif value in [0, 1, 2, 3]:  # Enabled cases
        return True
    return None  # Unknown/Error

def set_cd_status(disable=True):
    val = 4 if disable else 1
    if set_reg_dword(CDROM_PATH, START_VALUE, val):
        return f"CD/DVD drive access {'disabled' if disable else 'enabled'} successfully."
    return "Failed to update CD/DVD drive access."
