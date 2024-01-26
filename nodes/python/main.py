from machine import Pin
import time

led = Pin(2, Pin.OUT)
for i in range(4):
    led.on()
    time.sleep(1)
    led.off()
    time.sleep(1)
