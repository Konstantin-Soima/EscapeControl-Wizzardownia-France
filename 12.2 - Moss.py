from api import EscapeControlAPI
from time import sleep
from time import time
import random 
import math

api = EscapeControlAPI()

cabinet2Dev = 6
RX = 55
TX = 54
DF = 4
volume = 30
folder_id = 4
sound_id = 3
random_time = time()+random.randint(30, 60)
activities = [[11,3],[12,16],[13,4],[14,4],[15,5],[16,7],[17,10]]
api.DFPlayerBegin(cabinet2Dev, DF, RX, TX)
api.DFPlayerVolume(cabinet2Dev, DF, volume)

while True:
    pushed = not api.GPIORead(cabinet2Dev, 9)
    if pushed:
        api.GPIOSet(cabinet2Dev, 11, True) #Light Moss
        api.GPIOSet(cabinet2Dev, 12, True) #Song Moss
        api.DFPlayerPlayFolder(cabinet2Dev, DF, folder_id, sound_id)
        sleep(53.5)
        api.DFPlayerPause(cabinet2Dev, DF)
        api.GPIOSet(cabinet2Dev, 12, False) #Stop Moss
        api.GPIOSet(cabinet2Dev, 11, False)
        random_time = time()+random.randint(10, 60)
    elif time() >= random_time:
        played = random.choice(activities)
        api.DFPlayerPlayFolder(cabinet2Dev, DF, folder_id, played[0])
        for i in range(0,32):
            api.GPIOSetAnalog(cabinet2Dev, 11, int(abs(math.sin(1/math.pi*i)*255)))#Light Moss
            sleep(0.03)
        api.GPIOSet(cabinet2Dev, 12, True) #Song Moss
        while time() < random_time+played[1]-1 and api.GPIORead(cabinet2Dev, 9):
            sleep(0.2)
        api.GPIOSet(cabinet2Dev, 11, False) #Light Moss
        api.GPIOSet(cabinet2Dev, 12, False) #Song Moss
        random_time = time()+random.randint(20, 60)
    sleep(0.5)
