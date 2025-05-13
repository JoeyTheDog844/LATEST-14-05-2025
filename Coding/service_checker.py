import subprocess

# ✅ List of critical services to check
CRITICAL_SERVICES = {
    "DNS Client": "Dnscache",
    "DNS Server": "DNS",
    "Geolocation Service": "lfsvc",
    "Distributed Transaction Coordinator": "MSDTC",
    "Plug and Play": "PlugPlay",
    "Remote Access Auto Connection Manager": "RasAuto",
    "Remote Access Connection Manager": "RasMan",
    "Routing and Remote Access": "RemoteAccess",
    "Remote Registry": "RemoteRegistry",
    "RPC Endpoint Mapper": "RpcEptMapper",
    "Remote Procedure Call (RPC) Locator": "RpcLocator",
    "Remote Procedure Call (RPC)": "RpcSs",
    "Remote Desktop Configuration": "SessionEnv",
    "Microsoft Storage Spaces SMP": "smphost",
    "OpenSSH Authentication Agent": "sshd",
    "Remote Desktop Services": "TermService",
    "Problem Reports Control Panel Support": "wercplsupport",
    "Telnet Client": "TlntSvr"
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

def check_critical_services():
    """ ✅ Fetch status of all critical services. """
    service_statuses = {}
    
    for service, service_code in CRITICAL_SERVICES.items():
        service_statuses[service] = get_service_status(service_code)

    return service_statuses  # ✅ Returns a dictionary
