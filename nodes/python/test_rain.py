import machine
import time

machine.freq(80000000)
print(machine.freq())

calc_interval = 1000
rain_debounce_time = 150
rainTrigger = 0
rain_lastMicros = 0

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
    
pinRain = machine.Pin(15, machine.Pin.IN)
pinRain.irq(trigger=machine.Pin.IRQ_RISING, handler=countingRain)

nextcalc = round(time.time_ns() / 1000000) + calc_interval 
while True:
    timer = round(time.time_ns() / 1000000)
    if timer >= nextcalc:
        nextcalc = timer + calc_interval
        print('Total Tips:', rainTrigger)

