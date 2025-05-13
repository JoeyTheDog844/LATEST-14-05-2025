import subprocess

def get_current_policy():
    """ ✅ Retrieve and organize the current Password, Lockout Policy, and Inactivity Timeout """
    try:
        result = subprocess.run(["net", "accounts"], capture_output=True, text=True)
        lines = result.stdout.strip().splitlines()

        password_policy = {}
        lockout_policy = {}

        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()

                # Categorize into password or lockout policies
                if any(word in key.lower() for word in ["password", "minpw", "maxpw"]):
                    password_policy[key] = value
                elif any(word in key.lower() for word in ["lockout", "bad logon"]):
                    lockout_policy[key] = value

        # ✅ Get Machine Inactivity Limit from Registry
        try:
            reg_result = subprocess.run([
                "reg", "query", "HKCU\\Control Panel\\Desktop", "/v", "ScreenSaveTimeOut"
            ], capture_output=True, text=True)
            reg_output = reg_result.stdout.strip()
            timeout_seconds = None

            if "ScreenSaveTimeOut" in reg_output:
                parts = reg_output.split()
                timeout_seconds = int(parts[-1])

            if timeout_seconds is not None:
                lockout_policy["Machine Inactivity Limit (minutes)"] = str(timeout_seconds // 60)

        except Exception as reg_error:
            lockout_policy["Machine Inactivity Limit (minutes)"] = f"Error retrieving: {reg_error}"

        return {"Password Policy": password_policy, "Lockout Policy": lockout_policy}

    except Exception as e:
        return {"Error": f"Error retrieving policy: {e}"}

def set_password_policy():
    """ ✅ Set Password Policy """
    try:
        subprocess.run(["net", "accounts", "/MAXPWAGE:45"], capture_output=True, text=True)
        subprocess.run(["net", "accounts", "/MINPWAGE:0"], capture_output=True, text=True)
        subprocess.run(["net", "accounts", "/MINPWLEN:10"], capture_output=True, text=True)

        subprocess.run(["reg", "add", "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Netlogon\\Parameters", 
                        "/v", "PasswordComplexity", "/t", "REG_DWORD", "/d", "1", "/f"], capture_output=True, text=True)

        return "✅ Password policy successfully updated."

    except Exception as e:
        return f"Error updating password policy: {e}"


def set_lockout_policy():
    """ ✅ Set Lockout Policy """
    try:
        subprocess.run(["net", "accounts", "/lockoutthreshold:5"], capture_output=True, text=True)
        subprocess.run(["net", "accounts", "/lockoutduration:30"], capture_output=True, text=True)
        subprocess.run(["net", "accounts", "/lockoutwindow:15"], capture_output=True, text=True)

        # Set Machine Inactivity Limit (Screensaver Timeout in seconds)
        subprocess.run([
            "reg", "add", "HKCU\\Control Panel\\Desktop",
            "/v", "ScreenSaveTimeOut", "/t", "REG_SZ", "/d", "300", "/f"
        ], capture_output=True, text=True)

        return "✅ Lockout policy and machine inactivity limit successfully updated."

    except Exception as e:
        return f"Error updating lockout policy: {e}"
