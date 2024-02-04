import machine
import time
import os
import ubinascii
import gc
from umqttsimple import MQTTClient
from bmp085 import BMP180
import dht
import json
gc.collect()

print('...main...')

message = {
    "espID": "00",
    "bmp_temp": 0,
    "bmp_press": 0,
    "dht_temp": 0,
    "dht_hum": 0,
    "rain_tips": 0,
    "windSpeed_tips": 0,
    "windDir_deg": 0
}

# Sleep time(in seconds) for sleep after error and sleep after successful message send
errorTime = 60
sendTime = 300
# MQTT ID for connect
mqtt_client = ubinascii.hexlify(machine.unique_id())
# MQTT topic for publishing
topic_pub = 'Testing'

calc_interval = 5000
rain_debounce_time = 150
wind_debounce_time = 125
rainTrigger = 0
windTrigger = 0
lastMicrosRG = 0
wind_lastMicros = 0

windDirMin = [2923, 1367, 1586, 106, 159, 30, 493, 263, 896, 726, 2246, 2126, 4054, 3179, 3644, 2536]
windDirMax = [3005, 1449, 1668, 158, 217, 105, 575, 345, 978, 808, 2328, 2208, 4136, 3261, 3726, 2618]
windDirDeg = [0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5, 180, 202.5, 225, 247.5, 270, 292.5, 315, 337.5]
# --------------------------------------------------------------------------------------------
# Pins
I2C = machine.I2C(0, sda = machine.Pin(21), scl = machine.Pin(22), freq = 40000)
pinDHT = machine.Pin(23)
pinRain = machine.Pin(4, machine.Pin.IN)
pinWindSpeed = machine.Pin(2, machine.Pin.IN)
pinWindDir = machine.ADC(machine.Pin(36))
pinWindDir.atten(machine.ADC.ATTN_11DB)

pinBMP_power = machine.Pin(3, machine.Pin.OUT)
pinDHT_power = machine.Pin(1, machine.Pin.OUT)
pinRain_power = machine.Pin(18, machine.Pin.OUT)
pinWindSpeed_power = machine.Pin(5, machine.Pin.OUT)
pinWindDir_power = machine.Pin(17, machine.Pin.OUT)
# --------------------------------------------------------------------------------------------
# Functions
def countingRain(pin):
    pinRain.irq(None)
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
    global wind_lastMicros
    global wind_debounce_time
    global windTrigger
    if round(time.time_ns() / 1000) - wind_lastMicros >= wind_debounce_time * 1000:
        windTrigger += 1
        wind_lastMicros = round(time.time_ns() / 1000)
# --------------------------------------------------------------------------------------------
# Powering BMP and DHT
pinBMP_power.on()
pinDHT_power.on()
machine.lightsleep(5 * 1000)
# --------------------------------------------------------------------------------------------
# Need to add try: for exception
bmp180 = BMP180(I2C)
bmp180.oversample = 3
bmp180.sealevel = 1013
dht22 = dht.DHT22(pinDHT)
# --------------------------------------------------------------------------------------------
bmp180.makegauge()
temp_bmp180 = bmp180.temperature
press_bmp180 = bmp180.pressure
altitude_bmp180 = bmp180.altitude
print(temp_bmp180, press_bmp180, altitude_bmp180)
message['bmp_temp'] = temp_bmp180
message['bmp_press'] = press_bmp180

dht22.measure()
temp_dht22 = dht22.temperature()
hum_dht22 = dht22.humidity()
print(temp_dht22, hum_dht22)
message['dht_temp'] = temp_dht22
message['dht_hum'] = hum_dht22

pinBMP_power.off()
pinDHT_power.off()

pinRain_power.on()
pinRain.irq(trigger=machine.Pin.IRQ_RISING, handler=countingRain)
nextcalc = round(time.time_ns() / 1000000) + calc_interval
#print('Start of rain sensor:', nextcalc)
while True:
    timer = round(time.time_ns() / 1000000)
    if timer >= nextcalc:
        print('Total Tips(Rain Gauge):', rainTrigger)
        message['rain_tips'] = rainTrigger
        break
#print('End of rain sensor:', timer)
pinRain.irq(None)
pinRain_power.off()

pinWindSpeed_power.on()
pinWindSpeed.irq(trigger=machine.Pin.IRQ_FALLING, handler=countingWind)
nextcalc = round(time.time_ns() / 1000000) + calc_interval 
while True:
    timer = round(time.time_ns() / 1000000)
    if timer >= nextcalc:
        print('Total Tips(Wind Speed):', windTrigger)
        message['windSpeed_tips'] = windTrigger
        break
pinWindSpeed.irq(None)
pinWindSpeed_power.off()

pinWindDir_power.on()
pinWindDir_value = 0
for i in range(8):
    pinWindDir_value += pinWindDir.read()
pinWindDir_value /= 8
for i in range(len(windDirDeg)):
    if pinWindDir_value >= windDirMin[i] and pinWindDir_value <= windDirMax[i]:
        print('Wind Direction:', windDirDeg[i])
        message['windDir_deg'] = windDirDeg[i]
        break
pinWindDir_power.off()
    
if sta_if.isconnected():
    try:
        mqtt = MQTTClient(mqtt_client, auth.mqtt_host, auth.mqtt_port, auth.mqtt_user, auth.mqtt_pass)
        mqtt.connect()
    except OSError as e:
        print('Cant connect to MQTT, error -' + e)
        endTime = time.time()
        cycleTime = endTime - zaciatok
        print('Cycle time:', cycleTime)
        print('Error sleep')
        machine.deepsleep((errorTime - cycleTime) * 1000)
        machine.reset()
    else:
        try:
            print(message)
            mqtt.publish(topic_pub, json.dumps(message), False, 1)
        except OSError as e:
            print('Problem with Publish, error -' + e)
            endTime = time.time()
            cycleTime = endTime - zaciatok
            print('Cycle time:', cycleTime)
            print('Error sleep')
            machine.deepsleep((errorTime - cycleTime) * 1000)
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
            machine.deepsleep((sendTime - cycleTime ) * 1000)
            machine.reset()
else:
    print('Cant connect to WiFi, error -', e)
    endTime = time.time()
    cycleTime = endTime - zaciatok
    print('Cycle time:', cycleTime)
    print('Error sleep')
    machine.deepsleep((errorTime - cycleTime) * 1000)
    machine.reset()
print('...main...')