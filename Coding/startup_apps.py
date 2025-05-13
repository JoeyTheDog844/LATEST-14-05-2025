import winreg
import subprocess

def get_startup_programs():
    """
    Retrieves a list of startup applications from the Windows Registry and Task Scheduler.
    """
    startup_programs = []

    # Registry paths for startup applications
    registry_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run")
    ]

    # Extract startup programs from Windows Registry
    for hive, path in registry_paths:
        try:
            reg_key = winreg.OpenKey(hive, path)
            for i in range(winreg.QueryInfoKey(reg_key)[1]):  # Number of values in the key
                try:
                    name, command, _ = winreg.EnumValue(reg_key, i)
                    startup_programs.append((name, command, "Registry"))
                except FileNotFoundError:
                    continue
            winreg.CloseKey(reg_key)
        except FileNotFoundError:
            continue

    # Extract startup programs from Task Scheduler
    try:
        result = subprocess.run(["schtasks", "/query", "/fo", "LIST", "/v"], capture_output=True, text=True)
        lines = result.stdout.split("\n")
        task_name, task_path = None, None

        for line in lines:
            if "TaskName:" in line:
                task_name = line.split("TaskName:")[1].strip()
            elif "Task To Run:" in line:
                task_path = line.split("Task To Run:")[1].strip()
            elif "Status:" in line and task_name and task_path:
                startup_programs.append((task_name, task_path, "Task Scheduler"))
                task_name, task_path = None, None  # Reset for the next task

    except Exception as e:
        print(f"Error retrieving scheduled tasks: {e}")

    return sorted(startup_programs, key=lambda x: x[0])  # Sort alphabetically
