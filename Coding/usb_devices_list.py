import winreg

def get_usb_history():
    usb_devices = []
    reg_path = r'SYSTEM\\CurrentControlSet\\Enum\\USBSTOR'

    try:
        reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
        
        for i in range(winreg.QueryInfoKey(reg_key)[0]):
            device_key_name = winreg.EnumKey(reg_key, i)
            device_key = winreg.OpenKey(reg_key, device_key_name)
            
            for j in range(winreg.QueryInfoKey(device_key)[0]):
                instance_key_name = winreg.EnumKey(device_key, j)
                instance_key = winreg.OpenKey(device_key, instance_key_name)
                
                device_info = {
                    'Device': device_key_name,
                    'Serial': instance_key_name,
                    'FriendlyName': None
                }

                try:
                    friendly_name, _ = winreg.QueryValueEx(instance_key, 'FriendlyName')
                    device_info['FriendlyName'] = friendly_name
                except FileNotFoundError:
                    device_info['FriendlyName'] = 'N/A'
                
                usb_devices.append(device_info)
                winreg.CloseKey(instance_key)

            winreg.CloseKey(device_key)

        winreg.CloseKey(reg_key)

    except Exception as e:
        print(f"Error accessing registry: {e}")

    return usb_devices


if __name__ == '__main__':
    devices = get_usb_history()

    if devices:
        for device in devices:
            print(f"Device: {device['Device']}, Serial: {device['Serial']}, Name: {device['FriendlyName']}")
    else:
        print("No USB storage devices found.")
