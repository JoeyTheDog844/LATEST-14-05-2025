import psutil
import socket
import subprocess
import os
import platform
import requests

# Function to get System Serial Number
def get_system_serial_number():
    try:
        command = "wmic bios get SerialNumber"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        lines = [line.strip() for line in result.stdout.split("\n") if line.strip()]
        serial_number = lines[1] if len(lines) > 1 else "Not Available"
        
        # Hide "Default string" or empty values
        if serial_number.lower() == "default string" or serial_number == "":
            return "Not Available"
        return serial_number
    except Exception as e:
        return f"Error: {e}"

# Function to get public IP
def get_public_ip():
    """
    Retrieve public IP address with multiple fallback methods
    """
    ip_services = [
        "https://api64.ipify.org?format=text",
        "https://ipinfo.io/ip",
        "https://api.ipify.org",
        "https://icanhazip.com"
    ]
    
    for service in ip_services:
        try:
            response = requests.get(service, timeout=5)
            if response.status_code == 200:
                # Clean and validate the IP address
                ip = response.text.strip()
                # Basic IP address validation
                if len(ip.split('.')) == 4:
                    return ip
        except requests.RequestException:
            continue  # Move to next service if this one fails
    
    return "Could not retrieve"

# Function to get local IP
def get_local_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "Could not retrieve"

# Function to get PC Name, OS Name, Windows Version, Machine Type, Processor, Service Pack
# Optimized function to fetch multiple system details in one call
def get_system_identity():
    pc_name = socket.gethostname()

    try:
        command = 'wmic os get Name, Version, SystemDirectory, WindowsDirectory, OSArchitecture /format:list'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output_lines = [line.strip() for line in result.stdout.split("\n") if "=" in line]

        system_info = {}
        for line in output_lines:
            key, value = line.split("=")
            system_info[key.strip()] = value.strip()

        os_name = system_info.get("Name", "Could not retrieve").split("|")[0]  # Extract OS Name
        windows_version = system_info.get("Version", "Could not retrieve")
        system_directory = system_info.get("SystemDirectory", "Could not retrieve")
        windows_directory = system_info.get("WindowsDirectory", "Could not retrieve")
        machine_type = system_info.get("OSArchitecture", "Could not retrieve")  # 64-bit or 32-bit

    except:
        os_name = "Could not retrieve"
        windows_version = "Could not retrieve"
        system_directory = "Could not retrieve"
        windows_directory = "Could not retrieve"
        machine_type = "Could not retrieve"

    # Fetch Processor Name (Optimized)
    try:
        cpu_output = subprocess.run("wmic cpu get Name", shell=True, capture_output=True, text=True)
        cpu_lines = [line.strip() for line in cpu_output.stdout.split("\n") if line.strip()]
        processor = cpu_lines[1] if len(cpu_lines) > 1 else platform.processor()
    except:
        processor = platform.processor()

    # Fetch Service Pack Version
    try:
        sp_output = subprocess.run("wmic os get ServicePackMajorVersion, ServicePackMinorVersion", shell=True, capture_output=True, text=True)
        sp_lines = [line.strip() for line in sp_output.stdout.split("\n") if line.strip()]
        if len(sp_lines) > 1:
            sp_major, sp_minor = sp_lines[1].split()
            service_pack = f"Service Pack {sp_major}.{sp_minor}" if sp_major != "0" else "No Service Pack Installed"
        else:
            service_pack = "No Service Pack Installed"
    except:
        service_pack = "No Service Pack Installed"

    return pc_name, os_name, windows_version, machine_type, processor, service_pack, system_directory, windows_directory

def get_os_install_date():
    try:
        command = 'wmic os get InstallDate'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        lines = [line.strip() for line in result.stdout.split("\n") if line.strip()]
        install_date_raw = lines[1] if len(lines) > 1 else "Could not retrieve"
        
        if install_date_raw != "Could not retrieve":
            # Formatting Install Date (YYYYMMDDHHMMSS) to a readable format
            formatted_date = f"{install_date_raw[:4]}-{install_date_raw[4:6]}-{install_date_raw[6:8]}"
            return formatted_date
        
        return install_date_raw
    except:
        return "Could not retrieve"

def check_clear_desktop():
    try:
        desktop_path = os.path.join(os.environ["USERPROFILE"], "Desktop")
        items = os.listdir(desktop_path)  # List all files and folders on desktop
        file_count = len(items)

        if file_count == 0:
            return "Clear Desktop Maintained (No files on desktop)"
        elif file_count < 5:
            return f"Clear Desktop Maintained ({file_count} files/folders)"
        elif file_count < 10:
            return f"Partially Maintained ({file_count} files/folders)"
        else:
            return f"Desktop is Cluttered ({file_count} files/folders)"

    except Exception as e:
        return f"Error Checking Desktop Status ({str(e)})"

