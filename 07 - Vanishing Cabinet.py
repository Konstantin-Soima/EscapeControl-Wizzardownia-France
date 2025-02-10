from api import EscapeControlAPI
from time import sleep
from time import time

api = EscapeControlAPI()

mainDev = 1
cabinet1Dev = 5
cabinet2Dev = 6
maglock1 = 17
maglock2 = 18
doorsPin1 = 8
doorsPin2 = 8
#B- dev 5 = UV
opens = 0
api.GPIOSet(mainDev, 20, False)  # Chains lock
api.GPIOSetAnalog(cabinet1Dev,12,0)
while True: #TODO: сделать рабочим на протяжении 10 минут, потом выключать
    if api.GPIORead(cabinet1Dev,doorsPin1):
        api.GPIOSet(mainDev,maglock2,True)
    else:
        api.GPIOSet(mainDev,maglock2,False)
    if api.GPIORead(cabinet2Dev,doorsPin2):
        api.GPIOSet(mainDev,maglock1,True)
        opens += 1
        if opens == 10:
            api.LocksUnlock(9)
    else:
        api.GPIOSet(mainDev,maglock1,False)
    if not api.GPIORead(cabinet2Dev,doorsPin2) and not api.GPIORead(cabinet1Dev,doorsPin1):
        api.GPIOSetAnalog(cabinet1Dev,12,255)
    else:
        api.GPIOSetAnalog(cabinet1Dev,12,0)
    sleep(0.2)
    #TODO: считать что больше двух вышло