import subprocess
import re
from tabulate import tabulate

# Known smartphone/dongle vendors
VENDOR_MAP = {
    "VID_05AC": "Apple",
    "VID_04E8": "Samsung",
    "VID_18D1": "Google",
    "VID_0BB4": "HTC",
    "VID_2A70": "OnePlus",
    "VID_2C3F": "Realme",
    "VID_2717": "Xiaomi",
    "VID_22D9": "Oppo",
    "VID_297F": "Vivo"
}

def detect_vendor_from_vid(serial):
    for vid, brand in VENDOR_MAP.items():
        if vid in serial.upper():
            return brand
    return "Unknown"

def detect_type(device_name, vendor):
    name_lower = device_name.lower()
    if any(keyword in name_lower for keyword in ["ethernet", "modem", "ndis", "tethering"]):
        return "Dongle"
    elif vendor in VENDOR_MAP.values():
        return "Smartphone"
    else:
        return "Smartphone/Dongle"

def get_smartphone_dongle_history():
    try:
        result = subprocess.check_output(
            'reg query HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Enum\\USB /s',
            shell=True, text=True, errors='ignore'
        )
    except subprocess.CalledProcessError:
        return []

    devices = []
    blocks = result.split("HKEY_LOCAL_MACHINE")[1:]

    for block in blocks:
        if len(devices) >= 10:
            break

        block_text = "HKEY_LOCAL_MACHINE" + block
        lines = block_text.splitlines()

        serial = ""
        device_name_candidates = []

        for line in lines:
            if "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Enum\\USB\\" in line:
                serial_parts = line.strip().split("\\")
                if len(serial_parts) > 5:
                    candidate = serial_parts[-1]
                    if len(candidate) >= 4 and all(x not in candidate.lower() for x in ["parameters", "properties"]):
                        serial = candidate

            if any(key in line.lower() for key in ["devicedesc", "friendlyname", "device description", "class", "service"]):
                match = re.search(r"REG_SZ\s+(.*)", line)
                if match:
                    raw_name = match.group(1).strip()
                    cleaned = re.sub(r'^@[\w.]+,?%?[^;]*%;?', '', raw_name)
                    if cleaned.lower() not in device_name_candidates:
                        device_name_candidates.append(cleaned)

        vendor = detect_vendor_from_vid(serial)
        if vendor != "Unknown":
            device_name = device_name_candidates[0] if device_name_candidates else f"{vendor} Device"
            device_type = detect_type(device_name, vendor)
            devices.append({
                "Device": device_name,
                "Vendor": vendor,
                "Type": device_type,
                "Serial": serial or "N/A"
            })

    return devices

if __name__ == "__main__":
    devices = get_smartphone_dongle_history()
    print("\nSmartphone / Dongle Connection History")
    if devices:
        print(tabulate(
            [(i + 1, d["Device"], d["Vendor"], d["Type"], d["Serial"]) for i, d in enumerate(devices)],
            headers=["S.No", "Device", "Vendor", "Type", "Serial Number"],
            tablefmt="plain"
        ))
    else:
        print("No smartphones or USB dongles detected based on vendor IDs.")
