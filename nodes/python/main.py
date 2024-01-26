from machine import Pin
import time

led = Pin(2, Pin.OUT)
for i in range(16):
    led.on()
    time.sleep(0.1)
    led.off()
    time.sleep(0.1)
