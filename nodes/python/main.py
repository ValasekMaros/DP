import machine
import os
import ubinascii
import time
import gc
from umqttsimple import MQTTClient

gc.collect()

mqtt_client = ubinascii.hexlify(machine.unique_id())
topic_pub = 'Testing'

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
else:
    print('Cant connect to WiFi')
    machine.reset()