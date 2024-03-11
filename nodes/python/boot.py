import machine
import network
import auth
from ota import OTAUpdater
import time

machine.freq(80000000)

print('...boot...')
zaciatok = time.time()

sta_if = network.WLAN(network.STA_IF)

sta_if.active(True)
print('Wifi activated')
sta_if.connect(auth.SSID_Name, auth.SSID_Pass)

while not sta_if.isconnected():
    pass
print('Connection successful')
print(sta_if.ifconfig())
        
firmware_url = "https://raw.githubusercontent.com/ValasekMaros/DP/main/nodes/python/stable/"

ota_updater = OTAUpdater(firmware_url, "main.py")

ota_updater.download_and_install_update_if_available()

sta_if.disconnect()
sta_if.active(False)

print('...boot...')
