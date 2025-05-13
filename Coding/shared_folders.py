import subprocess

def get_shared_folders():
    """
    Retrieves a list of shared folders on the system using PowerShell.
    """
    try:
        # PowerShell command to list shared folders
        command = 'powershell "Get-WmiObject -Class Win32_Share | Select-Object Name, Path, Description"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        # Split lines and parse output
        lines = result.stdout.strip().split("\n")
        shared_folders = []

        # Extracting only valid rows
        for line in lines[3:]:  # Skip headers
            parts = line.strip().split(None, 2)  # Split into Name, Path, Description
            if len(parts) == 3:
                shared_folders.append({
                    "Name": parts[0], 
                    "Path": parts[1], 
                    "Description": parts[2]
                })
            elif len(parts) == 2:  # Some entries may not have a description
                shared_folders.append({
                    "Name": parts[0], 
                    "Path": parts[1], 
                    "Description": "No description available"
                })

        return shared_folders

    except Exception as e:
        print(f"Error retrieving shared folders: {e}")
        return []
