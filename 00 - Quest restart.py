from api import EscapeControlAPI
from time import sleep
from time import time

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
room1_light = 10
room2_light = 12

'''MAGNET LOCKS'''
doorRoom1 = 18 #Eter
doorRoom2 = 23 #Exit
elfenDoorMagnet = 19
magicBallsMagnet = 22
cabinetRoom2locker =21
chainsMagnet = 20
cabinetRoom1magnet = 17
cabinetRoom2magnet = 16

'''LEDs'''
RgbPins = [10, 11, 12]
handLight = 10
alchemicalLED = 10
magicBallLED = 12
cabinetUVControlPin = 11
mossLED = 11
ws = [62, 66, 65, 64, 63]

'''PINS'''
motorPin = 56 #Spirit Box solenoid
mossPin = 10
magicBallRFID = 11
alchemicalRFID = 14
'''AUDIO'''
gamePlayersCount = 3
dfrxtx = [
    [ghostDev, 1, 58,57],
    [beastDev, 1, 9, 8],
    [beastDev, 4, 6, 7],
    [cabinet2Dev, 4, 55, 54],
    [treeDev, 5, 61, 60]
]  # Device,DFNumber,RX,TX
#Open/Exit doors opened
api.GPIOSet(mainDev, doorRoom1, False)  # Enter
api.GPIOSet(mainDev, doorRoom2, False)  # Exit
api.GPIOSet(mainDev, cabinetRoom2magnet, False)  # Cabinet Doors Lock (shop side)
api.GPIOSet(mainDev, cabinetRoom1magnet, True)  # Cabinet Doors Lock (office side)
api.GPIOSet(mainDev, elfenDoorMagnet, True)  # Elf's door lock
api.GPIOSet(mainDev, chainsMagnet, True)  # Chains lock
api.GPIOSet(mainDev, cabinetRoom2locker, True)  # Lighter Locker
api.GPIOSet(mainDev, magicBallsMagnet, True)  # Magic balls
#All lamp on
api.GPIOSet(mainDev, wandSpot, True) # Wand
api.GPIOSet(mainDev, room1_light, True) # Room1
api.GPIOSet(mainDev, room2_light, True) # Room2
#All leds off
api.GPIOSet(cabinet1Dev,cabinetUVControlPin,False) # Doors UV
api.GPIOSet(cabinet1Dev,handLight, False) 
api.GPIOSet(alchiDev, alchemicalLED,False) # Alchimic led
api.GPIOSet(alchiDev, magicBallLED,False) # Ball led
api.GPIOSet(ghostDev, RgbPins[0], False) # Ghost RGB
api.GPIOSet(ghostDev, RgbPins[1], False) # Ghost RGB
api.GPIOSet(ghostDev, RgbPins[2], False) # Ghost RGB
api.GPIOSet(elfDev, RgbPins[0], False) # Elf RGB
api.GPIOSet(elfDev, RgbPins[1], False) # Elf RGB
api.GPIOSet(elfDev, RgbPins[2], False) # Elf RGB

api.WS2812Init(castleDev, 1, ws[0], 15)  # Microhome
api.WS2812Init(castleDev, 2, ws[1], 70) # 18 на башню
api.WS2812Init(castleDev, 3, ws[2], 107)  # Pin panel по часовой
api.WS2812Init(castleDev, 4, ws[3], 95)  # Castle 
api.WS2812Init(castleDev, 5, ws[4], 95)  # Castle Big Tower

for j in range(1,6):
    for i in range (0,107):
        api.WS2812Set(castleDev, j, i, 0, 0, 0)
    api.WS2812Sync(castleDev, j)

# Stop playing music
for i in range(1, gamePlayersCount + 1):
    player = api.connectToPlayer(i)
    player.volume(280)
    player.setLoop(False)
    player.stop()

volume = 20
for rxtx in dfrxtx:
    api.DFPlayerBegin(rxtx[0], rxtx[1], rxtx[2], rxtx[3])
    api.DFPlayerVolume(rxtx[0], rxtx[1], volume)
    sleep(0.1)
    api.DFPlayerPlayFolder(rxtx[0], rxtx[1],rxtx[1],1)
    sleep(5)
    api.DFPlayerPause(rxtx[0], rxtx[1])
    sleep(0.1)
    api.DFPlayerStop(rxtx[0], rxtx[1])
    sleep(0.1)
    api.DFPlayerEnd(rxtx[0], rxtx[1])

api.GPIOSet(cabinet2Dev, 12, False)  # Stop Moss

api.GPIOSet(alchiDev, 11, False) #RFID Off
api.GPIOSet(alchiDev, 14, False) #RFID Off