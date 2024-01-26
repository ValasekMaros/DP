import machine
import time

led = machine.Pin(2, machine.Pin.OUT)

for i in range(8):
    led.on()
    time.sleep(0.5)
    led.off()
    time.sleep(0.5)
machine.reset()
