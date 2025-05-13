import winreg

def get_installed_programs():
    """
    Retrieves a list of installed programs from the Windows Registry.
    """
    program_list = []

    # Registry paths for 64-bit and 32-bit programs
    registry_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]

    # Open both registry hives (Local Machine & Current User)
    hives = [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]

    for hive in hives:
        for path in registry_paths:
            try:
                reg_key = winreg.OpenKey(hive, path)
                for i in range(0, winreg.QueryInfoKey(reg_key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(reg_key, i)
                        subkey = winreg.OpenKey(reg_key, subkey_name)

                        # Retrieve DisplayName if available
                        program_name, _ = winreg.QueryValueEx(subkey, "DisplayName")

                        # Retrieve Version if available
                        try:
                            version, _ = winreg.QueryValueEx(subkey, "DisplayVersion")
                        except FileNotFoundError:
                            version = "Unknown Version"

                        program_list.append((program_name, version))
                        winreg.CloseKey(subkey)
                    except FileNotFoundError:
                        continue
                winreg.CloseKey(reg_key)
            except FileNotFoundError:
                continue

    return sorted(program_list, key=lambda x: x[0])  # Sort alphabetically
