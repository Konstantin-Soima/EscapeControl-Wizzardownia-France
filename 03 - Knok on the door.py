from api import EscapeControlAPI
from time import sleep
from time import time
from threading import Thread
from copy import deepcopy
import numpy as np

api = EscapeControlAPI()
mainDev = 1
elfDev = 4
rgb_pins = [11, 10, 12]#Пины для RGB/GRB ленты
skyColor = [66,135,200] #4287f5
magnet = 19
answer = 20
repeat_pattern = False
piezo = 0
api.GPIOSet(mainDev, magnet, True)
def setBlue(i):
    api.GPIOSetAnalog(elfDev, rgb_pins[0], skyColor[0] // skyColor[2] * i)  # Красный цвет
    #api.GPIOSetAnalog(elfDev, rgb_pins[1], skyColor[1] // skyColor[2] * i)  # Зеленый цвет
    api.GPIOSetAnalog(elfDev, rgb_pins[2], i)  # Синий цвет
def intro():
    for i in range(1,8):
        api.GPIOSet(elfDev, rgb_pins[0], False) 
        api.GPIOSet(elfDev, rgb_pins[1], False)
        api.GPIOSet(mainDev, 44,False)
        api.GPIOSet(mainDev, 45,False)
        sleep(0.2)
        api.GPIOSet(elfDev, rgb_pins[0], True) # Красный цвет
        api.GPIOSetAnalog(elfDev, rgb_pins[1], 170)  # Зеленый цвет
        api.GPIOSet(mainDev, 44,True)
        sleep(1/i)
    api.GPIOSet(elfDev, rgb_pins[0], False) 
    api.GPIOSet(elfDev, rgb_pins[1], False)
    start_timer = time()
    while time()-start_timer < 25:
        for i in range(4):
            api.GPIOSet(mainDev, 44,0)
            api.GPIOSet(mainDev, 45,0)
            sleep(0.3)
            valL = int((time()-start_timer)/20*128)
            api.Log(valL)
            if valL > 255:
                valL = 255
            api.GPIOSetAnalog(mainDev, 44,valL)
            api.GPIOSetAnalog(mainDev, 45,valL)
            sleep(0.2)
        api.GPIOSet(mainDev, 44,True)
        api.GPIOSet(mainDev, 45,True)
        sleep(3)
    waves = [*range(skyColor[2]),*range(skyColor[2],0,-1),
             *range(0,skyColor[2],2),*range(skyColor[2],0,-2),
             *range(skyColor[2]),*range(skyColor[2],skyColor[2]//2,-1),
             *range(skyColor[2]//2,int(skyColor[2]/1.25)),*range(int(skyColor[2]/1.25),int(skyColor[2]/1.75),-1),
             *range(int(skyColor[2]/1.75),skyColor[2]),*range(skyColor[2],0,-1)]
    for i in waves:
        api.GPIOSetAnalog(elfDev, rgb_pins[0], skyColor[0] // skyColor[2] * i)  # Красный цвет
        api.GPIOSetAnalog(elfDev, rgb_pins[1], max(skyColor[1] // skyColor[2] * i,answer))  # Зеленый цвет
        api.GPIOSetAnalog(elfDev, rgb_pins[2], skyColor[2] // skyColor[2] * i)  # Синий цвет

def splash():
    wave = [*range(20,200,10),*range(200,20,-20)]
    for i in wave:
        answer = i
        api.GPIOSetAnalog(elfDev, rgb_pins[1], answer)
    answer = 20
def pattern():
    while repeat_pattern:
        #3 2
        one = [*range(0,skyColor[2],2),*range(skyColor[2],0,-2)]
        two = [*range(0,skyColor[2],3),*range(skyColor[2],0,-3),*range(0,skyColor[2],3),*range(skyColor[2],0,-3)]
        three = [*range(0,skyColor[2],4),*range(skyColor[2],0,-4),*range(0,skyColor[2],4),*range(skyColor[2],0,-4),*range(0,skyColor[2],4),*range(skyColor[2],0,-4)]
        for i in one:
            setBlue(i)
        sleep(1.2)
        for i in three:
            setBlue(i)
        sleep(1.2)
        for i in two:
            setBlue(i)
        sleep(4)
api.GPIOSet(elfDev, rgb_pins[0], True) # Красный цвет
api.GPIOSetAnalog(elfDev, rgb_pins[1], 170)  # Зеленый цвет
api.GPIOSetAnalog(elfDev, rgb_pins[2], 0)  # Синий цвет
api.LocksWait(4)
intro()
repeat_pattern = True
light_tread = Thread(target=pattern)
light_tread.start()
last_knock = api.GPIOReadAnalog(elfDev,0)
count = 0
start_time = time()
cooldown_time = time()
api.Log("Start at value: "+str(last_knock))
stack = []
pattern = [1, 3, 2]
mat = [True, False, False, True, False]
lastTime = time()
ln = sum(pattern)

def anal():
    if len(stack) < ln:
        return False
    # Вычисляем дельты и среднее значение
    lst = np.diff(stack[-ln:])
    avg = np.mean(lst)
    # Проверка условий
    sumT = np.sum(lst)
    if sumT < 11 and sumT>= 2:
        api.Log(lst.tolist())
        return True
    for i in range(len(lst)):
#        if (lst[i] < avg and mat[i]) or (lst[i] > avg and not mat[i]):
        if (lst[i] < avg and mat[i]):
            #api.Log(lst.tolist())
            return False
    # Логирование и возврат результата
    api.Log(lst.tolist())
    return True

while True:
    knock_power = api.GPIOReadAnalog(elfDev, piezo)
    if (knock_power > last_knock + 4):
        api.Log("boom: "+ str(knock_power - last_knock) + " val:" + str(knock_power) + " at:"+str(time()))
        stack.append(time())
        lastTime = time()
        lastBig = knock_power
        if len(stack) >= ln:
            if anal():
                repeat_pattern = False
                sleep(0.1)
                api.GPIOSet(mainDev, magnet, False)
                break
        sleep(0.04)
        while knock_power >= lastBig:
            knock_power = api.GPIOReadAnalog(elfDev, piezo)
            #sleep(0.02)
    last_knock = knock_power
    #sleep(0.02)
api.Log("Open")
api.GPIOSet(mainDev, magnet, False)
light_tread.join()
api.LocksUnlock(5)