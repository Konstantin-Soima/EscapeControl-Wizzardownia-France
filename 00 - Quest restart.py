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
wandSpot = 44
room1_light = 45
'''AUDIO'''
gamePlayersCount = 3
dfrxtx = [
    [2, 1, 57,58],
    [3, 3, 7, 8],
    [3, 2, 9, 54],
    [6, 4, 55, 54],
    [8, 5, 60, 61]
]  # Device,DFNumber,RX,TX

api.GPIOSet(mainDev, 17, False)  # Cabinet Doors Lock (shop side)
api.GPIOSet(mainDev, 18, False)  # Cabinet Doors Lock (office side)
api.GPIOSet(mainDev, 19, True)  # Elf's door lock
api.GPIOSet(mainDev, 20, True)  # Chains lock
api.GPIOSet(mainDev, 21, True)  # Lighter Locker
api.GPIOSet(mainDev, 22, True)  # Magic balls

api.GPIOSet(cabinet1Dev,12,False) # Doors UV
api.GPIOSet(alchiDev, 12,False) # Alchimic led

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

api.WS2812Init(castleDev, 1, 6, 15)  # Microhome
api.WS2812Init(castleDev, 2, 7, 41) # 10 на башню
api.WS2812Init(castleDev, 3, 8, 107)  # Pin panel против часовой
api.WS2812Init(castleDev, 4, 9, 75)  # Castle

for j in range(1,5):
    for i in range (0,107):
        api.WS2812Set(castleDev, j, i, 0, 0, 0)
    api.WS2812Sync(castleDev, j)

api.GPIOSet(alchiDev, 11, False) #RFID Off
api.GPIOSet(alchiDev, 14, False) #RFID Off