# Function to get Domain information
def get_domain():
    try:
        command = 'wmic computersystem get Domain'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        lines = [line.strip() for line in result.stdout.split("\n") if line.strip()]
        domain = lines[1] if len(lines) > 1 else "WORKGROUP"
        return domain
    except:
        return "Could not retrieve"

# Function to get BIOS Version
def get_bios_version():
    try:
        command = "wmic bios get SMBIOSBIOSVersion"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        lines = [line.strip() for line in result.stdout.split("\n") if line.strip()]
        return lines[1] if len(lines) > 1 else "Could not retrieve"
    except:
        return "Could not retrieve"

# Function to get OS Configuration
def get_os_configuration():
    try:
        output = os.popen('systeminfo | findstr /C:"OS Configuration"').read()
        return output.strip().split(":")[1].strip() if ":" in output else "Not Available"
    except Exception as e:
        return f"Error: {e}"

def classify_network(ip_address):
    if ip_address.startswith("10.69."):
        return "DRONA"
    elif ip_address.startswith("10.86.0."):
        return "CIAG"
    else:
        return "Project Network or Unknown"

def get_plug_and_play_status():
    try:
        # ✅ Check if Plug and Play (PnP) is enabled/disabled
        cmd = 'powershell -Command "(Get-ItemProperty -Path \'HKLM:\\SYSTEM\\CurrentControlSet\\Services\\PlugPlay\' -Name Start).Start"'
        output = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()

        if output == "2":
            return "Plug and Play Enabled (Automatic Start)"
        elif output == "3":
            return "Plug and Play Enabled (Manual Start)"
        elif output == "4":
            return "Plug and Play Disabled"
        else:
            return f"Plug and Play Status Unknown (Registry Value: {output})"

    except:
        return "Error Retrieving Plug and Play Status"
    
# Function to get Windows Product ID
def get_windows_product_id():
    try:
        command = "wmic os get SerialNumber"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        lines = [line.strip() for line in result.stdout.split("\n") if line.strip()]
        return lines[1] if len(lines) > 1 else "Could not retrieve"
    except Exception as e:
        return f"Error: {e}"

# Function to get last Windows update
def get_last_windows_update():
    try:
        command = "wmic qfe get HotFixID, InstalledOn"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        updates = [line.strip() for line in result.stdout.split("\n") if line.strip() and "HotFixID" not in line]
        
        if not updates:
            return "No update history found."
        
        formatted_updates = "\n".join([f"- {update}" for update in updates])
        return formatted_updates
    except Exception as e:
        return f"Error: {e}"

def get_last_system_update():
    try:
        command = 'powershell "Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -ExpandProperty InstalledOn -First 1"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        last_update_date = result.stdout.strip()

        # Ensure the output contains a full date
        if last_update_date and len(last_update_date.split()) >= 3:
            return " ".join(last_update_date.split()[:3])  # Keeps day, month, and year
        return "Could not retrieve"
    except:
        return "Could not retrieve"
    
# Function to check Windows License Status
def get_windows_license_status():
    try:
        command = 'powershell "(Get-WmiObject -query \'select LicenseStatus from SoftwareLicensingProduct where PartialProductKey is not null\').LicenseStatus"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        status_code = result.stdout.strip()

        # Ensure status_code is valid
        if not status_code:
            return "Could not retrieve"

        license_status_map = {
            "0": "Not Activated",
            "1": "Activated",
            "2": "Activation Expired",
            "3": "Activation Problem (Hardware Changed)",
            "4": "Pirated Copy Detected",
            "5": "Activation Required (Watermark Visible)",
            "6": "Extended Activation Period",
            "7": "License Expired",
            "8": "Activation Grace Period"
        }

        return license_status_map.get(status_code, "Unknown License Status")
    except:
        return "Could not retrieve"

def get_bitlocker_status():
    try:
        # Run the BitLocker status command
        cmd = 'powershell -ExecutionPolicy Bypass -NoProfile -Command "manage-bde -status C:"'
        output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL).strip()

        # Check for different BitLocker statuses
        if "Protection On" in output:
            return "BitLocker is Enabled (Drive is encrypted)"
        elif "Protection Off" in output and "Percentage Encrypted: 0.0%" in output:
            return "BitLocker is Disabled (Drive is not encrypted)"
        elif "BitLocker Version: None" in output:
            return "BitLocker Not Available (Not installed on this system)"
        else:
            return "BitLocker Status Unknown (Check manually)"

    except subprocess.CalledProcessError:
        return "Error: (Requires Admin Privileges)"

