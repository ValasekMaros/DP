import machine
import time

machine.freq(80000000)
print(machine.freq())

calc_interval = 1000
debounce_time = 125
rainTrigger = 0
lastMicrosRG = 0

def countingRain(pin):
    print('Interupt...')
    global lastMicrosRG
    global debounce_time
    global rainTrigger
    if round(time.time_ns() / 1000) - lastMicrosRG >= debounce_time * 1000:
        rainTrigger += 1
        lastMicrosRG = round(time.time_ns() / 1000)
    
pinRain = machine.Pin(15, machine.Pin.IN)
pinRain.irq(trigger=machine.Pin.IRQ_FALLING, handler=countingRain)

nextcalc = round(time.time_ns() / 1000000) + calc_interval 
while True:
    timer = round(time.time_ns() / 1000000)
    if timer >= nextcalc:
        nextcalc = timer + calc_interval
        print('Total Tips:', rainTrigger)