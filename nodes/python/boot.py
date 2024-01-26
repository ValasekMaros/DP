from ota import OTAUpdater
from auth import SSID_Name, SSID_Pass

firmware_url = "https://raw.githubusercontent.com/ValasekMaros/DP/main/nodes/python/"

ota_updater = OTAUpdater(SSID_Name, SSID_Pass, firmware_url, "boot.py")
ota_updater = OTAUpdater(SSID_Name, SSID_Pass, firmware_url, "main.py")

ota_updater.download_and_install_update_if_available()
