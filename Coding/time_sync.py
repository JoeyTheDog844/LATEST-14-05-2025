import subprocess

def set_time_service_automatic():
    commands = [
        'sc config W32Time start= auto',
        'net start W32Time'
    ]
    try:
        for cmd in commands:
            subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        return "Time service set to Automatic and started successfully."
    except subprocess.CalledProcessError as e:
        return f"Failed to set time service: {e.stderr}"

def set_time_server(server="time.nist.gov"):
    try:
        subprocess.run(f'w32tm /config /manualpeerlist:"{server}" /syncfromflags:manual /update', shell=True, check=True, capture_output=True, text=True)
        subprocess.run('w32tm /resync', shell=True, check=True, capture_output=True, text=True)
        return f"Time server set to {server} and synced successfully."
    except subprocess.CalledProcessError as e:
        return f"Failed to set time server: {e.stderr}"

def get_time_service_status():
    try:
        result = subprocess.check_output('sc query W32Time', shell=True, text=True)
        return "RUNNING" if "RUNNING" in result else "STOPPED"
    except subprocess.CalledProcessError:
        return "UNKNOWN"
