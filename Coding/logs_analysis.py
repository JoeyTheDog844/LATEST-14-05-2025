import subprocess
import re

# ✅ Suppress black CMD windows
startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

def get_usb_logs():
    """Fetch last 50 USB-related logs with deep details for cybersecurity auditing."""
    command = 'wevtutil qe "Microsoft-Windows-DriverFrameworks-UserMode/Operational" /c:50 /f:text'
    result = subprocess.run(command, shell=True, capture_output=True, text=True, startupinfo=startupinfo)
    logs = result.stdout.strip().split("\n\n")  # Split log entries

    parsed_logs = []
    for log in logs:
        if "Event ID:" in log:
            lines = log.split("\n")
            
            # Extract relevant details
            event_id = next((line.split(":")[1].strip() for line in lines if "Event ID" in line), "Unknown")
            timestamp = next((line.split(":")[1].strip() for line in lines if "Date" in line), "Unknown")
            device_id = next((line.split(":")[1].strip() for line in lines if "USB\\VID" in line), "Unknown")
            serial_number = next((line.split(":")[1].strip() for line in lines if "Serial Number" in line), "Unknown")
            user = next((line.split(":")[1].strip() for line in lines if "User" in line), "SYSTEM")
            driver_name = next((line.split(":")[1].strip() for line in lines if "Driver Name" in line), "Unknown")
            driver_version = next((line.split(":")[1].strip() for line in lines if "Driver Version" in line), "Unknown")
            port_used = next((line.split(":")[1].strip() for line in lines if "Port" in line), "Unknown")
            description = next((line.strip() for line in lines if "Description:" in line), "No Description")
            installation_status = "Success" if "Status: Success" in log else "Failure"
            error_code = next((match.group(1) if (match := re.search(r'Error Code: (\d+)', line)) else None for line in lines), "None")

            # Flag unknown devices
            flagged_device = "Suspicious Device" if "VID_0000" in device_id or "Unknown" in driver_name else "Known Device"

            parsed_logs.append(f"""
📌 **Event ID:** {event_id}
        **Timestamp:** {timestamp}
        **Device ID:** {device_id}
        **Serial Number:** {serial_number}
        **User:** {user}
        **USB Port Used:** {port_used}
        **Driver:** {driver_name} (Version: {driver_version})
        **Description:** {description}
        **Installation Status:** {installation_status}
        **Error Code:** {error_code}
        **Security Check:** {flagged_device}
            """.strip())

    usb_logs = "\n\n".join(parsed_logs) if parsed_logs else "No USB activity detected."
    return usb_logs.strip()


def get_security_logs():
    """Fetch and clean last 50 security logs."""
    command = 'wevtutil qe Security /c:50 /f:text'
    result = subprocess.run(command, shell=True, capture_output=True, text=True, startupinfo=startupinfo)
    
    logs = result.stdout.strip().split("\n\n")
    parsed_logs = []
    for log in logs:
        if "Event ID:" in log:
            lines = log.split("\n")
            event_id = next((line.split(":")[1].strip() for line in lines if "Event ID" in line), "Unknown")
            time_created = next((line.split(":")[1].strip() for line in lines if "TimeCreated" in line), "Unknown")
            account_name = next((line.split(":")[1].strip() for line in lines if "Account Name" in line), "Unknown")
            ip_address = next((line.split(":")[1].strip() for line in lines if "IpAddress" in line), "Unknown")
            logon_type = next((line.split(":")[1].strip() for line in lines if "Logon Type" in line), "Unknown")
            
            parsed_logs.append(f"""
🔐 **Event ID:** {event_id}
    **Timestamp:** {time_created}
    **Account:** {account_name}
    **IP Address:** {ip_address}
    **Logon Type:** {logon_type}
            """.strip())
    
    return "\n\n".join(parsed_logs) if parsed_logs else "No Security Logs Found."