# Function to check Internet Connectivity
def check_connectivity():
    try:
        command = "ping -n 1 8.8.8.8" if platform.system().lower() == "windows" else "ping -c 1 8.8.8.8"
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return "Connected" if result.returncode == 0 else "No Internet Connection"
    except:
        return "Could not determine"

def get_wifi_ssid():
    try:
        command = 'netsh wlan show interfaces | findstr SSID'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        lines = [line.strip() for line in result.stdout.split("\n") if "SSID" in line and "BSSID" not in line]

        if lines:
            ssid = lines[0].split(":")[1].strip()
            return ssid
        else:
            return "No Wi-Fi Connection"
    except:
        return "Could not retrieve Wi-Fi SSID"

def get_geolocation_status():
    try:
        # ✅ Check if Location Services is enabled/disabled
        cmd = 'powershell -Command "(Get-ItemProperty -Path \'HKLM:\\SYSTEM\\CurrentControlSet\\Services\\lfsvc\' -Name Start).Start"'
        output = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()

        if output == "3":
            return "Geo-Location Services Enabled"
        elif output == "4":
            return "Geo-Location Services Disabled"
        else:
            return f"Geo-Location Status Unknown (Registry Value: {output})"

    except:
        return "Error Retrieving Geo-Location Status"
  
def get_bluetooth_status():
    try:
        # ✅ Check if a Bluetooth adapter exists
        cmd = 'powershell -Command "Get-PnpDevice -Class Bluetooth | Select-Object -ExpandProperty Status"'
        output = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()

        if not output:  # ✅ No Bluetooth adapter detected
            return "No Bluetooth Adapter Found"

        if "OK" in output:
            return "Bluetooth Enabled"
        else:
            return "Bluetooth Disabled"

    except subprocess.CalledProcessError:
        return "No Bluetooth Adapter Found"  # ✅ If command fails, assume no Bluetooth hardware

# Function to get all user account names
def get_all_user_accounts():
    try:
        command = 'wmic useraccount get name'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        lines = [line.strip() for line in result.stdout.split("\n") if line.strip()]
        users = lines[1:]  # Skip header
        return ", ".join(users) if users else "No users found."
    except Exception as e:
        return f"Error: {e}"

# Function to list desktop files and count them
def get_desktop_files():
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    try:
        files = os.listdir(desktop_path)
        file_count = len(files)
        file_list = "\n".join(files[:10]) if files else "No files found."
        return file_list, file_count
    except:
        return "Could not retrieve desktop files.", 0

# Function to get system info
def get_system_info():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent
    pc_name, os_name, windows_version, machine_type, processor, service_pack, system_directory, windows_directory = get_system_identity()

    return {
        "System Serial Number": get_system_serial_number(),
        "PC Name": pc_name,
        "OS Name": os_name,
        "Windows Version": windows_version,
        "BIOS Version": get_bios_version(),
        "Machine Type": machine_type,
        "Processor": processor,
        "Product ID": get_windows_product_id(),
        "Service Pack Status": service_pack,
        "OS Configuration": get_os_configuration(),
        "Plug and Play Status": get_plug_and_play_status(),
        "Windows Directory": windows_directory,
        "System Directory": system_directory,
        "Clear Desktop Status": check_clear_desktop(),
        "OS Install Date": get_os_install_date(),
        "Domain": get_domain(),
        "System Last Updated On": get_last_system_update(),
        "Windows License Status": get_windows_license_status(),
        "BitLocker Status": get_bitlocker_status(),
        "Internet Connectivity": check_connectivity(),
        "Geo-Location Status": get_geolocation_status(),
        "Bluetooth Status": get_bluetooth_status(),
        "Local IP Address": get_local_ip(),
        "Public IP Address": get_public_ip(),
        "CPU Usage": f"{cpu_usage}%",
        "Memory Usage": f"{memory_usage}%",
    }

