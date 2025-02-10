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
pins = [2,3,5,6,7,9,54,55,57,62,63,65]
pinsLedIndex = [
    [2,[0,1,2,3]],
    [3,[100,101,102,103]],
    [5,[87,88,89]],
    [6,[80,81,82,83]],
    [7,[74,75,76]],
    [9,[60,61,62,63]],
    [54,[54,55,56]],
    [55,[47,48,49]],
    [57,[33,34,35,36]],
    [62,[27,28,29,30]],
    [63,[21,22,23]],
    [65,[7,8,9,10]]
]
stack = [None]*4
player_sfx = api.connectToPlayer(2)  # Плеер ситуационных звуков
player_sfx.volume(280)
player_sfx.setLoop(False)

def playSfx(sound):
    player_sfx.playSound(sound + ".mp3")

def stackAppend(n):
    non = stack.count(None)
    if non > 0:
        stack[4 - non] = n
    else:
        stack[:-1] = stack[1:]
        stack[3] = n

api.WS2812Init(castleDev, 1, ws[0], 15)  # Microhome
api.WS2812Init(castleDev, 2, ws[1], 41) # 10 на башню
api.WS2812Init(castleDev, 3, ws[2], 107)  # Pin panel по часовой
api.WS2812Init(castleDev, 4, ws[3], 95)  # Castle 


for i in range(0, 40): #Towers Light OFF
    api.WS2812Set(castleDev, 2, i, 0, 0, 0)
api.WS2812Sync(castleDev, 2)
#Set Castle based colour
for i in range(0, 15):
    api.WS2812Set(castleDev, 1, i, 60,30, 10)
api.WS2812Sync(castleDev, 1)
for i in range(0, 95):
    api.WS2812Set(castleDev, 4, i, 255,128, 24)
api.WS2812Sync(castleDev, 4)

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

prev = api.GPIOReadList(castleDev, pins)
while True:
    readTowers = api.GPIOReadList(castleDev, towers)
    if sum(readTowers) == 3: #if one (and only one) of towers pushed 
        pushed = towers[readTowers.index(0)]
        #Push tower
        if active <1:
            playSfx("wand_touches_castle_tower_nods")
            start_WS_pos = 0
            if pushed == SW:
                start_WS_pos = 68
            elif pushed == SE:
                start_WS_pos = 95
            elif pushed == NE:
                start_WS_pos = 15
            elif pushed == NW:
                start_WS_pos = 41
            activeColour = towersColour[pushed]
            for i in towersRange[pushed]:
                api.WS2812Set(castleDev, 2, i, activeColour[1], activeColour[0], activeColour[2])
            api.WS2812Sync(castleDev, 2)
            circleColor(start_WS_pos,activeColour[1], activeColour[0], activeColour[2])
            active = pushed
        #Read Pins
        readPins = api.GPIOReadList(castleDev, pins)
        diff = [x - y for x, y in zip(prev, readPins)]
        prev = readPins
        if sum(diff) == 1:
            runeNum = diff.index(1)
            playSfx("wand_touches_castle_nods")
            stackAppend(pins[runeNum])
            api.Log('you put: ' + str(pins[runeNum]))
            for btns in pinsLedIndex: #touch rune animation
                if pins[runeNum] == btns[0]:
                    hsv_code = colorsys.rgb_to_hsv(activeColour[0], activeColour[1], activeColour[2])
                    hsv_code = list(hsv_code)
                    hsv_code[0] += 0.1
                    new_activeColour = colorsys.hsv_to_rgb(hsv_code[0],hsv_code[1],hsv_code[2])
                    for pn in btns[1]:
                        api.WS2812Set(castleDev, 3, pn, int(new_activeColour[1]), int(new_activeColour[0]), int(new_activeColour[2])) #GRB LED
                api.WS2812Sync(castleDev, 3)
        elif sum(diff) == -1:
            runeNum = diff.index(-1)
            for btns in pinsLedIndex:
                if pins[runeNum] == btns[0]:
                    for pn in btns[1]:
                        api.WS2812Set(castleDev, 3, pn, activeColour[1], activeColour[0], activeColour[2]) #GRB LED
                api.WS2812Sync(castleDev, 3)
        if pushed == SE and (stack == SEseq[0] or stack == SEseq[1]):
            SEend = True
            playSfx("tower_activation")
            for i in range(-128,129):
                j=128-abs(i)
                #api.GPIOSetAnalog(castleDev, 12, j) create animation here
            api.Log(stack)
            stack = [None]*4
        if pushed == NE and (stack == NEseq[0] or stack == NEseq[1]):
            NEend = True
            playSfx("tower_activation")
            for i in range(-128,129):
                j=128-abs(i)
                #api.GPIOSetAnalog(castleDev, 12, j) create animation here
            api.Log(stack)
            stack = [None]*4
        if pushed == SW and (stack == SWseq[0] or stack == SWseq[1]):
            SWend = True
            playSfx("tower_activation")
            for i in range(-128,129):
                j=128-abs(i)
                #api.GPIOSetAnalog(castleDev, 12, j) create animation here
            api.Log(stack)
            stack = [None]*4
        if pushed == NW and (stack == NWseq[0] or stack == NWseq[1]):
            NWend = True
            playSfx("tower_activation")
            for i in range(-128,129):
                j=128-abs(i)
                #api.GPIOSetAnalog(castleDev, 12, j) create animation here
            api.Log(stack)
            stack = [None]*4
    else:

        if not SWend:
            for i in towersRange[SW]:
                api.WS2812Set(castleDev, 2, i, 0, 0, 0)
        if not SEend:
            for i in towersRange[SE]:
                api.WS2812Set(castleDev, 2, i, 0, 0, 0)
        if not NEend:
            for i in towersRange[NE]:
                api.WS2812Set(castleDev, 2, i, 0, 0, 0)
        if not NWend:
            for i in towersRange[NW]:
                api.WS2812Set(castleDev, 2, i, 0, 0, 0)
        api.WS2812Sync(castleDev, 2)
        for i in range(0,107):
            api.WS2812Set(castleDev, 3, i, 0, 0, 0)
        api.WS2812Sync(castleDev, 3)
        active = 0
        stack = [None]*4
    if (SEend and NEend and NWend and SWend):
        sleep(2)
        break
    sleep(0.2)

api.LocksUnlock(14)
