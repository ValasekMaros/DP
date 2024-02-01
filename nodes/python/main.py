import os
import ubinascii
import gc
from umqttsimple import MQTTClient
from bmp085 import BMP180
import dht
gc.collect()
# Set frequency for CPu to 80MHz
machine.freq(80000000)
print(machine.freq())

# Sleep time for sleep after error and sleep after successful message send
errorTime = 15 * 1000
sendTime = 1 * 60 * 1000
# MQTT ID for connect
mqtt_client = ubinascii.hexlify(machine.unique_id())
# MQTT topic for publishing
topic_pub = 'Testing'

calc_interval = 1000

rainTrigger = 0
lastMicrosRG = 0
pinRain = machine.Pin(15, machine.Pin.IN)

wind_debounce_time = 125
windTrigger = 0
wind_lastMicros = 0
pinWindSpeed = machine.Pin(15, machine.Pin.IN)

pinWindDir = machine.ADC(machine.Pin(15))
pinWindDir.atten(machine.ADC.ATTN_11DB)

windDirMin = [2923, 1367, 1586, 106, 159, 30, 493, 263, 896, 726, 2246, 2126, 4054, 3179, 3644, 2536]
windDirMax = [3005, 1449, 1668, 158, 217, 105, 575, 345, 978, 808, 2328, 2208, 4136, 3261, 3726, 2618]
windDirDeg = [0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5, 180, 202.5, 225, 247.5, 270, 292.5, 315, 337.5]
# --------------------------------------------------------------------------------------------
# Functions
def countingRain(pin):
    pinRain.irq(None)
    global rainTrigger
    rainTrigger += 1
    time.sleep(0.15)
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
# Need to add try: for exception
I2C = machine.I2C(0, sda = machine.Pin(21), scl = machine.Pin(22), freq = 40000)
bmp180 = BMP180(I2C)
bmp180.oversample = 3
bmp180.sealevel = 1039.3

# --------------------------------------------------------------------------------------------
dht22 = dht.DHT22(machine.Pin(23))
bmp180.makegauge()
time.sleep(0.25)
temp_bmp180 = bmp180.temperature
press_bmp180 = bmp180.pressure
altitude_bmp180 = bmp180.altitude
print(temp_bmp180, press_bmp180, altitude_bmp180)

dht22.measure()
time.sleep(0.25)
temp_dht22 = dht22.temperature()
hum_dht22 = dht22.humidity()
print(temp_dht22, hum_dht22)

pinRain.irq(trigger=machine.Pin.IRQ_RISING, handler=countingRain)
nextcalc = round(time.time_ns() / 1000000) + calc_interval 
while True:
    timer = round(time.time_ns() / 1000000)
    if timer >= nextcalc:
        nextcalc = timer + calc_interval
        print('Total Tips(Rain Gauge):', rainTrigger)
        break
pinRain.irq(None)

pinWindSpeed.irq(trigger=machine.Pin.IRQ_FALLING, handler=countingWind)
nextcalc = round(time.time_ns() / 1000000) + calc_interval 
while True:
    timer = round(time.time_ns() / 1000000)
    if timer >= nextcalc:
        nextcalc = timer + calc_interval
        print('Total Tips(Wind Speed):', windTrigger)
pinWindSpeed.irq(None)

while True:
    pinWindDir_value = 0
    for i in range(8):
        pinWindDir_value += pinWindDir.read()
    pinWindDir_value /= 8
    for i in range(len(windDirDeg)):
        if pinWindDir_value >= windDirMin[i] and pinWindDir_value <= windDirMax[i]:
            print(windDirDeg[i])
            break
    time.sleep(0.5)

mqtt = MQTTClient(mqtt_client, auth.mqtt_host, auth.mqtt_port, auth.mqtt_user, auth.mqtt_pass)
if sta_if.isconnected():
    try:
        mqtt.connect()
    except OSError as e:
        print('Cant connect to MQTT - ' + e)
        machine.reset()
    else:
        try:
            mqtt.publish(topic_pub, "Hello World", False , 1)
        except OSError as e:
            print('Problem with Publish - ' + e)
            machine.reset()
        else:
            print('Message send')
            mqtt.disconnect()
            print(time.time() - zaciatok)
            #machine.lightsleep(sendTime)
            #machine.reset()
else:
    print('Cant connect to WiFi')
    machine.reset()