# Function to get Network Interface Name (Wi-Fi & Ethernet)
def get_network_interface():
    try:
        # ✅ Get active network adapter (Ethernet/Wi-Fi)
        command = 'wmic nic where "NetEnabled=True" get Name'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        lines = [line.strip() for line in result.stdout.split("\n") if line.strip()]

        active_interface = lines[1] if len(lines) > 1 else "Unknown"

        # ✅ Check if Wi-Fi adapter exists
        wifi_command = 'powershell -Command "Get-NetAdapter | Where-Object {$_.Name -match \'Wi-Fi\'} | Select-Object -ExpandProperty Name"'
        wifi_result = subprocess.run(wifi_command, shell=True, capture_output=True, text=True)
        wifi_lines = [line.strip() for line in wifi_result.stdout.split("\n") if line.strip()]
        wifi_adapter = wifi_lines[0] if wifi_lines else "No Wi-Fi Adapter Found"

        # ✅ Check if Wi-Fi is ON or OFF
        wifi_status_command = 'powershell -Command "Get-NetAdapter | Where-Object {$_.Name -match \'Wi-Fi\'} | Select-Object -ExpandProperty Status"'
        wifi_status_result = subprocess.run(wifi_status_command, shell=True, capture_output=True, text=True)
        wifi_status = wifi_status_result.stdout.strip()

        if "Up" in wifi_status:
            wifi_status = "Wi-Fi is ON"
        elif "Down" in wifi_status:
            wifi_status = "Wi-Fi is OFF"
        else:
            wifi_status = "Wi-Fi Status Unknown"

        return active_interface, wifi_adapter, wifi_status

    except:
        return "Unknown", "Could not retrieve", "Unknown Wi-Fi Status"
    
# Function to get network details
def get_network_details():
    try:
        ip_address = get_local_ip()
        mac_address = "Unknown"
        connection_type = "Unknown"
        wifi_ssid = get_wifi_ssid()

        # ✅ Get network interface details
        active_interface, wifi_interface, wifi_status = get_network_interface()

        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == psutil.AF_LINK:
                    mac_address = addr.address
                    connection_type = "Wi-Fi" if "Wi-Fi" in interface else "Ethernet"

         # ✅ Classify network type based on IP
        network_type = classify_network(ip_address)

        return {
            "MAC Address": mac_address,
            "Connection Type": connection_type,
            "Active Network Interface": active_interface,
            "Wi-Fi Interface": wifi_interface,
            "Wi-Fi Status": wifi_status,
            "Wi-Fi SSID": wifi_ssid,  
            "IP Address": ip_address,
            "Network Type": network_type
        }
    except Exception as e:
        return {
            "MAC Address": "Unknown",
            "Connection Type": "Unknown",
            "Active Network Interface": "Unknown",
            "Wi-Fi Interface": "Could not retrieve",
            "Wi-Fi Status": "Unknown",
            "Wi-Fi SSID": "Could not retrieve",  
            "IP Address": "Unknown",
            "Network Type": "Unknown",
            "Error": str(e)
        }

# Generate system report
def generate_system_report():
    system_info = get_system_info()
    network_details = get_network_details()
    network_type = classify_network(network_details["IP Address"])
    desktop_files, file_count = get_desktop_files()
    user_accounts = get_all_user_accounts()

    return f"""
🔍 System Audit Report

📌 System Info:
System Serial Number: {system_info["System Serial Number"]}
PC Name: {system_info["PC Name"]}
OS Name: {system_info["OS Name"]}
Windows Version: {system_info["Windows Version"]}
BIOS Version: {system_info["BIOS Version"]}
Machine Type: {system_info["Machine Type"]}
Processor: {system_info["Processor"]}
Product ID: {system_info["Product ID"]}
Service Pack Status: {system_info["Service Pack Status"]}
OS Configuration: {system_info["OS Configuration"]}
Plug and Play Status: {system_info["Plug and Play Status"]}
Windows Directory: {system_info["Windows Directory"]}
System Directory: {system_info["System Directory"]}
Clear Desktop Status: {system_info["Clear Desktop Status"]}
OS Install Date: {system_info["OS Install Date"]}
Domain: {system_info["Domain"]}
System Last Updated On: {system_info["System Last Updated On"]}
Windows License Status: {system_info["Windows License Status"]}
BitLocker Status: {system_info["BitLocker Status"]}
Internet Connectivity: {system_info["Internet Connectivity"]}
Geo-Location Status: {system_info["Geo-Location Status"]}
Bluetooth Status: {system_info["Bluetooth Status"]}
Local IP Address: {system_info["Local IP Address"]}
Public IP Address: {system_info["Public IP Address"]}
CPU Usage: {system_info["CPU Usage"]}
Memory Usage: {system_info["Memory Usage"]}

📌 Network Details:
Connection Type: {network_details["Connection Type"]}
Active Network Interface: {network_details["Active Network Interface"]}
Wi-Fi Interface: {network_details["Wi-Fi Interface"]}
Wi-Fi Status: {network_details["Wi-Fi Status"]}
Wi-Fi SSID: {network_details["Wi-Fi SSID"]}
MAC Address: {network_details["MAC Address"]}
IP Address: {network_details["IP Address"]}
Network Type: {network_type}

📌 User Accounts:
{user_accounts}

📌 Last Windows Update:
{get_last_windows_update()}

📌 Desktop Files ({file_count} total):
{desktop_files}
"""

if __name__ == "__main__":
    print(generate_system_report())