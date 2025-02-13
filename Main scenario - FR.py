from api import EscapeControlAPI
from time import sleep
from time import time
import math

api = EscapeControlAPI()

'''DEVICES'''
mainDev = 1
ghostDev = 2
beastDev = 3
elfDev = 4
cabinet1Dev = 5
cabinet2Dev = 6
alchiDev = 7
treeDev = 8
castleDev = 9

'''LIGHTS'''
wandSpot = 45
room1_light = 44
room2_light = 46

'''MAGNET LOCKS'''
doorLock1 = 16
maglock1 = 17
maglock2 = 18
doorLock2 = 19

api.GPIOSet(mainDev,maglock1,True)
api.GPIOSet(mainDev,maglock2,True)

'''PINS'''
motorPin = 56 #Spirit Box solenoid
ghostRgbPins = [10, 11, 12]
handLight = 14  # M-
alchemicalLED = 10

'''Initialization of players'''
player_ost = api.connectToPlayer(1)  # Плеер фоновых саундтреков
player_sfx = api.connectToPlayer(2)  # Плеер ситуационных звуков
player_txt = api.connectToPlayer(3)  # Плеер ситуационных звуков
player_ost.volume(180)
player_sfx.volume(280)
player_txt.volume(300)
player_sfx.setLoop(False)
player_ost.setLoop(False)
player_txt.setLoop(False)
#VLC Player functions
def playOst(sound):
    player_ost.playSound(sound + ".mp3")

def playSfx(sound):
    player_sfx.playSound(sound + ".mp3")

def playTxt(sound):
    player_txt.playSound(sound + ".mp3")

#WAITING TASKS
def waitBoxWithGhost(): #Scenario 4
    api = EscapeControlAPI()
    playerPins = [1,57,58] #DF Player number, RX pin, TX pin
    folder_id = 1
    exit_sound = 3
    sleep(0.2)
    api.LocksWait(4)
    #Outro animation
    api.DFPlayerBegin(ghostDev, playerPins[0], playerPins[1], playerPins[2])
    sleep(0.2)
    api.DFPlayerStop(ghostDev, playerPins[0])
    silentHit()
    api.DFPlayerVolume(ghostDev, playerPins[0], 30)
    splashGhostBox()
    api.DFPlayerPlayFolder(ghostDev, playerPins[0], folder_id, exit_sound)
    sleep(1)
    hit()
    sleep(1)
    hit()
    splashGhostBox()
    for i in range(6):
        silentHit()
        sleep(0.07)
    for i in range(4):
        silentHit2()
        sleep(0.1)
    for i in range(3):  # смесь ударов
        silentHit2()
        sleep(0.1)
        hit()
        sleep(0.1)
    for i in range(4):
        hit()
        splashGhostBox()
    api.GPIOSet(ghostDev, motorPin, True)
    splashGhostBox()
    sleep(2)
    api.GPIOSet(ghostDev, motorPin, False)
    for rgb in range(3):  # обнуляем всё
        api.GPIOSetAnalog(ghostDev, ghostRgbPins[rgb], 0)
    playTxt("Heed_the_ghost_s_message_FR")
    api.ScenarioStop(7) #kill all parralel reading
    api.ScenarioStop(4)
    player_ost.volume(160)

def waitKnockingToTheDoor(): #Scenario 5
    api = EscapeControlAPI()
    api.LocksWait(5)
    player_ost.volume(180) #Higher OST music 
    api.GPIOSet(mainDev, 19, False) #Elf's door lock    
    api.ScenarioStop(5)
    api.ScenarioStart(7)

def waitToadPlayer():
    api = EscapeControlAPI()
    playerPins = [2,9,54,56] #DF Player number, RX pin, TX pin, Busy
    folder_id = 2
    wakeup_sound = 2
    api.LocksWait(6)
    #звук побудки
    sleep(0.1)
    api.DFPlayerPlayFolder(beastDev,playerPins[0],folder_id,wakeup_sound)
    while not api.GPIORead(beastDev,):
        sleep(0.5)
    sleep(0.3)
    api.SetParameter('frogSongEnd', 1) 

def waitCabinetCombination():
    api = EscapeControlAPI()
    sleep(0.2)
    api.LocksWait(8)
    api.ScenarioStop(7)
    api.ScenarioStop(8)
    api.ScenarioStop(8)#TODO: number of additional scenario for Hand light
    api.GPIOSet(mainDev, 20, False)  # Chains lock
    api.GPIOSet(cabinet1Dev,handLight,False)

def waitTapestry():
    api = EscapeControlAPI()
    sleep(0.2)
    api.LocksWait(11)
    playTxt("Tapestry_solved_FR")

