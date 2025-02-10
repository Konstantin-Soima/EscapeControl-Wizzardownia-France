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
    short_hint_sound = 7
wakeup_Sound = 4
if lang == 1:
    wakeup_Sound = 104
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
sleep(0.1)
api.DFPlayerVolume(beastDev, DF, volume)
sleep (0.2)
api.DFPlayerStop(beastDev, DF)
'''
sleep(1)
api.Log("correct play")
api.DFPlayerPlayFolder(beastDev, DF, folder, correct_sound)
sleep (5)
api.DFPlayerStop(beastDev, DF)
sleep(1)
api.Log("incorrect play")
api.DFPlayerPlayFolder(beastDev, DF, folder, incorrect_sound)
'''
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
                api.Log("I am sleep! Pin:" + str(pins_digital[i]) + " sens:" + str(aPin))
                api.DFPlayerPlayFolder(beastDev, DF, folder, sleeping_sound)
                sleep(12)
        dif = [a - b for a, b in zip(start, cur)]
        api.Log(dif)
        sleep(0.4)

# Реакции на касания
def handle_reactions():
    api.DFPlayerPlayFolder(beastDev, DF, folder, wakeup_Sound)  # Пробуждение
    step = 0
    cur = -1
    current = [False]*5
    angry = True
    currentPlay = 0
    while angry:
        string = ""
        for i in range(5):
            aPin = api.GPIOReadAnalog(beastDev, pins_digital[i])
            string += " pin" + str(pins_digital[i]) + ": " + str(aPin) + " "
            if aPin in sensity_range[i]:  # aPin >= sensity[i]:
                activated[i] += 1
                api.Log(string)
                if activated[i] >= longed:
                    #if i != cur:
                    if not current[i]:
                        if i == seq[step]:
                            step += 1
                            api.DFPlayerPlayFolder(beastDev, DF, folder, correct_sound)
                            api.Log("Play correct sound")
                            currentPlay = correct_sound
                        elif step > 0 and i == seq[step-1]:
                            api.DFPlayerPlayFolder(beastDev, DF, folder, correct_sound)
                            api.Log("Play correct sound")
                            currentPlay = correct_sound
                        else:
                            step = 0
                            if currentPlay != incorrect_sound:
                                api.DFPlayerPlayFolder(beastDev, DF, folder, incorrect_sound)
                                api.Log("Play incorrect sound")
                                currentPlay = incorrect_sound
                        cur = i
                        current[i] = True
                    deactivated[i] = 0
                    activated[i] = -2
                    if step >= len(seq):
                        api.Log("complete")
                        angry = False
                        break
            else:
                deactivated[i] += 1
                if deactivated[i] >= longed:
                    activated[i] = 0
                    current[i] = False
                    if cur == i:
                        cur = -1
        sleep(0.1)
        if api.GPIORead(beastDev, BUSY):
            currentPlay = 0
    api.DFPlayerPlayFolder(beastDev, DF, folder, hint_sound)
    api.LocksUnlock(7)

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

check_sleep_state()
handle_reactions()
repeat_answer()
