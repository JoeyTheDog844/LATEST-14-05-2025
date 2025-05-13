import subprocess
import time

# ✅ List of critical services
CRITICAL_SERVICES = {
    "Geolocation Service": "lfsvc",
    "Remote Access Auto Connection Manager": "RasAuto",
    "Remote Access Connection Manager": "RasMan",
    "Routing and Remote Access": "RemoteAccess",
    "Remote Registry": "RemoteRegistry",
    "Remote Desktop Services": "TermService",
    "Remote Desktop Configuration": "SessionEnv",
    "OpenSSH Authentication Agent": "sshd",
    "Problem Reports Control Panel Support": "wercplsupport",
    "Telnet Client": "TlntSvr",
    "Plug and Play": "PlugPlay",
    "AutoPlay": "AutoPlay", # if anyone is confused lol, this is disabling both NoDriveTypeAutoRun = 255 AND DisableAutoplay = 1
    "Wi-Fi AutoConfig Service": "WlanSvc"
}

def get_service_status(service_name):
    try:
        if service_name == "AutoPlay":
            # Special case for AutoPlay: check registry
            result = subprocess.run([
                "reg", "query", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer", "/v", "NoDriveTypeAutoRun"
            ], capture_output=True, text=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)

            if "0xFF" in result.stdout or "0xff" in result.stdout:
                return "Disabled"  # AutoPlay blocked = Disabled ✅
            else:
                return "Running"   # AutoPlay active = Running ✅

        # Normal Windows service checking
        result = subprocess.run(
            ["sc", "qc", service_name],
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        if "DISABLED" in result.stdout:
            return "Disabled"

        result = subprocess.run(
            ["sc", "query", service_name],
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        if "RUNNING" in result.stdout:
            return "Running"
        elif "STOPPED" in result.stdout:
            return "Stopped"
        else:
            return "Unknown"
    except Exception as e:
        return f"Error: {e}"

def check_all_services():
    """ ✅ Fetch all service statuses. """
    statuses = {}
    for service, service_code in CRITICAL_SERVICES.items():
        statuses[service] = get_service_status(service_code)
    return statuses

def start_all_services():
    """ ✅ Enable and start all stopped/disabled services. """
    started_services = []
    failed_services = []

    for service_name, service_code in CRITICAL_SERVICES.items():
        status = get_service_status(service_code)

        if status in ["Stopped", "Disabled"]:
            try:
                # Step 1: Set to manual (or auto if you prefer)
                config_result = subprocess.run(
                    ["sc", "config", service_code, "start=", "demand"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )

                if "SUCCESS" not in config_result.stdout:
                    failed_services.append(f"{service_name} (couldn't configure)")
                    continue

                # Step 2: Try to start
                subprocess.run(
                    ["sc", "start", service_code],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )

                # Step 3: Wait and check status
                for _ in range(5):
                    time.sleep(1)
                    if get_service_status(service_code) == "Running":
                        started_services.append(service_name)
                        break
                else:
                    failed_services.append(f"{service_name} (couldn't confirm start)")

            except Exception as e:
                failed_services.append(f"{service_name} (error: {e})")

    return started_services, failed_services

def disable_all_services():
    """ ✅ Disable all critical services including AutoPlay. """
    disabled_services = []
    failed_services = []

    for service_name, service_code in CRITICAL_SERVICES.items():
        try:
            if service_code == "AutoPlay":
                # Step 1: Disable AutoRun for all drive types
                subprocess.run([
                    "reg", "add", r"HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
                    "/v", "NoDriveTypeAutoRun", "/t", "REG_DWORD", "/d", "255", "/f"
                ], capture_output=True, text=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)

                # Step 2: Disable AutoPlay handler (disable the checkbox)
                result = subprocess.run([
                    "reg", "add", r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\AutoplayHandlers",
                    "/v", "DisableAutoplay", "/t", "REG_DWORD", "/d", "1", "/f"
                ], capture_output=True, text=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)

                if "completed successfully" in result.stdout.lower() or result.returncode == 0:
                    disabled_services.append(service_name)
                else:
                    failed_services.append(service_name)
                continue

            # Disable standard Windows service
            result = subprocess.run(
                ["sc", "config", service_code, "start=", "disabled"],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if "SUCCESS" in result.stdout:
                disabled_services.append(service_name)
            else:
                failed_services.append(service_name)
        except Exception:
            failed_services.append(service_name)

    return disabled_services, failed_services


