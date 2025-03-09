from api import EscapeControlAPI
from time import sleep, time

api = EscapeControlAPI()

# Константы
beastDev = 3
RX = 7
TX = 8
DF = 1
BUSY = 55
folder = 3
volume = 25
lang = api.GetParameter("language")
short_hint_sound = 6
if lang == 1:
    short_hint_sound = 206
pins_analog = [54, 55, 56 ,57, 58]
pins_digital = [0,1,2,3, 4]
sensity_range = [
    range(60, 140), range(58, 140), range(60, 135), range(58, 140), range(60, 137)
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
                api.DFPlayerPlayFolder(beastDev, DF, folder, short_hint_sound)
<<<<<<< HEAD
                # После обработки сбрасываем время, чтобы не сработало повторно
                sensor["last_change"] = time() + 30  # небольшая задержка до следующего срабатывания
=======
                sleep(32)
                # После обработки сбрасываем время, чтобы не сработало повторно
                sensor["last_change"] = time() + 3  # небольшая задержка до следующего срабатывания
>>>>>>> 4aaf9f9d6efdf6bd7823ddaf3d6c271b73075d4d
    return False

while True:
    read_sensors()
    if process_sequence():
        break
    sleep(CHECK_INTERVAL)