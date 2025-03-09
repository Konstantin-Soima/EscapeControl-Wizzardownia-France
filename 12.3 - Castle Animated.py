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
player_sfx = api.connectToPlayer(2)  # Плеер ситуационных звуков
player_sfx.volume(280)
player_sfx.setLoop(False)

def playSfx(sound):
    player_sfx.playSound(sound + ".mp3")

api.WS2812Init(castleDev, 1, ws[0], 15)  # Microhome
api.WS2812Init(castleDev, 2, ws[1], 70) # 18 на башню
api.WS2812Init(castleDev, 3, ws[2], 107)  # Pin panel по часовой
api.WS2812Init(castleDev, 4, ws[3], 95)  # Castle 
api.WS2812Init(castleDev, 5, ws[4], 100)  # Castle Big Tower

start = time()


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
    while time()-start < 60:
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


#tread = Thread(target=magicCircle)
def magicAttack():
    while time()-start < 60:
        # Фаза 1: "Атака" – случайные вспышки в оттенках фиолетового, расширенные в 2 раза.
        attack_duration = 5.0  # время атаки в секундах
        start_attack = time()
        while time() - start_attack < attack_duration:
            side = random.choice(["left", "right"])
            # Выбираем позицию ближе к выбранной стороне
            if side == "left":
                pos = random.randint(0, 10)
            else:
                pos = random.randint(97, 106)
            # Для более широкой атаки зажигаем 3 соседних светодиода (pos-1, pos, pos+1)
            # Проходим по градации оттенков фиолетового от тёмного к яркому.
            for intensity in range(64, 256, 25):  # оттенки от темного до яркого
                color = (intensity, 0, intensity)  # оттенок фиолетового (одинаковые R и B)
                for offset in [-1, 0, 1]:
                    p = pos + offset
                    if 0 <= p < 107:
                        api.WS2812Set(castleDev, 3, p, *color)
                api.WS2812Sync(castleDev, 3)
                sleep(0.005)
            # Гасим область атаки
            for offset in [-1, 0, 1]:
                p = pos + offset
                if 0 <= p < 107:
                    api.WS2812Set(castleDev, 3, p, 0, 0, 0)
            api.WS2812Sync(castleDev, 3)
            sleep(0.03)
        
        # Фаза 2: "Ответ замка" – волна магического отблеска, исходящая из центра, с синими переливами.
        center = 107 // 2  # Центр ленты
        # Выполняем 3 волны репульсии
        for wave in range(3):
            for offset in range(center + 1):
                factor = 1 - offset / center  # чем дальше от центра, тем меньше яркость
                # Вычисляем градиентный синий цвет:
                # Здесь базовый синий (яркость ~255) плавно переходит к более "холодному" оттенку с добавлением зеленого.
                color = (0, int(150 * factor), int(255 * factor))
                left_pos = center - offset
                right_pos = center + offset
                if left_pos >= 0:
                    api.WS2812Set(castleDev, 3, left_pos, *color)
                if right_pos < 107:
                    api.WS2812Set(castleDev, 3, right_pos, *color)
                api.WS2812Sync(castleDev, 3)
                sleep(0.01)
            # Затухание волны: гасим всю ленту
            for pos in range(107):
                api.WS2812Set(castleDev, 3, pos, 0, 0, 0)
            api.WS2812Sync(castleDev, 3)
            sleep(0.2)

# В финальной части заменяем вызов magicCircle на наш новый magicAttack:
tread = Thread(target=magicAttack)
tread.start()
castleMagicBatle()
tread.join()