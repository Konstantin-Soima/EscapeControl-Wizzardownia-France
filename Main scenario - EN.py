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
wandSpot = 45
room1_light = 44
room2_light = 46
'''MAGNET LOCKS'''
doorLock = 16
maglock1 = 17
maglock2 = 18

'''Initialization of players'''
player_ost = api.connectToPlayer(1)  # Плеер фоновых саундтреков
player_sfx = api.connectToPlayer(2)  # Плеер ситуационных звуков
player_txt = api.connectToPlayer(3)  # Плеер ситуационных звуков
player_ost.volume(210) #260
player_sfx.volume(225) #280
player_txt.volume(225) #280
player_sfx.setLoop(False)
player_ost.setLoop(False)
player_txt.setLoop(False)

api.GPIOSet(mainDev,maglock1,True)
api.GPIOSet(mainDev,maglock2,True)


def playOst(sound):
    player_ost.playSound(sound + ".mp3")


def playSfx(sound):
    player_sfx.playSound(sound + ".mp3")


def playTxt(sound):
    player_txt.playSound(sound + ".mp3")


def room1():
    api.Log("Welcome to the Game")
    # Изначально свет в комнате почти отсутствует. Световой спот горит над шкатулкой с палочками.
    api.GPIOSet(mainDev, wandSpot, True)
    api.GPIOSet(mainDev, room1_light, False)
    api.GPIOSet(mainDev, doorLock, True)
    api.ScenarioStart(3)
    api.LocksWait(3)
    # Когда игроки берут палочки, срабатывает электроника и проигрывается аудио.Загорается свет в комнате.
    playTxt("intro")
    sleep(64)
    playOst("ambience_1")
    api.GPIOSet(mainDev, room1_light, True)
    # Все загадки активны со входа
    api.ScenarioStart(4)
    api.ScenarioStart(5)
    api.ScenarioStart(7)
    api.ScenarioStart(8)
    api.LocksWait(4)
    playTxt("heed_the_ghost_s_message")
    api.ScenarioStop(7)
    player_ost.volume(200)
    sleep(4) #Delay for stop scenario when skiped
    api.ScenarioStop(4)
    api.ScenarioStart(6)
    api.LocksWait(5)
    api.ScenarioStart(7)
    player_ost.volume(220)
    api.GPIOSet(mainDev, 19, False) #Elf's door lock
    sleep(1)
    api.ScenarioStop(5)

    api.LocksWait(6)
    api.SetParameter('frogSongEnd', 1)
    api.LocksWait(8)
    api.ScenarioStop(7)
    # Активация шлюза
    api.ScenarioStart(9)


def room2():
    api.Log("Office opened")
    api.GPIOSet(mainDev, room2_light, True)
    playOst("ambience_2")
    api.LocksWait(9)
    sleep(60)
    playTxt("click_on_books")
    api.ScenarioStart(10)
    api.LocksWait(10)
    api.GPIOSet(mainDev, 21, False)  # Lighter Locker
    api.ScenarioStart(11)
    api.LocksWait(11)
    playTxt("tapestry_solved")
    api.ScenarioStart(12)
    api.ScenarioStart(13)
    api.LocksWait(13)
    playTxt("director_reappears")
    sleep(20)
    api.ScenarioStart(14)
    api.ScenarioStart(15)
    api.LocksWait(14)
    playTxt("activate_castle_protection")
    sleep(25)
    playTxt("outro")
    api.ScenarioStop(9)
    api.GPIOSet(mainDev, doorLock, False)    
    api.GPIOSet(mainDev, maglock1, False)
    api.GPIOSet(mainDev, maglock2, False)

room1()
room2()