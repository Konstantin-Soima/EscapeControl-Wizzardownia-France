from api import EscapeControlAPI
import threading
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
wandSpot = 11
room1Light = 10
room2Light = 12

'''MAGNET LOCKS'''
doorRoom1 = 18 #Eter
doorRoom2 = 23 #Exit
elfenDoorMagnet = 19
magicBallsMagnet = 22
UVLightLocker = 21
chainsMagnet = 20
cabinetRoom1magnet = 17
cabinetRoom2magnet = 16

'''LEDs'''
rgbPins = [10, 11, 12]
handLightPin = 10
alchemicalLEDPin = 10
magicBallLEDPin = 12
cabinetUVControlPin = 11
mossLEDPin= 11
ws = [62, 66, 65, 64, 63]

'''PINS'''
motorPin = 56 #Spirit Box solenoid
mossPin = 10
magicBallRFID = 11
alchemicalRFID = 14

'''AUDIO'''
dfrxtx = [
    [ghostDev, 1, 58,57],
    [beastDev, 1, 9, 8],
    [beastDev, 4, 6, 7],
    [cabinet2Dev, 4, 55, 54],
    [treeDev, 5, 61, 60]
]  # Device,DFNumber,RX,TX
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
    api.GPIOSetAnalog(mainDev,room1Light,30)
    setFadeLight(elfDev, "Yellow", 60)
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
        api.GPIOSetAnalog(ghostDev, rgbPins[rgb], 0)
    playTxt("heed_the_ghost_s_message")
    api.ScenarioStop(48) #kill all parralel reading
    api.ScenarioStop(4)
    player_ost.volume(160)
    sleep(36)
    api.GPIOSet(mainDev, room1Light, True)

def waitKnockingToTheDoor(): #Scenario 5
    api = EscapeControlAPI()
    api.LocksWait(5)
    player_ost.volume(180) #Higher OST music 
    api.GPIOSet(mainDev, 19, False) #Elf's door lock    
    api.ScenarioStop(5)
    api.ScenarioStart(48)

def waitToadPlayer():
    api = EscapeControlAPI()
    playerPins = [2,6, 7,60] #DF Player number, RX pin, TX pin, Busy
    folder_id = 2
    wakeup_sound = 2
    api.LocksWait(6)
    #звук побудки
    sleep(0.1)
    api.DFPlayerPlayFolder(beastDev,playerPins[1],folder_id,wakeup_sound)
    #while not api.GPIORead(beastDev,):
    #    sleep(0.5)
    sleep(10)
    api.SetParameter('frogSongEnd', 1) 
    api.ScenarioStop(6)


def waitCabinetCombination():
    api = EscapeControlAPI()
    sleep(0.2)
    api.LocksWait(8)
    api.ScenarioStop(7)
    api.ScenarioStop(8)
    api.ScenarioStop(8)#TODO: number of additional scenario for Hand light
    api.GPIOSet(mainDev, 20, False)  # Chains lock
    api.GPIOSet(cabinet1Dev,handLightPin,False)

def waitTapestry():
    api = EscapeControlAPI()
    sleep(0.2)
    api.LocksWait(11)
    playTxt("tapestry_solved")

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
        api.GPIOSetAnalog(alchiDev, alchemicalLEDPin, int(abs(math.sin(i / math.pi) * 256)))  # LED-
        sleep(0.01)
    api.GPIOSet(alchiDev, magicBallsLedControlPin, False) #Light Off magic ball
    playTxt("director_reappears")
    sleep(20)

def waitCastle():
    api = EscapeControlAPI()
    sleep(0.2)
    api.LocksWait(14)
    api.ScenarioStop(15)
    api.ScenarioStop(14)
    playTxt("activate_castle_protection")
    api.ScenarioStart(16) #Castle animation
    sleep(25)
    playTxt("outro")

'''Ghost box actions'''
def splashGhostBox():
    for rgb in range(3):
        api.GPIOSetAnalog(ghostDev, rgbPins[rgb], 255)
    sleep(0.02)
    for rgb in range(3):
        api.GPIOSetAnalog(ghostDev, rgbPins[rgb], 0)
    sleep(0.5)
    api.GPIOSetAnalog(ghostDev, rgbPins[0], 66)  # Красный цвет
    api.GPIOSetAnalog(ghostDev, rgbPins[1], 135)  # Зеленый цвет
    api.GPIOSetAnalog(ghostDev, rgbPins[2], 200)  # Синий цвет

