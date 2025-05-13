# security_scoring.py

from system_information import get_system_info
from security_logs import (
    get_antivirus_status,
    get_usb_device_control_status,
    get_autoplay_status,
    get_rdp_status,
    get_telnet_status,
    get_default_share_status,
    get_shared_folder_status,
    get_login_password_status,
    get_lockout_policy_status,
    get_password_policy_status
)
from unwanted_softwares import detect_unwanted_software

# ✅ Helper functions

def get_geolocation_status_systeminfo():
    status = get_system_info().get("Geo-Location Status")
    if not status:
        return False
    return "disabled" in status.strip().lower()

def is_autoplay_disabled():
    return get_autoplay_status().strip().lower() == "autoplay is disabled"

def get_plug_and_play_status_systeminfo():
    info = get_system_info()
    return "Disabled" in info.get("Plug and Play Status", "Unknown")

def is_desktop_clear():
    from system_information import get_desktop_files
    _, file_count = get_desktop_files()
    return file_count <= 10

def is_wifi_disabled():
    from system_information import get_network_details
    details = get_network_details()
    wifi_status = details.get("Wi-Fi Status", "Enabled")
    return "Disabled" in wifi_status

def login_password_set():
    login_status = get_login_password_status()
    return "Set" in login_status

# ✅ Final function to calculate the score
def calculate_security_health():
    compulsory_score = sum(1 for check in COMPULSORY_PARAMETERS.values() if check() == "YES")
    desirable_score = sum(1 for check in DESIRABLE_PARAMETERS.values() if check() == "YES")

    compulsory_results = {name: check() for name, check in COMPULSORY_PARAMETERS.items()}
    desirable_results = {name: check() for name, check in DESIRABLE_PARAMETERS.items()}

    return compulsory_score, desirable_score, compulsory_results, desirable_results

def is_firewall_enabled():
    from security_logs import get_firewall_status
    status = get_firewall_status()

    # ✅ Check if all three profiles are "Enabled"
    return all(profile in status for profile in [
        "Domain Profile: Enabled",
        "Private Profile: Enabled",
        "Public Profile: Enabled"
    ])

def get_tcp_port_count():
    from security_logs import get_open_ports
    ports = get_open_ports()
    return len(ports.get("tcp", []))

def get_udp_port_count():
    from security_logs import get_open_ports
    ports = get_open_ports()
    return len(ports.get("udp", []))

# ✅ Compulsory and Desirable Parameters
COMPULSORY_PARAMETERS = {
    "Antivirus Installed": lambda: "YES" if get_antivirus_status().lower() != "not installed" else "NO",
    "Firewall Enabled": lambda: "YES" if is_firewall_enabled() else "NO",
    "USB Storage Media Blocked": lambda: "YES" if "Blocked" in get_usb_device_control_status() else "NO",
    "AutoPlay Disabled": lambda: "YES" if is_autoplay_disabled() else "NO",
    "Remote Desktop Disabled (RDP)": lambda: "YES" if "disabled" in get_rdp_status().lower() else "NO",
    "Telnet Service Disabled": lambda: "NO" if "Running" in (get_telnet_status() or "") else "YES",
    "Default Share Disabled": lambda: "YES" if "Disabled" in get_default_share_status() else "NO",
    "No Shared Folders Configured": lambda: "YES" if len(get_shared_folder_status()) == 0 else "NO",
    "No Shared Folders Configured": lambda: "YES" if "Not Configured" in get_shared_folder_status() else "NO",
    "Wi-Fi Disabled": lambda: "YES" if is_wifi_disabled() else "NO",
    "Login Password Set": lambda: "YES" if login_password_set() else "NO",
}

DESIRABLE_PARAMETERS = {
    "Geo-Location Disabled": lambda: "YES" if get_geolocation_status_systeminfo() else "NO",
    "Plug and Play Disabled": lambda: "YES" if get_plug_and_play_status_systeminfo() else "NO",
    "Clear Desktop Maintained": lambda: "YES" if is_desktop_clear() else "NO",
    "System Lockout Policy Configured": lambda: "YES" if "Configured" in get_lockout_policy_status() else "NO",
    "Password Policy Configured": lambda: "YES" if "Configured" in get_password_policy_status() else "NO",
    "Open TCP Ports < 10": lambda: "YES" if get_tcp_port_count() < 10 else "NO",
    "Open UDP Ports < 10": lambda: "YES" if get_udp_port_count() < 10 else "NO",
}



