try:
    import machine
    import network
    import auth
    from ota import OTAUpdater
    import time
    
    machine.freq(80000000)
    
    rtc = machine.RTC()
    rtc.datetime([2000,1,1,5,0,0,0,0])
    
    print('...boot...')
    startBootTime1 = time.time()

    errorTime = 300
    calc_interval = 15000

    sta_if = network.WLAN(network.STA_IF)

    sta_if.active(True)
    print('Wifi activated')
    sta_if.connect(auth.SSID_Name, auth.SSID_Pass)

    nextcalc = round(time.time_ns() / 1000000) + calc_interval
    while not sta_if.isconnected():
        timer = round(time.time_ns() / 1000000)
        if timer >= nextcalc:
            print('Cant connect to WiFi, error')
            endTime = time.time()
            cycleTime = endTime - startBootTime1
            print('Cycle time:', cycleTime)
            print('Error sleep')
            machine.deepsleep((errorTime - cycleTime) * 1000)
            machine.reset()

    print('Connection successful')
    print(sta_if.ifconfig())
  
    firmware_url = "https://raw.githubusercontent.com/ValasekMaros/DP/main/nodes/python/"

    ota_updater = OTAUpdater(firmware_url, "main.py")

    ota_updater.download_and_install_update_if_available()

    sta_if.disconnect()
    sta_if.active(False)

    machine.freq(20000000)
    endBootTime1 = time.time()
    bootTime = endBootTime1-startBootTime1
    print('Boot Time: ', bootTime)
    print('...boot...')
except Exception as E:
    print('Error(Exception)...')
    print(E)
    machine.reset()
except OSError as e:
    print('Error(OSError)...')
    print(e)
    machine.reset()
