import machine
import time

windDirMin = [2783, 1336, 1566, 167, 200, 104, 532, 320, 903, 746, 2240, 2045, 3723, 3224, 3278, 2578]
windDirMax = [3223, 1565, 1885, 205, 245, 128, 650, 392, 1103, 901, 2578, 2239, 4334, 3277, 3722, 2782]
windDirDeg = [0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5, 180, 202.5, 225, 247.5, 270, 292.5, 315, 337.5]
windDirName = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']

pinWindDir = machine.ADC(machine.Pin(36))
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