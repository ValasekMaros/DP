import machine
import time

windDirMin = [2923, 1367, 1586, 106, 159, 30, 493, 263, 896, 726, 2246, 2126, 4054, 3179, 3644, 2536]
windDirMax = [3005, 1449, 1668, 158, 217, 105, 575, 345, 978, 808, 2328, 2208, 4136, 3261, 3726, 2618]
windDirDeg = [0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5, 180, 202.5, 225, 247.5, 270, 292.5, 315, 337.5]

pinWindDir = machine.ADC(machine.Pin(15))
pinWindDir.atten(machine.ADC.ATTN_11DB)

while True:
    pinWindDir_value = 0
    for i in range(8):
        pinWindDir_value += pinWindDir.read()
    pinWindDir_value /= 8
    for i in range(len(windDirDeg)):
        if pinWindDir_value >= windDirMin[i] and pinWindDir_value <= windDirMax[i]:
            print(windDirDeg[i])
            break
    time.sleep(0.5)

"""
# finding analog value for directions
while True:
    pinWindDir_value = 0
    for i in range(8):
        pinWindDir_value += pinWindDir.read()
        #print(pinWindDir.read())
    pinWindDir_value /= 8
    print('-----------------------------------')
    print(pinWindDir_value)
    print('-----------------------------------')
    time.sleep(0.25)
"""