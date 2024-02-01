import machine
import time

machine.freq(80000000)

calc_interval = 1000
debounce_time = 225
rainTrigger = 0
lastMicrosRG = 0

def countingRain(pin):
    pinRain.irq(None)
    global rainTrigger
    rainTrigger += 1
    time.sleep(0.15)
    pinRain.irq(trigger=machine.Pin.IRQ_RISING, handler=countingRain)

pinRain = machine.Pin(15, machine.Pin.IN)
pinRain.irq(trigger=machine.Pin.IRQ_RISING, handler=countingRain)

nextcalc = round(time.time_ns() / 1000000) + calc_interval 
while True:
    timer = round(time.time_ns() / 1000000)
    if timer >= nextcalc:
        nextcalc = timer + calc_interval
        print('Total Tips:', rainTrigger)