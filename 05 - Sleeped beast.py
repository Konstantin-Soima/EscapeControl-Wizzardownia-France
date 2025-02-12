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
pins_analog = [57, 58, 59, 60, 61]
pins_digital = [3, 4, 5, 6, 7]
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
sleep (5)
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

# Проверка состояния сна
def check_sleep_state():
    sleeped = True
    while sleeped:
        sleeped = not api.GetParameter("frogSongEnd")
        cur = [0]*5
        for i in range(5):
            aPin = api.GPIOReadAnalog(beastDev, pins_digital[i])
            cur[i] = aPin
            if aPin >= sensity[i]:
                #api.Log("I am sleep! Pin:" + str(pins_digital[i]) + " sens:" + str(aPin))
                api.DFPlayerPlayFolder(beastDev, DF, folder, sleeping_sound)
                sleep(12)
        dif = [a - b for a, b in zip(start, cur)]
        api.Log(dif)
        sleep(0.4)

check_sleep_state()