def waitAlchemical():
    rfidControlPin = 12         # Пин для управления RFID (ON/OFF)
    magicBallsLedControlPin = 11          # Пин для управления LED
    magicBallsDoorPin = 22      # Пин для двери с магическими шарами
    api = EscapeControlAPI()
    sleep(0.2)
    api.GPIOSet(alchiDev, magicBallsDoorPin, False) #OPEN MAGIC BALLS DOOR
    magicBallsDoorPin
    api.LocksWait(13)
    playSfx("alchemy_adding_ingredients")
    api.ScenarioStop(13)
    api.ScenarioStop(12)#Kill magic ball reader
    api.GPIOSet(alchiDev, rfidControlPin, False) #RFID Off
    api.GPIOSet(alchiDev, rfidControlPin, False) #RFID Off
    animation = range(149)
    for i in animation:
        api.GPIOSetAnalog(alchiDev, alchemicalLED, int(abs(math.sin(i / math.pi) * 256)))  # LED-
        sleep(0.01)
    api.GPIOSet(alchiDev, magicBallsLedControlPin, False) #Light Off magic ball
    playTxt("Director_reappears_FR")
    sleep(20)

def waitCastle():
    api = EscapeControlAPI()
    sleep(0.2)
    api.LocksWait(14)
    api.ScenarioStop(15)
    api.ScenarioStop(14)
    playTxt("Activate_castle_protection_DE")
    api.ScenarioStart(16) #Castle animation
    sleep(25)
    playTxt("Outro_DE")

'''Ghost box actions'''
def splashGhostBox():
    for rgb in range(3):
        api.GPIOSetAnalog(ghostDev, ghostRgbPins[rgb], 255)
    sleep(0.02)
    for rgb in range(3):
        api.GPIOSetAnalog(ghostDev, ghostRgbPins[rgb], 0)
    sleep(0.5)
    api.GPIOSetAnalog(ghostDev, ghostRgbPins[0], 66)  # Красный цвет
    api.GPIOSetAnalog(ghostDev, ghostRgbPins[1], 135)  # Зеленый цвет
    api.GPIOSetAnalog(ghostDev, ghostRgbPins[2], 200)  # Синий цвет

def silentHit():  # Еле бьёт
    hit(0.02)  # Мотор не успевает сработать

def silentHit2():  # Средне бьёт
    hit(0.045) # Мотор тут же возвращается обратно

def hit(duration = 0.07):  # Сильно бьёт
    api.GPIOSet(ghostDev, motorPin, True)
    sleep(duration)  # Двойной удар: вверх и вниз из-за долгой паузы
    api.GPIOSet(ghostDev, motorPin, False)

'''First room'''
def room1():
    api.Log("Welcome to the Game")
    # Изначально свет в комнате почти отсутствует. Световой спот горит над шкатулкой с палочками.
    api.GPIOSet(mainDev, wandSpot, True)
    api.GPIOSet(mainDev, room1_light, False)
    api.GPIOSet(mainDev, doorLock1, True)
    api.GPIOSet(mainDev, doorLock2, True)
    api.ScenarioStart(3)
    api.LocksWait(3)
    # Когда игроки берут палочки, срабатывает электроника и проигрывается аудио.Загорается свет в комнате.
    playTxt("Intro_DE")
    sleep(53)
    playOst("ambience_1")
    api.GPIOSet(mainDev, room1_light, True)
    # Все загадки активны со входа
    api.ScenarioStart(4)
    api.ScenarioStart(5)
    api.ScenarioStart(7)
    api.ScenarioStart(8)#TODO: change number of additional scenario for Hand light
    waitBoxWithGhost()
    api.ScenarioStart(6)
    waitKnockingToTheDoor()
    waitToadPlayer()
    api.ScenarioStart(8)
    waitCabinetCombination()
    # Активация шлюза
    api.ScenarioStart(9)

'''Second room'''
def room2():
    api.Log("Office opened")
    api.GPIOSet(mainDev, room2_light, True)
    playOst("ambience_2")
    api.LocksWait(9)
    sleep(60)
    playTxt("Click_on_books_FR")
    api.ScenarioStart(10)
    api.LocksWait(10)
    api.GPIOSet(mainDev, 21, False)  # Lighter Locker
    api.ScenarioStart(11)
    waitTapestry()
    api.ScenarioStart(12)
    api.ScenarioStart(13)
    waitAlchemical()
    api.ScenarioStart(14)
    api.ScenarioStart(15)
    waitCastle()
    api.ScenarioStop(9)
    api.GPIOSet(mainDev, doorLock1, False)    
    api.GPIOSet(mainDev, maglock1, False)
    api.GPIOSet(mainDev, maglock2, False)
    api.GPIOSet(mainDev, doorLock2, False) 

room1()
room2()