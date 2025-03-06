from api import EscapeControlAPI
from time import sleep, time
from threading import Thread

api = EscapeControlAPI()

# Константы
beastDev = 3
RX = 9
TX = 8
DF = 1
BUSY = 61
folder = 3
volume = 25
sleeping_sound = 5
correct_sound = 3
incorrect_sound = 2
lang = api.GetParameter("language")
hint_sound = 9
if lang == 1:
    hint_sound = 209 
wakeup_Sound = 4
if lang == 1:
    wakeup_Sound = 204
pins_analog = [54, 55, 56 ,57, 58]
pins_digital = [0,1,2,3, 4]
sensity = [75, 60, 82, 60, 86]
sensity_range = [
    range(60, 140), range(60, 140), range(60, 140), range(60, 140), range(60, 137)
]
seq = [0, 3, 2]  # Последовательность
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
# Реакции на касания
def handle_reactions():
    api.DFPlayerPlayFolder(beastDev, DF, folder, wakeup_Sound)  # Пробуждение
    sleep(10)
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

handle_reactions()
api.LocksUnlock(7)
api.ScenarioStart(52)
'''
# Константы
DEBOUNCE_TIME = 0.3  # время в секундах для подтверждения касания
SEQUENCE = [0, 3, 2]  # правильная последовательность
CHECK_INTERVAL = 0.05  # интервал проверки датчиков

# Инициализация состояний датчиков
sensors = [{
    "pin": pins_digital[i],
    "threshold_range": sensity_range[i],
    "is_active": False,
    "last_change": 0
} for i in range(5)]

current_step = 0

def read_sensors():
    for sensor in sensors:
        value = api.GPIOReadAnalog(beastDev, sensor["pin"])
        # Если значение попадает в диапазон, считаем, что датчик активен
        if value in sensor["threshold_range"]:
            if not sensor["is_active"]:
                # При переходе в активное состояние запоминаем время
                sensor["last_change"] = time()
            sensor["is_active"] = True
        else:
            sensor["is_active"] = False

def process_sequence():
    global current_step
    for sensor in sensors:
        if sensor["is_active"]:
            # Если прошло достаточное время с момента перехода в активное состояние
            if time() - sensor["last_change"] >= DEBOUNCE_TIME:
                # Если датчик соответствует ожидаемому
                if sensor["pin"] == pins_digital[ SEQUENCE[current_step] ]:
                    api.DFPlayerPlayFolder(beastDev, DF, folder, correct_sound)
                    api.Log("Correct touch:"+str(sensor["pin"])+" on step:"+str(current_step))
                    current_step += 1
                    if current_step >= len(SEQUENCE):
                        api.Log("Sequence complete")
                        return True
                elif current_step > 0 and sensor["pin"] == pins_digital[ SEQUENCE[current_step-1] ]:
                    api.DFPlayerPlayFolder(beastDev, DF, folder, correct_sound)
                else:
                    # Ошибка: сброс последовательности
                    api.DFPlayerPlayFolder(beastDev, DF, folder, incorrect_sound)
                    api.Log("Wrong touch:"+str(sensor["pin"])+" on step:"+str(current_step))
                    current_step = 0
                # После обработки сбрасываем время, чтобы не сработало повторно
                sensor["last_change"] = time() + 3  # небольшая задержка до следующего срабатывания
    return False

# Основной цикл после пробуждения
api.DFPlayerPlayFolder(beastDev, DF, folder, wakeup_Sound)
sleep(10)

while True:
    read_sensors()
    if process_sequence():
        break
    sleep(CHECK_INTERVAL)

api.DFPlayerPlayFolder(beastDev, DF, folder, hint_sound)
api.LocksUnlock(7)
sleep(50)
api.ScenarioStart(52)