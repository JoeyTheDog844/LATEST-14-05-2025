import os
import ctypes
import shutil
import subprocess

# ✅ Suppress black CMD windows
startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

def clear_recycle_bin():
    """Clears the Windows Recycle Bin."""
    try:
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0x00000001)  # 0x00000001: Don't show confirmation
        return "✅ Recycle Bin cleared successfully."
    except Exception as e:
        return f"❌ Error clearing Recycle Bin:\n{e}"

def clear_temp_files():
    """Clears temporary files from the user's temp directory."""
    temp_path = os.environ.get("TEMP", "C:\\Windows\\Temp")
    deleted = 0
    try:
        for item in os.listdir(temp_path):
            item_path = os.path.join(temp_path, item)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.remove(item_path)
                    deleted += 1
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path, ignore_errors=True)
                    deleted += 1
            except Exception:
                continue
        return f"✅ Temporary files cleared. Items removed: {deleted}"
    except Exception as e:
        return f"❌ Error clearing temporary files:\n{e}"

def clear_dns_cache():
    """Flushes the DNS resolver cache."""
    try:
        subprocess.run("ipconfig /flushdns", shell=True, check=True, startupinfo=startupinfo)
        return "✅ DNS cache cleared."
    except Exception as e:
        return f"❌ Error clearing DNS cache:\n{e}"

def clear_windows_update_cache():
    """Deletes cached update files in SoftwareDistribution."""
    update_cache_path = r"C:\Windows\SoftwareDistribution\Download"
    try:
        if os.path.exists(update_cache_path):
            shutil.rmtree(update_cache_path, ignore_errors=True)
        os.makedirs(update_cache_path, exist_ok=True)  # Always ensure the folder exists
        return "✅ Windows Update cache cleared."
    except Exception as e:
        return f"❌ Error clearing Windows Update cache:\n{e}"

def clear_all_caches():
    """Runs all cleanup operations and returns a combined message."""
    messages = [
        clear_recycle_bin(),
        clear_temp_files(),
        clear_dns_cache(),
        clear_windows_update_cache()
    ]
    return "\n".join(messages)