def get_system_logs():
    """Fetch and clean last 50 system logs."""
    command = 'wevtutil qe System /c:50 /f:text'
    result = subprocess.run(command, shell=True, capture_output=True, text=True, startupinfo=startupinfo)

    logs = result.stdout.strip().split("\n\n")
    parsed_logs = []
    
    for log in logs:
        if "Event ID:" in log:
            lines = log.split("\n")
            event_id = next((line.split(":")[1].strip() for line in lines if "Event ID" in line), "Unknown")
            timestamp = next((line.split(":")[1].strip() for line in lines if "TimeCreated" in line), "Unknown")
            source = next((line.split(":")[1].strip() for line in lines if "Provider Name" in line), "Unknown")
            level = next((line.split(":")[1].strip() for line in lines if "Level" in line), "Unknown")

            parsed_logs.append(f"""
⚙️ **Event ID:** {event_id}
    **Timestamp:** {timestamp}
    **Source:** {source}
    **Level:** {level}
            """.strip())
    
    return "\n\n".join(parsed_logs) if parsed_logs else "No System Logs Found."

def get_application_logs():
    """Fetch and clean last 50 application logs."""
    command = 'wevtutil qe Application /c:50 /f:text'
    result = subprocess.run(command, shell=True, capture_output=True, text=True, startupinfo=startupinfo)

    logs = result.stdout.strip().split("\n\n")
    parsed_logs = []

    for log in logs:
        if "Event ID:" in log:
            lines = log.split("\n")
            event_id = next((line.split(":")[1].strip() for line in lines if "Event ID" in line), "Unknown")
            timestamp = next((line.split(":")[1].strip() for line in lines if "TimeCreated" in line), "Unknown")
            source = next((line.split(":")[1].strip() for line in lines if "Provider Name" in line), "Unknown")
            level = next((line.split(":")[1].strip() for line in lines if "Level" in line), "Unknown")

            parsed_logs.append(f"""
🗂️ **Event ID:** {event_id}
    **Timestamp:** {timestamp}
    **Application:** {source}
    **Level:** {level}
            """.strip())

    return "\n\n".join(parsed_logs) if parsed_logs else "No Application Logs Found."

def get_dns_logs():
    """Fetch and clean last 50 DNS lookup logs, or fallback to DNS cache if unavailable."""
    
    # Check if DNS-Client Operational Log is enabled
    check_command = 'wevtutil gl "Microsoft-Windows-DNS-Client/Operational"'
    check_result = subprocess.run(check_command, shell=True, capture_output=True, text=True, startupinfo=startupinfo)
    
    if "enabled: false" in check_result.stdout.lower():
        # Fallback to DNS Cache
        fallback_result = subprocess.run('ipconfig /displaydns', shell=True, capture_output=True, text=True, startupinfo=startupinfo)
        fallback_output = fallback_result.stdout.strip()
        lines = fallback_output.splitlines()
        trimmed_output = "\n".join(lines[:100])
        return trimmed_output + "\n\n[Only top 100 DNS cache lines shown]" if trimmed_output else "DNS Client Logs are disabled and no DNS Cache found."

    
    # Fetch last 5 DNS events
    fetch_command = 'wevtutil qe "Microsoft-Windows-DNS-Client/Operational" /c:50 /f:text'
    fetch_result = subprocess.run(fetch_command, shell=True, capture_output=True, text=True, startupinfo=startupinfo)
    
    logs = fetch_result.stdout.strip().split("\n\n")
    parsed_logs = []
    
    for log in logs:
        if "Event ID:" in log:
            lines = log.split("\n")
            event_id = next((line.split(":")[1].strip() for line in lines if "Event ID" in line), "Unknown")
            timestamp = next((line.split(":")[1].strip() for line in lines if "TimeCreated" in line), "Unknown")
            queried_domain = next((line.split(":")[1].strip() for line in lines if "QueryName" in line), "Unknown")
            response_ip = next((line.split(":")[1].strip() for line in lines if "Address" in line), "Unknown")
            query_status = "Success" if "Status: 0" in log else "Failure"

            parsed_logs.append(f"""
🌐 **Domain Queried:** {queried_domain}
    **Timestamp:** {timestamp}
    **Response IP:** {response_ip}
    **Query Status:** {query_status}
            """.strip())
    
    return "\n\n".join(parsed_logs) if parsed_logs else "No DNS Logs Found."





