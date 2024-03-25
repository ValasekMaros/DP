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
gc.collect()

print('...main...')

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
    "battery_voltage": None
}

rtc = machine.RTC()

# Sleep time(in seconds) for sleep after error and sleep after successful message send, and for warming sensors
warmSensor = 5
errorTime = 300
sendTime = 1800
# MQTT ID for connect
#mqtt_client = ubinascii.hexlify(machine.unique_id())
mqtt_client = "MeteoStation00"
# MQTT topic for publishing
topic_pub = 'project'

calc_interval = 15000
rain_debounce_time = 150
wind_debounce_time = 125
rainTrigger = 0
windSpeedTrigger = 0
windDir_deg = 0
windDir_name = None

lastMicrosRG = 0
wind_lastMicros = 0

windDirMin = [2783, 1336, 1566, 167, 200, 104, 532, 320, 903, 746, 2371, 2045, 3723, 3224, 3278, 2579]
windDirMax = [3223, 1565, 1885, 205, 245, 128, 650, 392, 1103, 901, 2578, 2370, 4334, 3277, 3722, 2782]
windDirDeg = [0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5, 180, 202.5, 225, 247.5, 270, 292.5, 315, 337.5]
windDirName = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
# --------------------------------------------------------------------------------------------
# Pins
i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21), freq=10000)
pinDHT = machine.Pin(23)
pinRain = machine.Pin(34, machine.Pin.IN)
pinWindSpeed = machine.Pin(15, machine.Pin.IN)
pinWindDir = machine.ADC(machine.Pin(36))
pinWindDir.atten(machine.ADC.ATTN_11DB)

#pinBMP_power = machine.Pin(19, machine.Pin.OUT)
pinBME_power = machine.Pin(19, machine.Pin.OUT)
pinDHT_power = machine.Pin(18, machine.Pin.OUT)

pinRain_power = machine.Pin(5, machine.Pin.OUT)
pinWindSpeed_power = machine.Pin(17, machine.Pin.OUT)
pinWindDir_power = machine.Pin(16, machine.Pin.OUT)

# --------------------------------------------------------------------------------------------
# Functions
def countingRain(pin):
    pinRain.irq(None)
    rtc.datetime((2000,01,01,5,0,0,0,0))
    print('Interupt...')
    global rain_lastMicros
    global rain_debounce_time
    global rainTrigger
    if round(time.time_ns() / 1000) - rain_lastMicros >= rain_debounce_time * 1000:
        rainTrigger += 1
        rain_lastMicros = round(time.time_ns() / 1000)
    pinRain.irq(trigger=machine.Pin.IRQ_RISING, handler=countingRain)

def countingWind(pin):
    print('Interupt...')
    rtc.datetime((2000,01,01,5,0,0,0,0))
    global wind_lastMicros
    global wind_debounce_time
    global windSpeedTrigger
    if round(time.time_ns() / 1000) - wind_lastMicros >= wind_debounce_time * 1000:
        windSpeedTrigger += 1
        wind_lastMicros = round(time.time_ns() / 1000)
# --------------------------------------------------------------------------------------------
# Powering BMP and DHT
#pinBMP_power.on()
pinBME_power.on()
pinDHT_power.on()
pinWindDir_power.on()
pinRain_power.on()
pinWindSpeed_power.on()
machine.lightsleep(warmSensor * 1000)

try:
    sensor = ina219.INA219(i2c, addr=0x40)
    sensor.set_calibration_16V_400mA()
except OSError as e:
    print('Cand connect to INA219, error')
    print(e)
    endTime = time.time()
    cycleTime = endTime - zaciatok
    print('Cycle time:', cycleTime)
    print('Error sleep')
    machine.deepsleep(errorTime * 1000)
    machine.reset()
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
    bme280 = BME280.BME280(mode=3, address=0x77, i2c=i2c)
    dht22 = dht.DHT22(pinDHT)
    #bmp180.makegauge()
    dht22.measure()
except OSError as e:
    print('Cand connect to BME or DHT, error -', e)
    endTime = time.time()
    cycleTime = endTime - zaciatok
    print('Cycle time:', cycleTime)
    print('Error sleep')
    machine.deepsleep(errorTime * 1000)
    machine.reset()
