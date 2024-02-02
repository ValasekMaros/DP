import machine
import time

machine.freq(80000000)
print(machine.freq())

calc_interval = 1000
wind_debounce_time = 125
windTrigger = 0
wind_lastMicros = 0

def countingWind(pin):
    print('Interupt...')
    global wind_lastMicros
    global wind_debounce_time
    global windTrigger
    if round(time.time_ns() / 1000) - wind_lastMicros >= wind_debounce_time * 1000:
        windTrigger += 1
        wind_lastMicros = round(time.time_ns() / 1000)
    
pinWindSpeed = machine.Pin(15, machine.Pin.IN)
pinWindSpeed.irq(trigger=machine.Pin.IRQ_FALLING, handler=countingWind)

nextcalc = round(time.time_ns() / 1000000) + calc_interval 
while True:
    timer = round(time.time_ns() / 1000000)
    if timer >= nextcalc:
        nextcalc = timer + calc_interval
        print('Total Tips:', windTrigger)