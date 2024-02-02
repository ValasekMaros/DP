import os
import ubinascii
import gc
from umqttsimple import MQTTClient
from bmp085 import BMP180
import dht
gc.collect()

errorTime = 15 * 1000
sendTime = 1 * 60 * 1000
mqtt_client = ubinascii.hexlify(machine.unique_id())
topic_pub = 'Testing'

# Need to add try: for exception
I2C = machine.I2C(0, sda = machine.Pin(21), scl = machine.Pin(22), freq = 40000)
bmp180 = BMP180(I2C)
bmp180.oversample = 3
bmp180.sealevel = 1039.3

dht22 = dht.DHT22(machine.Pin(23))
bmp180.makegauge()
time.sleep(0.5)
temp_bmp180 = bmp180.temperature
press_bmp180 = bmp180.pressure
altitude_bmp180 = bmp180.altitude
print(temp_bmp180, press_bmp180, altitude_bmp180)

dht22.measure()
time.sleep(0.5)
temp_dht22 = dht22.temperature()
hum_dht22 = dht22.humidity()
print(temp_dht22, hum_dht22)

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