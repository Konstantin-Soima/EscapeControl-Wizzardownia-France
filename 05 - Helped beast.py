from api import EscapeControlAPI
from time import sleep, time
from threading import Thread

api = EscapeControlAPI()

# Константы
beastDev = 3
RX = 7
TX = 8
DF = 1
BUSY = 55
folder = 3
volume = 25
sleeping_sound = 5
correct_sound = 3
incorrect_sound = 2
lang = api.GetParameter("language")
hint_sound = 9
if lang == 1:
    hint_sound = 10 
short_hint_sound = 6
if lang == 1:
    short_hint_sound = 206
wakeup_Sound = 4
if lang == 1:
    wakeup_Sound = 4 #TODO: replace to guden tag
pins_analog = [54, 55, 56 ,57, 58]
pins_digital = [0,1,2,3, 4]
sensity = [75, 60, 82, 60, 86]
sensity_range = [
    range(60, 140), range(60, 140), range(60, 135), range(60, 140), range(60, 137)
]
seq = [0, 3, 1]  # Последовательность
longed = 5  # Порог активации
activated = [0] * 5
deactivated = [0] * 5

# Настройка DFPlayer и начальный лог
api.DFPlayerBegin(beastDev, DF, RX, TX)
sleep(1)
api.DFPlayerVolume(beastDev, DF, volume)
sleep (2)
api.DFPlayerStop(beastDev, DF)
# Калибровка сенсоров
start = [0]*5
def calibrate_sensors():
    api.Log("Starting sensitivity calibration")
    for i in range(5):
        api.GPIOMode(beastDev, pins_analog[i], 0)  # Правильный режим для аналоговых пинов
        aPin = api.GPIOReadAnalog(beastDev, pins_analog[i])
        api.Log("Analog PIN " + str(pins_analog[i]) + " value: " + str(aPin))
        start[i] = aPin

calibrate_sensors()

# Повторение ответа
def repeat_answer():
    activated = [-2] * 5
    while True:
        for i in range(5):
            aPin = api.GPIOReadAnalog(beastDev, pins_digital[i])
            if aPin >= sensity[i]:
                activated[i] += 1
                api.Log("Signal on pin:" + str(pins_digital[i]) + " value:" + str(aPin))
                if activated[i] >= longed:
                    api.DFPlayerPlayFolder(beastDev, DF, folder, short_hint_sound)
                    sleep(32)
                    activated = [-2] * 5
        sleep(0.3)

repeat_answer()
