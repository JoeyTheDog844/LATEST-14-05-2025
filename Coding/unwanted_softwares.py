import winreg

# ✅ Expanded list of unwanted software
UNWANTED_SOFTWARE = [
    # Remote Access
    "TeamViewer", "AnyDesk", "UltraVNC", "LogMeIn", "RemotePC", "Ammyy Admin", "ShowMyPC", "Chrome Remote Desktop",
    "TightVNC", "ConnectWise Control", "Zoho Assist", "RustDesk", "NoMachine",

    # Registry Cleaners
    "CCleaner", "Advanced SystemCare", "Registry Mechanic", "Wise Registry Cleaner", "Glary Utilities",
    "Auslogics Registry Cleaner", "IObit Advanced SystemCare", "WinOptimizer", "RegCure Pro",
    "PC Speed Maximizer", "WinThruster", "OneSafe PC Cleaner",

    # Virtual Machines
    "VMware", "VirtualBox", "Hyper-V", "Sandboxie", "Parallels Desktop", "QEMU", "Shadow Defender", "Deep Freeze",

    # Torrent Clients
    "uTorrent", "BitTorrent", "qBittorrent", "Deluge", "Vuze", "FrostWire", "Transmission", "eMule",
    "Popcorn Time", "Pirate Bay Client", "LimeWire",

    # Hacking & Cracking Tools
    "Cain & Abel", "Wireshark", "Metasploit", "John the Ripper", "Aircrack-ng", "Nmap", "Hydra", "Mimikatz",
    "Maltego", "Brutus", "Hashcat", "NetStumbler", "ZMap",

    # Keyloggers
    "Refog Keylogger", "Elite Keylogger", "Spyrix Keylogger", "Ardamax Keylogger", "Best Free Keylogger",
    "PC Pandora", "REFOG Personal Monitor", "KidLogger",

    # VPNs
    "Tor", "Psiphon", "Freegate", "Ultrasurf", "Hotspot Shield", "NordVPN", "ExpressVPN", "ProtonVPN",
    "CyberGhost", "TunnelBear", "Windscribe", "Hidemyass VPN",

    # Cloud Storage
    "Dropbox", "Google Drive", "OneDrive", "Box", "Mega", "MediaFire", "Sync.com", "pCloud",
    "WeTransfer", "Send Anywhere",

    # Social Media Apps
    "Facebook Messenger", "WhatsApp Desktop", "Telegram Desktop", "TikTok", "Instagram", "Snapchat",
    "Reddit Desktop", "Discord", "Skype"
]

def get_installed_software():
    """ Retrieves a list of installed software from the Windows registry. """
    software_list = []

    registry_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]

    for reg_path in registry_paths:
        try:
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
            for i in range(winreg.QueryInfoKey(reg_key)[0]):
                try:
                    sub_key_name = winreg.EnumKey(reg_key, i)
                    sub_key = winreg.OpenKey(reg_key, sub_key_name)

                    software_name, _ = winreg.QueryValueEx(sub_key, "DisplayName")
                    software_list.append(software_name)

                    winreg.CloseKey(sub_key)
                except (FileNotFoundError, OSError):
                    continue

            winreg.CloseKey(reg_key)

        except FileNotFoundError:
            continue

    return software_list

def detect_unwanted_software():
    """ ✅ Returns a list of unwanted software instead of printing it. """
    installed_software = get_installed_software()

    # ✅ Ensure function always returns a list
    detected_unwanted = [
        s for s in installed_software if any(u.lower() in s.lower() for u in UNWANTED_SOFTWARE)
    ] if installed_software else []

    return detected_unwanted  # ✅ FIX: Returning a list instead of printing
