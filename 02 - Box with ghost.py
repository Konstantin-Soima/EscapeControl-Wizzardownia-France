from api import EscapeControlAPI
from time import sleep
from time import time
import random
import threading

api = EscapeControlAPI()

ghostDev = 2
rgb_pins = [10, 11, 12]  # Пины для RGB/GRB ленты
skyColor = [66, 135, 200]  # 4287f5
api.GPIOSetAnalog(ghostDev, rgb_pins[0], skyColor[0])  # Красный цвет
api.GPIOSetAnalog(ghostDev, rgb_pins[1], skyColor[1])  # Зеленый цвет
api.GPIOSet(ghostDev, rgb_pins[2], True)  # Синий цвет
motorPin = 56
alive = True
answer = [2, 1, 5, 6]
# O - 4, H - 3, M - 7, III - 8
stack = [None] * 4

# Плеер духа
RX = 58  # A3
TX = 57  # A4
BUSY = 59  # A5
DF = 1
volume = 20 
folder_id = 1
lang = api.GetParameter("language")
ghost_sound = 1
if lang == 1:
    ghost_sound = 21
scrap_sound = 4
exit_sound = 3
api.DFPlayerBegin(ghostDev, DF, RX, TX)
sleep(0.2)
api.DFPlayerVolume(ghostDev, DF, volume)
isAngry = True
def push():
    for i in range(skyColor[1],255,4):
        api.GPIOSetAnalog(ghostDev, rgb_pins[1], i)  # rGb
        api.GPIOSetAnalog(ghostDev, rgb_pins[0], i) 
        api.GPIOSetAnalog(ghostDev, rgb_pins[2], 50) 
        #api.GPIOSet(ghostDev, rgb_pins[1], True)
        #sleep(0.01)
    api.GPIOSetAnalog(ghostDev, rgb_pins[1], skyColor[1])  # Зеленый цвет
    api.GPIOSetAnalog(ghostDev, rgb_pins[0], skyColor[0])  # Зеленый цвет
    api.GPIOSet(ghostDev, rgb_pins[2], True)  # Зеленый цвет

def stackAppend(n):
    non = stack.count(None)
    if non > 0:
        stack[4 - non] = n
    else:
        for i in range(3):
            stack[i] = stack[i + 1]
        stack[3] = n

def scrapers():
    while alive:
        api.DFPlayerPlayFolder(ghostDev, DF, folder_id, ghost_sound)
        sleep(0.2)
        realHit = random.randint(0, 1)
        if realHit and isAngry:
            api.GPIOSet(ghostDev, motorPin, True)
            sleep(0.1)
            api.GPIOSet(ghostDev, motorPin, False)
        while not api.GPIORead(ghostDev,BUSY) and alive:
            sleep(0.2)
        api.DFPlayerVolume(ghostDev, DF, 28)
        if alive:
            sleep(1)
        api.DFPlayerPlayFolder(ghostDev, DF, folder_id, scrap_sound)
        sleep(0.2)
        while not api.GPIORead(ghostDev,BUSY) and alive:
            sleep(0.2)
        api.DFPlayerVolume(ghostDev, DF, volume)
        if alive:
            sleep(1)
    #api.DFPlayerStop(ghostDev, DF)
    #api.DFPlayerPlayFolder(ghostDev, DF, folder_id, exit_sound)

def colorAnimation():
    color = 0
    api.Log("Animated Red")
    while alive:
        # for rgb in range(2):
        n = random.randint(-15, 15)
        color += n
        if color < 0:
            color = 0
        elif color > 180:
            color = 178
        api.GPIOSetAnalog(ghostDev, rgb_pins[0], color)  # Rgb
        # api.GPIOSetAnalog(ghostDev, rgb_pins[1], color)  # rGb
        sleep(0.01)
    api.Log("Stop Red")

stripThread = threading.Thread(target=colorAnimation)
stripThread.start()
soundThread = threading.Thread(target=scrapers)
soundThread.start()
prev = api.GPIOReadList(ghostDev, [2, 3, 4, 5, 6, 7, 8, 9, 54])
while True:  # чтение касания палочек
    contact = api.GPIOReadList(ghostDev, [2, 3, 4, 5, 6, 7, 8, 9, 54])
    if 8 >= sum(contact) >= 5:
        isAngry = False
        diff = [x - y for x, y in zip(prev, contact)]
        if sum(diff) == 1:
            push()
            rune = diff.index(1)
            stackAppend(rune)
            api.Log('you triggered: ' + str(rune))
    if 9 == sum(contact):
        isAngry = True
    if stack == answer:
        alive = False
        api.GPIOSet(ghostDev, motorPin, True)
        break;
    prev = contact
    sleep(0.25)
api.LocksUnlock(4)
sleep(1)
api.GPIOSet(ghostDev, motorPin, False)
api.LocksUnlock(4+0)
