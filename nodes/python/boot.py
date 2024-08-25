try:
    import machine
    import network
    import auth
    from ota import OTAUpdater
    import time
    
    try:
        machine.freq(80000000)
    except:
        pass
    try:
        rtc = machine.RTC()
        rtc.datetime([2000,1,1,5,0,0,0,0])
    except:
        pass
    
    print('...boot...')
    startBootTime1 = time.time()

    errorTime = 60
    calc_interval = 15000

    sta_if = network.WLAN(network.STA_IF)
    try:
        sta_if.active(True)
        #sta_if.ifconfig((auth.device_IP, auth.mask, auth.gateway, auth.gateway))
        print('Wifi activated')
        sta_if.connect(auth.SSID_Name, auth.SSID_Pass)
    except:
        pass
    nextcalc = round(time.time_ns() / 1000000) + calc_interval
    while not sta_if.isconnected():
        timer = round(time.time_ns() / 1000000)
        if timer >= nextcalc:
            print('Cant connect to WiFi, error')
            print('Error sleep')
            machine.deepsleep(errorTime * 1000)
            machine.reset()

    print('Connection successful')
    print(sta_if.ifconfig())
  
    firmware_url = "https://raw.githubusercontent.com/ValasekMaros/DP/main/nodes/python/"

    ota_updater = OTAUpdater(firmware_url, "main.py")

    ota_updater.download_and_install_update_if_available()

    try:
        sta_if.disconnect()
        sta_if.active(False)
    except:
        pass
    endBootTime1 = time.time()
    bootTime = endBootTime1-startBootTime1
    print('Boot Time: ', bootTime)
    print('...boot...')
except Exception as e:
    print('Error(Exception)...')
    print(e)
    machine.reset()