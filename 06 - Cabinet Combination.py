from api import EscapeControlAPI
from time import sleep
from time import time

api = EscapeControlAPI()

mainDev = 1
cabinet1Dev = 5
hand = 5
pins = [3, 4, 2, 6, 7]  # 6 -Ring, 7 - spiders, 2 -candle, 3 - Egg, 4 - scull
doors = 8
handLight = 10
answer = [7, 2, 6, 4, 3]
stack = [None] * 5
maglock1 = 17
maglock2 = 18
api.GPIOSet(mainDev, maglock1, True)
api.GPIOSet(mainDev, maglock2, True)

def stackAppend(n):
    non = stack.count(None)
    if non > 0:
        stack[5 - non] = n
    else:
        for i in range(4):
            stack[i] = stack[i + 1]
        stack[4] = n


last = [None] * 5
while True:
    sleep(0.2)
    elements = api.GPIOReadList(cabinet1Dev, pins)
    if elements == last:
        continue
    if sum(elements) == 4:
        api.Log(elements)
        pined = pins[elements.index(0)]
        stackAppend(pined)
        api.Log(stack)
        last = elements
    if stack == answer:
        api.LocksUnlock(8)
        break
api.LocksUnlock(7 + 1)
