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
sleeping_sound = 5
correct_sound = 3
incorrect_sound = 2
lang = 1#api.GetParameter("language")
hint_sound = 9
if lang == 1 or True:
    hint_sound = 209 
wakeup_Sound = 4
if lang == 1:
    wakeup_Sound = 204
pins_analog = [54, 55, 56 ,57, 58]
pins_digital = [0,1,2,3, 4]
sensity = [75, 60, 82, 60, 86]
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