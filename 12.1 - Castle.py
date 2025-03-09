import colorsys
from api import EscapeControlAPI
from time import sleep
from time import time
from threading import Thread
import random 

api = EscapeControlAPI()

castleDev = 9
ws = [62, 66, 65, 64, 63]
NE = 4 # - yellow dragon NE
NW = 55 # - red tree NW
SE = 2 # - green crack SE
SW = 57 # - blue eggs SW
NEseq = [[6,58,61,60],[60,61,58,6]]
NWseq = [[58,7,56,5],[5,56,7,58]]
SEseq = [[9,56,54,8],[8,54,56,9]]
SWseq = [[3,61,59,9],[9,59,61,3]]
NEend, SEend, NWend, SWend = False, False, False, False
towers = [NE,NW,SW,SE]
towersRange = {
    NE: range(18,34),
    NW: range(0,17),
    SW: range(55,68),
    SE: range(36,53)
}
towersColour = {
    NE: [128, 255, 0],
    NW: [0, 255, 0],
    SW: [0, 0, 255],
    SE: [255, 0, 0]
}
active = 0
activeColour = [0,0,0]
pins = [3,5,6,7,8,9,54,56,58,59,60,61]
pinsLedIndex = [
    [3,[18,19,20,21]],
    [5,[38,39,40,41]],
    [6,[4,5,6,7]],
    [7,[11,12,13,14]],
    [8,[31,32,33,34]],
    [9,[91,92,93,94]],
    [54,[98,99,100,101]],
    [56,[58,59,60]],
    [58,[71,72,73,74]],
    [59,[64,65,66,67]],
    [60,[44,45,46,47]],
    [61,[84,85,86,87]]
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
api.WS2812Init(castleDev, 2, ws[1], 70) # 18 на башню
api.WS2812Init(castleDev, 3, ws[2], 107)  # Pin panel по часовой
api.WS2812Init(castleDev, 4, ws[3], 95)  # Castle 
api.WS2812Init(castleDev, 5, ws[4], 100)  # Castle Big Tower



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
for i in range(0, 100):
    api.WS2812Set(castleDev, 5, i, 255,128, 24)
api.WS2812Sync(castleDev, 5)

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

TestMode = False
while TestMode: #Помогает в поиске герконов и положения ленты относительно их
    pos = 0
    act = 0
    new_activeColour = colorsys.hsv_to_rgb(random.uniform(0, 1),1,1)
    l = [2,3,4,5,6,7,8,9,54,55,56,57,58,59,60,61]
    r = api.GPIOReadList(castleDev,l)
    while sum(r) == 15:
        act = r.index(0)
        #not api.GPIORead(castleDev, 2):
        pos +=1
        api.WS2812Set(castleDev, 3, pos, int(new_activeColour[1]*255), int(new_activeColour[0]*255), int(new_activeColour[2]*255)) #GRB LED
        api.WS2812Sync(castleDev, 3)
        sleep(0.5)
        r = api.GPIOReadList(castleDev,l)
    if pos > 0:
        api.Log("Pin: " + str(l[act])+ " LED index: "+ str(pos))
    for i in range(107):
        api.WS2812Set(castleDev, 3, i, 0,0,0)
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