else:
    print('Connected to BME and DHT')
    temp_bme280 = bme280.temperature
    hum_bme280 = bme280.humidity
    press_bme280 = bme280.pressure
    print('BME:', temp_bme280, hum_bme280, press_bme280)
    message['bme_temp'] = temp_bme280
    message['bme_hum'] = hum_bme280
    message['bme_press'] = press_bme280

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

rtc.datetime((2000,01,01,5,0,0,0,0))

pinRain.irq(trigger=machine.Pin.IRQ_RISING, handler=countingRain)
nextcalc = round(time.time_ns() / 1000000) + calc_interval
#print('Start of rain sensor:', nextcalc)
while True:
    timer = round(time.time_ns() / 1000000)
    #time.sleep(0.1)
    if timer >= nextcalc:
        print('Total Tips(Rain Gauge):', rainTrigger)
        try:
            message['rain_tips'] = rainTrigger
            message['rain_mm'] = rainTrigger * 0.2794 / calc_interval * 3600000
        except:
            pass
        break
#print('End of rain sensor:', timer)
pinRain.irq(None)
pinRain_power.off()

rtc.datetime((2000,01,01,5,0,0,0,0))

pinWindSpeed.irq(trigger=machine.Pin.IRQ_FALLING, handler=countingWind)
nextcalc = round(time.time_ns() / 1000000) + calc_interval 
while True:
    timer = round(time.time_ns() / 1000000)
    #time.sleep(0.1)
    if timer >= nextcalc:
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
pinWindSpeed_power.off()

pinWindDir_value = 0
for i in range(8):
    pinWindDir_value += pinWindDir.read()
pinWindDir_value /= 8
message['windDir_ADC'] = pinWindDir_value
for i in range(len(windDirDeg)):
    if pinWindDir_value >= windDirMin[i] and pinWindDir_value <= windDirMax[i]:
        windDir_deg = windDirDeg[i]
        windDir_name = windDirName[i]
        message['windDir_deg'] = windDir_deg
        message['windDir_name'] = windDir_name
        break
print('Wind Direction Deg:', windDir_deg)
print('Wind Direction Name:', windDir_name)
pinWindDir_power.off()

machine.freq(80000000)

sta_if.active(True)
print('Wifi activated')
sta_if.connect(auth.SSID_Name, auth.SSID_Pass)

rtc.datetime((2000,01,01,5,0,0,0,0))

nextcalc = round(time.time_ns() / 1000000) + calc_interval
while not sta_if.isconnected():
    timer = round(time.time_ns() / 1000000)
    if timer >= nextcalc:
        print('Cant connect to WiFi, error')
        endTime = time.time()
        cycleTime = endTime - zaciatok
        print('Cycle time:', cycleTime)
        print('Error sleep')
        machine.deepsleep((errorTime - cycleTime) * 1000)
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
        endTime = time.time()
        cycleTime = endTime - zaciatok
        print('Cycle time:', cycleTime)
        print('Error sleep')
        machine.deepsleep(errorTime * 1000)
        machine.reset()
    else:
        try:
            print(message)
            mqtt.publish(topic_pub, json.dumps(message), False, 1)
        except OSError as e:
            print('Problem with Publish, error')
            print(e)
            endTime = time.time()
            cycleTime = endTime - zaciatok
            print('Cycle time:', cycleTime)
            print('Error sleep')
            machine.deepsleep(errorTime * 1000)
            machine.reset()
        else:
            print('Message send')
            mqtt.disconnect()
            sta_if.disconnect()
            sta_if.active(False)
            endTime = time.time()
            cycleTime = endTime - zaciatok
            print('Cycle time:', cycleTime)
            print('Deep sleep after message')
            machine.deepsleep(sendTime * 1000)
            machine.reset()
else:
    print('Cant connect to WiFi, error')
    endTime = time.time()
    cycleTime = endTime - zaciatok
    print('Cycle time:', cycleTime)
    print('Error sleep')
    machine.deepsleep(errorTime * 1000)
    machine.reset()
print('...main...')
machine.reset()
