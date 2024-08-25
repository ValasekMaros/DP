try:
    import machine
    import time
    import os
    import ubinascii
    import gc
    from umqttsimple import MQTTClient
    #from bmp085 import BMP180
    import BME280
    import dht
    import json
    import ina219
    import auth
    import esp32
    gc.collect()
    
    try:
        machine.freq(20000000)
    except:
        pass
    
    print('...main...')
    startMainTime1 = time.time()
    importTime = startMainTime1 - endBootTime1
    print('Import time: ', importTime)
    
    rtcData = {
        "presses": None
    }
    
    message = {
        "espID": "00",
        #"bmp_temp": None,
        #"bmp_press": None,
        "bme_temp": None,
        "bme_hum": None,
        "bme_press": None,
        "dht_temp": None,
        "dht_hum": None,
        "rain_tips": None,
        "rain_mm": None,
        "windSpeed_tips": None,
        "windSpeed_1Hz": None,
        "windSpeed_kmh": None,
        "windSpeed_ms": None,
        "windDir_deg": None,
        "windDir_name": None,
        "windDir_ADC": None,
        "battery_voltage": None,
        "status_wifimqtt": "OK",
        "status_ina219": "OK",
        "status_bme280": "OK",
        "status_dht22": "OK"
    }
    # Sleep time(in seconds) for sleep after error and sleep after successful message send, and for warming sensors
    #warmSensor = 5
    errorTime = 60
    sendTime = 60
    correctionTime = 3
    # MQTT ID for connect
    #mqtt_client = ubinascii.hexlify(machine.unique_id())
    mqtt_client = "MeteoStation00"
    # MQTT topic for publishing
    topic_pub = 'project'

    calc_interval = 15000
    rain_debounce_time = 80
    wind_debounce_time = 80
    windDirCycle = 1
    windSpeedTrigger = 0
    windDir_deg = 0
    windDir_name = None
    rain_sleep = False
    rtcDataPresses = 0
    spin = 0

    rain_lastMicros = 0
    wind_lastMicros = 0

    '''
    # Values before rotation for our use (90 degree rotation)
    windDirDeg = [0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5, 180, 202.5, 225, 247.5, 270, 292.5, 315, 337.5]
    windDirName = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    '''
    windDirMin = [2783, 1336, 1566, 167, 200, 104, 532, 320, 903, 746, 2371, 2045, 3723, 3224, 3278, 2579]
    windDirMax = [3223, 1565, 1885, 202, 245, 128, 650, 392, 1103, 901, 2578, 2370, 4334, 3277, 3722, 2782]
    windDirDeg = [90, 112.5, 135, 157.5, 180, 202.5, 225, 247.5, 270, 292.5, 315, 337.5, 360, 22.5, 45, 67.5]
    windDirName = ['E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW', 'N', 'NNE', 'NE', 'ENE']
    
    # --------------------------------------------------------------------------------------------
    # Pins
    try:
        i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21), freq=10000)
    except:
        pass
    #pinRain_power = machine.Pin(5, machine.Pin.OUT)
    #pinWindSpeed_power = machine.Pin(17, machine.Pin.OUT)
    #pinWindDir_power = machine.Pin(16, machine.Pin.OUT)
    pinDHT = machine.Pin(23)
    pinRain = machine.Pin(34, machine.Pin.IN, machine.Pin.PULL_DOWN)
    pinWindSpeed = machine.Pin(15, machine.Pin.IN)
    pinWindDir = machine.ADC(machine.Pin(36))
    pinWindDir.atten(machine.ADC.ATTN_11DB)

    #pinBMP_power = machine.Pin(19, machine.Pin.OUT)
    pinBME_power = machine.Pin(19, machine.Pin.OUT)
    pinDHT_power = machine.Pin(18, machine.Pin.OUT)

    # --------------------------------------------------------------------------------------------
    # Functions
    def countingRain(pin):
        pinRain.irq(None)
        print('')
        print('Rain Interupt...')
        print('')
        global rain_lastMicros
        global rain_debounce_time
        global rain_sleep
        global rtcDataPresses
        global spin
        if round(time.time_ns() / 1000) - rain_lastMicros >= rain_debounce_time * 1000:
            rtcDataPresses += 1
            rain_lastMicros = round(time.time_ns() / 1000)
        print('rain_sleep: ', rain_sleep)
        if rain_sleep:
            try:
                rtcData["presses"] = rtcDataPresses
                rtc.memory(json.dumps(rtcData))
            except:
                pass
            else:
                print('rtcData Saved')
            time.sleep(0.25)
            sleepTime = sendTime - time.time()
            pinRain.irq(trigger=machine.Pin.IRQ_FALLING, handler=countingRain)
            esp32.wake_on_ext0(pin = pinRain, level = esp32.WAKEUP_ALL_LOW)
            machine.lightsleep(sleepTime * 1000)
            while True:
                spin += 1
                print('spin: ', spin)
                if spin > 15:
                    spin = 0
                    break
        pinRain.irq(trigger=machine.Pin.IRQ_FALLING, handler=countingRain)
        return

    def countingWind(pin):
        print('Interupt...')
        global wind_lastMicros
        global wind_debounce_time
        global windSpeedTrigger
        global timer
        global nextcalc
        if round(time.time_ns() / 1000) - wind_lastMicros >= wind_debounce_time * 1000:
            windSpeedTrigger += 1
            wind_lastMicros = round(time.time_ns() / 1000)
        if timer >= nextcalc:
            pinWindSpeed.irq(None)
            return
        return
    # --------------------------------------------------------------------------------------------
    
    try:
        readData = json.loads(rtc.memory())
        rtcDataPresses = readData["presses"]
        print('rtcDataPresses: ', rtcDataPresses)
    except:
        pass
    
    pinRain.irq(trigger=machine.Pin.IRQ_FALLING, handler=countingRain)
    # Powering BMP and DHT
    #pinBMP_power.on()
    pinBME_power.on()
    pinDHT_power.on()
    #pinWindDir_power.on()
    #pinRain_power.on()
    #pinWindSpeed_power.on()
    time.sleep(1)

    try:
        sensor = ina219.INA219(i2c, addr=0x40)
        sensor.set_calibration_16V_400mA()
    except OSError as e:
        print('Cant connect to INA219, error')
        print(e)
        message['status_ina219'] = "Error"
        message['battery_voltage'] = None
        '''
        endMainTime1 = time.time()
        cycleTime = (endMainTime1 - startMainTime1) + bootTime + importTime
        print('Cycle time:', cycleTime)
        print('Error sleep')
        machine.deepsleep((errorTime - cycleTime) * 1000)
        machine.reset()
        '''
    else:
        print('Connected to INA219')
        
        batteryVoltage = sensor.bus_voltage
        print("Bus voltage   / V: %8.3f" % (batteryVoltage))
        message['battery_voltage'] = batteryVoltage

    # --------------------------------------------------------------------------------------------
    # Need to add try: for exception
    try:
        #bmp180 = BMP180(I2C)
        #bmp180.oversample = 3
        #bmp180.sealevel = 1013
        bme280 = BME280.BME280(mode=5, address=0x77, i2c=i2c)
        #bmp180.makegauge()
    except OSError as e:
        print('Cant connect to BME280, error')
        print(e)
        message['status_bme280'] = "Error"
        message['bme_temp'] = None
        message['bme_hum'] = None
        message['bme_press'] = None
        
        '''
        endMainTime1 = time.time()
        cycleTime = (endMainTime1 - startMainTime1) + bootTime + importTime
        print('Cycle time:', cycleTime)
        print('Error sleep')
        machine.deepsleep((errorTime - cycleTime) * 1000)
        machine.reset()
        '''
    else:
        print('Connected to BME280')
        
        temp_bme280 = bme280.temperature
        time.sleep(1)
        hum_bme280 = bme280.humidity
        time.sleep(1)
        press_bme280 = bme280.pressure
        print('BME:', temp_bme280, hum_bme280, press_bme280)
        message['bme_temp'] = temp_bme280
        message['bme_hum'] = hum_bme280
        message['bme_press'] = press_bme280
        
    try:
        dht22 = dht.DHT22(pinDHT)
        dht22.measure()
    except OSError as e:
        print('Cant connect to DHT22, error')
        print(e)
        message['status_dht22'] = "Error"
        message['dht_temp'] = None
        message['dht_hum'] = None
        '''
        endMainTime1 = time.time()
        cycleTime = (endMainTime1 - startMainTime1) + bootTime
        print('Cycle time:', cycleTime)
        print('Error sleep')
        machine.deepsleep((errorTime - cycleTime) * 1000)
        machine.reset()
        '''
    else:
        print('Connected to DHT22')

        dht22.measure()
        temp_dht22 = dht22.temperature()
        hum_dht22 = dht22.humidity()
        print('DHT', temp_dht22, hum_dht22)
        message['dht_temp'] = temp_dht22
        message['dht_hum'] = hum_dht22

    # --------------------------------------------------------------------------------------------
    #bmp180.makegauge()
    #temp_bmp180 = bmp180.temperature
    #press_bmp180 = bmp180.pressure
    #altitude_bmp180 = bmp180.altitude
    #print('BMP:', temp_bmp180, press_bmp180, altitude_bmp180)
    #message['bmp_temp'] = temp_bmp180
    #message['bmp_press'] = press_bmp180

    #pinBMP_power.off()
    pinBME_power.off()
    pinDHT_power.off()
    #pinWindDir_power.off()
    #pinRain_power.off()
    #pinWindSpeed_power.off()
    
    nextcalc = round(time.time_ns() / 1000000) + calc_interval
    windSpeedStart = 1
    print('Start of Wind Speed Measurement')
    while True:
        if windSpeedStart:
            pinWindSpeed.irq(trigger=machine.Pin.IRQ_FALLING, handler=countingWind)
            windSpeedStart = 0
        timer = round(time.time_ns() / 1000000)
        #time.sleep(0.1)
        if timer >= nextcalc:
            pinWindSpeed.irq(None)
            print('Wind speed, measure interval: ',(timer - nextcalc) + calc_interval)
            print('Total Tips(Wind Speed):', windSpeedTrigger)
            try:
                windSpeed_1Hz = windSpeedTrigger / calc_interval * 1000
                message['windSpeed_tips'] = windSpeedTrigger
                message['windSpeed_1Hz'] = windSpeed_1Hz
                message['windSpeed_kmh'] = windSpeed_1Hz * 2.4
                message['windSpeed_ms'] = (windSpeed_1Hz * 2.4) / 3.6
            except:
                pass
            break
    pinWindSpeed.irq(None)
    print('End of Wind Speed Measurement')
    
    print('Start of Wind Direction Measurement')
    try:
        pinWindDir_value = 0
        for i in range(windDirCycle):
            pinWindDir_value += pinWindDir.read()
        pinWindDir_value /= windDirCycle
        message['windDir_ADC'] = pinWindDir_value
        for i in range(len(windDirDeg)):
            if pinWindDir_value >= windDirMin[i] and pinWindDir_value <= windDirMax[i]:
                windDir_deg = windDirDeg[i]
                windDir_name = windDirName[i]
                message['windDir_deg'] = windDir_deg
                message['windDir_name'] = windDir_name
                break
        else:
            message['windDir_deg'] = None
            message['windDir_name'] = ''
        print('Wind Direction Deg:', windDir_deg)
        print('Wind Direction Name:', windDir_name)
        #pinWindDir_power.off()
    except:
        message['windDir_deg'] = None
        message['windDir_name'] = ''
    print('End of Wind Direction Measurement')
    
    try:
        machine.freq(80000000)
    except:
        machine.reset()
        
    try:
        sta_if.active(True)
        sta_if.ifconfig((auth.device_IP, auth.mask, auth.gateway, auth.gateway))
        print('Wifi activated')
        sta_if.connect(auth.SSID_Name, auth.SSID_Pass)
    except:
        machine.reset()
        
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

    if sta_if.isconnected():
        try:
            mqtt = MQTTClient(mqtt_client, auth.mqtt_host, auth.mqtt_port, auth.mqtt_user, auth.mqtt_pass)
            mqtt.connect()
        except OSError as e:
            print('Problem with MQTT Connect, error')
            print(e)
            print('Error sleep')
            machine.deepsleep(errorTime * 1000)
            machine.reset()
        else:
            try:
                pinRain.irq(None)
                print('Total Tips(Rain Gauge):', rtcDataPresses)
                #print('rtcDataPresses: ', rtcDataPresses)
                #print('message["rain_tips"]: ', message['rain_tips'])
                message['rain_tips'] = rtcDataPresses
                message['rain_mm'] = rtcDataPresses * 0.2794
                rtcDataPresses = 0
                pinRain.irq(trigger=machine.Pin.IRQ_FALLING, handler=countingRain)
            except:
                pass
            try:
                print(message)
                mqtt.publish(topic_pub, json.dumps(message), False, 1)
            except OSError as e:
                print('Problem with Publish, error')
                print(e)
                print('Error sleep')
                machine.deepsleep(errorTime * 1000)
                machine.reset()
            else:
                print('Message send')
                try:
                    mqtt.disconnect()
                except:
                    pass
                rtcData["presses"] = rtcDataPresses
                print('rtcDataPresses: ', rtcDataPresses)
                try:
                    rtc.memory(json.dumps(rtcData))
                except:
                    pass
                rain_sleep = True
                esp32.wake_on_ext0(pin = pinRain, level = esp32.WAKEUP_ALL_LOW)
                try:
                    sta_if.disconnect()
                    sta_if.active(False)
                except:
                    pass
                time.sleep(0.1)
                try:
                    machine.freq(20000000)
                except:
                    pass
                endMainTime1 = time.time()
                cycleTime = (endMainTime1 - startMainTime1) + bootTime + importTime
                print('Cycle time:', cycleTime)
                print('Sleep after message')
                print((sendTime - cycleTime ) * 1000)
                lightSleep = sendTime - cycleTime
                if lightSleep > sendTime or lightSleep <= 0:
                    machine.lightsleep((sendTime - correctionTime) * 1000)
                else:
                    machine.lightsleep(int((lightSleep - correctionTime) * 1000))
                while True:
                    spin += 1
                    #time.sleep(0.1)
                    #print('spin: ', spin)
                    if spin > 16:
                        spin = 0
                        machine.soft_reset()
    else:
        print('Cant connect to WiFi, error')
        print('Error sleep')
        machine.deepsleep(errorTime * 1000)
        machine.reset()
        
    print('...main...')
except Exception as e:
    print('Error(Exception)...')
    print(e)
    machine.reset()
