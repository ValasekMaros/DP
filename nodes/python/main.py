from machine import Pin
import time

led = Pin(2, Pin.OUT)
for i in range(32):
    led.on()
    time.sleep(0.05)
    led.off()
    time.sleep(0.05)