def silentHit():  # Еле бьёт
    hit(0.02)  # Мотор не успевает сработать

def silentHit2():  # Средне бьёт
    hit(0.045) # Мотор тут же возвращается обратно

def hit(duration = 0.07):  # Сильно бьёт
    api.GPIOSet(ghostDev, motorPin, True)
    sleep(duration)  # Двойной удар: вверх и вниз из-за долгой паузы
    api.GPIOSet(ghostDev, motorPin, False)

def setFadeLight(device,color,duration):
    color_map = {
        "Yellow": (255, 170, 0),
        "Blue": (135, 66, 200),
        "Off": (0, 0, 0),
    }
    a = 3.0
    steps = duration * 10
    rgb = color_map[color]
    def fade():
        api = EscapeControlAPI()
        for step in range(steps):
            fraction = (math.exp(a * step / steps) - 1) / (math.exp(a) - 1)

            api.GPIOSetAnalog(device, rgbPins[0], int(rgb[1] * fraction)) #GRB Pins
            api.GPIOSetAnalog(device, rgbPins[1], int(rgb[0] * fraction))
            api.GPIOSetAnalog(device, rgbPins[2], int(rgb[2] * fraction))
            sleep(0.1)
            api.Log("sleep:"+str(duration/steps)+" R: "+str(fraction))
    # Запускаем анимацию в отдельном потоке
    thread = threading.Thread(target=fade)
    thread.daemon = True
    thread.start()

api.SetParameter("language", 0) #set English directly
'''First room'''
def room1():
    api.Log("Welcome to the Game")
    # Изначально свет в комнате почти отсутствует. Световой спот горит над шкатулкой с палочками.
    setFadeLight(elfDev,"Off",1)
    setFadeLight(ghostDev,"Off",1)
    api.GPIOSet(mainDev, wandSpot, True)
    api.GPIOSet(mainDev, room1Light, False)
    api.GPIOSet(mainDev, doorRoom1, True) #Lock the players
    api.GPIOSet(mainDev, doorRoom2, True)
    api.ScenarioStart(3)
    api.LocksWait(3)
    # Когда игроки берут палочки, срабатывает электроника и проигрывается аудио.Загорается свет в комнате.
    playTxt("intro")
    setFadeLight(ghostDev, "Blue", 60)
    sleep(64)
    playOst("ambience_1")
    api.GPIOSet(mainDev, room1Light, True)
    api.ScenarioStart(4)
    api.ScenarioStart(48)#sleeped beast
    api.ScenarioStart(55)#silent Toad player
    api.ScenarioStart(8)#TODO: change number of additional scenario for Hand light
    waitBoxWithGhost()
    api.ScenarioStart(5)
    waitKnockingToTheDoor()
    api.ScenarioStart(6)
    waitToadPlayer()
    api.ScenarioStop(48)
    api.ScenarioStart(7)
    waitCabinetCombination()
    # Активация шлюза
    api.ScenarioStart(9)


def room2():
    api.Log("Office opened")
    api.GPIOSet(mainDev, room2Light, True)
    playOst("ambience_2")
    api.LocksWait(9)
    sleep(60)
    playTxt("click_on_books")
    api.ScenarioStart(10)
    api.LocksWait(10)
    api.GPIOSet(mainDev, UVLightLocker, False)  # Lighter Locker
    api.ScenarioStart(11)
    waitTapestry()
    api.ScenarioStart(12)
    api.ScenarioStart(13)
    waitAlchemical()
    api.ScenarioStart(14)
    api.ScenarioStart(15)
    waitCastle()

    api.ScenarioStop(9)
    api.GPIOSet(mainDev, doorRoom1, False)    
    api.GPIOSet(mainDev, doorRoom2, False)
    api.GPIOSet(mainDev, cabinetRoom1magnet, False)
    api.GPIOSet(mainDev, cabinetRoom2magnet, False) 

room1()
room2()