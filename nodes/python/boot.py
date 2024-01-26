import network
import auth
from ota import OTAUpdater

print('...boot...')
sta_if = network.WLAN(network.STA_IF)

sta_if.active(True)
sta_if.connect(auth.SSID_Name, auth.SSID_Pass)

while not sta_if.isconnected():
    pass
print('Connection successful')
print(sta_if.ifconfig())
        
firmware_url = "https://raw.githubusercontent.com/ValasekMaros/DP/main/nodes/python/"

ota_updater = OTAUpdater(firmware_url, "main.py")

ota_updater.download_and_install_update_if_available()
print('...boot...')