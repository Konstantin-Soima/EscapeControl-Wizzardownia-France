import colorsys
from api import EscapeControlAPI
from time import sleep
from time import time
from threading import Thread
import random 


api = EscapeControlAPI()

castleDev = 9
ws = [58, 60, 61, 59]
NE = 64 # 54 - yellow dragon NE
NW = 56 # 58 - red tree NW
SE = 4 # 66 - green crack SE
SW = 8 # 62 - blue eggs SW
NEseq = [[3,9,7,57],[57,7,9,3]]
NWseq = [[9,2,55,62],[62,55,2,9]]
SEseq = [[6,55,5,63],[63,5,55,6]]
SWseq = [[65,7,54,6],[6,54,7,65]]
NEend, SEend, NWend, SWend = False, False, False, False
towers = [NE,NW,SW,SE]
towersRange = {
    NE: range(8,15),
    NW: range(0,8),
    SW: range(26,40),
    SE: range(16,25)
}
towersColour = {
    NE: [128, 255, 0],
    NW: [0, 255, 0],
    SW: [0, 0, 255],
    SE: [255, 0, 0]
}
active = 0
activeColour = [0,0,0]
player_sfx = api.connectToPlayer(2)  # Плеер ситуационных звуков
player_sfx.volume(280)
player_sfx.setLoop(False)

def playSfx(sound):
    player_sfx.playSound(sound + ".mp3")

api.WS2812Init(castleDev, 1, ws[0], 15)  # Microhome
api.WS2812Init(castleDev, 2, ws[1], 41) # 10 на башню
api.WS2812Init(castleDev, 3, ws[2], 107)  # Pin panel по часовой
api.WS2812Init(castleDev, 4, ws[3], 95)  # Castle 



#Set Castle based colour
for i in range(0, 15):
    api.WS2812Set(castleDev, 1, i, 60,30, 10)
api.WS2812Sync(castleDev, 1)
for i in range(0, 95):
    api.WS2812Set(castleDev, 4, i, 255,128, 24)
api.WS2812Sync(castleDev, 4)

for tower in towers: #set tower colours
    for i in towersRange[tower]:
        api.WS2812Set(castleDev, 2, i,towersColour[tower][1],towersColour[tower][0],towersColour[tower][2])
    api.WS2812Sync(castleDev, 2)
    
def circleColor(startPos,R,G,B): #circle activate Animation
    if active > 0:
        return
    for i in range(0,55):
        rightI = startPos + i
        if rightI > 107:
            rightI = rightI - 107
        api.WS2812Set(castleDev, 3, rightI, R, G, B)
        leftI = startPos - i
        if leftI < 0:
            leftI = 108 - abs(leftI)
        api.WS2812Set(castleDev, 3, leftI, R, G, B)
        api.WS2812Sync(castleDev, 3)

def offCircle():
    for i in range(0,107):
        api.WS2812Set(castleDev, 3, i, 0, 0, 0)
    api.WS2812Sync(castleDev, 3)

#FINAL ANIMATION
def castleMagicBatle():
    s = 1
    h = 0.12
    colo = colorsys.hsv_to_rgb(h,abs(s),255)
    for i in range(0,15):
        api.WS2812Set(castleDev, 1, i, int(colo[0]), int(colo[1]), int(colo[2]))
    api.WS2812Sync(castleDev, 1)
    for i in range(0,95):
        api.WS2812Set(castleDev, 4, i, int(colo[0]), int(colo[1]), int(colo[2]))
    api.WS2812Sync(castleDev, 4)
    while True:
        start = random.randint(5, 70)
        s = -1
        h = 0.12 if s >= 0 else 0.70
        colo = colorsys.hsv_to_rgb(h,abs(s),255)
        api.WS2812Set(castleDev, 4, start, int(colo[0]), int(colo[1]), int(colo[2]))
        api.WS2812Sync(castleDev, 4)
       
        for i in range(1,5): 
            s += 0.15
            h = 0.12 if s >= 0 else 0.70
            sleep(0.07)
            colo = colorsys.hsv_to_rgb(h,abs(s),255)
            api.WS2812Set(castleDev, 4, start+(i), int(colo[0]), int(colo[1]), int(colo[2]))
            api.WS2812Set(castleDev, 4, start-(i), int(colo[0]), int(colo[1]), int(colo[2]))
            api.WS2812Sync(castleDev, 4)
            if start < 15:
                api.WS2812Set(castleDev, 1, start+(i), int(colo[0]), int(colo[1]), int(colo[2]))
                api.WS2812Set(castleDev, 1, start-(i), int(colo[0]), int(colo[1]), int(colo[2]))
                api.WS2812Sync(castleDev, 1)
        s = 1
        for i in range(5,0,-1):
            h = 0.12 if s >= 0 else 0.70
            sleep(0.07)
            colo = colorsys.hsv_to_rgb(h,abs(s),255)
            api.WS2812Set(castleDev, 4, start+(i), int(colo[0]), int(colo[1]), int(colo[2]))
            api.WS2812Set(castleDev, 4, start-(i), int(colo[0]), int(colo[1]), int(colo[2]))
            api.WS2812Sync(castleDev, 4)
            if start < 15:
                api.WS2812Set(castleDev, 1, start+(i), int(colo[0]), int(colo[1]), int(colo[2]))
                api.WS2812Set(castleDev, 1, start-(i), int(colo[0]), int(colo[1]), int(colo[2]))
                api.WS2812Sync(castleDev, 1)

def magicCircle():
    enterAngle = 34
    exitAngle = 87  
    for i in range(0,107):
        api.WS2812Set(castleDev, 3, i, 20,50,150)
    while True:
        
        for i in range(0,5):
            colo = colorsys.hsv_to_rgb(1/5*i,1,255)
            api.WS2812Set(castleDev, 3, i+enterAngle, int(colo[0]), int(colo[1]), int(colo[2]))
            api.WS2812Set(castleDev, 3, i+exitAngle, int(colo[0]), int(colo[1]), int(colo[2]))
            api.WS2812Sync(castleDev, 3)
            sleep(0.03)
        rVector = int(random.randint(-1, 1))
        if rVector == 1:
            if exitAngle > 0:
                api.WS2812Set(castleDev, 3, exitAngle-1, 20,50,150)
            if enterAngle > 0:
                api.WS2812Set(castleDev, 3, enterAngle-1, 20,50,150)
        else:
            api.WS2812Set(castleDev, 3, exitAngle+5, 20,50,150)
            api.WS2812Set(castleDev, 3, enterAngle+5, 20,50,150)
        api.WS2812Sync(castleDev, 3)
        api.WS2812Set(castleDev, 3, enterAngle + int(random.randint(0, 5)), 20,50,150)
        api.WS2812Sync(castleDev, 3)
        api.WS2812Set(castleDev, 3, exitAngle + int(random.randint(0, 5)), 20,50,150)
        api.WS2812Sync(castleDev, 3)
        sleep(0.05)
        enterAngle = (107 + enterAngle + rVector) % 107
        exitAngle = (107 + exitAngle + rVector) % 107


tread = Thread(target=magicCircle)
tread.start()
castleMagicBatle()
tread.join()