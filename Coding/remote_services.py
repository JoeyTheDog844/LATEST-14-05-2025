import subprocess

# ✅ Services to check
REMOTE_SERVICES = {
    "Bluetooth Support Service": "bthserv",
    "Geolocation Service": "lfsvc",
    "Plug and Play": "PlugPlay",
    "HV Host Service": "vmickvpexchange",
    "Remote Desktop Services": "TermService",
    "Remote Procedure Call (RPC)": "RpcSs",
    "Routing and Remote Access": "RemoteAccess",
    "Wi-Fi Direct Services": "WFDSConMgrSvc",
    "Xbox Game Monitoring": "xbgm",
    "Default Share Status": "LanmanServer"
}

def get_service_status(service_name):
    """ ✅ Checks if a Windows service is running or stopped. """
    try:
        command = f'sc query "{service_name}"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        # ✅ Extract service state from output
        if "RUNNING" in result.stdout:
            return "Running"
        elif "STOPPED" in result.stdout:
            return "Stopped"
        else:
            return "Unknown"
    except Exception as e:
        return f"Error: {e}"

def check_remote_services():
    """ ✅ Fetch status of all remote & networking services. """
    service_statuses = {}
    
    for service, service_code in REMOTE_SERVICES.items():
        service_statuses[service] = get_service_status(service_code)

    return service_statuses  # ✅ Returns a dictionary
