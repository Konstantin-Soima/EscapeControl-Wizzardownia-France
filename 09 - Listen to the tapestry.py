from api import EscapeControlAPI
from time import sleep, time
from copy import deepcopy

api = EscapeControlAPI()

mainDev = 1
treeDev = 8

treePins = [55, 59, 56, 62, 57, 58, 9, 5, 8, 7, 2, 6, 3, 4]
treeSounds = [2, 21, 13, 12, 9, 5, 4, 7, 8, 14, 11, 6, 3, 1]  # local mp3 player with amplifier

lang = api.GetParameter("language")
if lang == 1:
    treeSounds = [202, 221, 13, 12, 209, 205, 204, 207, 208, 14, 211, 206, 203, 201]

answer = [13, 12, 6, 5, 7]  # 59 58 8 7 9 - correct pins
stack = [None] * 5

playerId = 5
folderId = 5
firstHint = True
rxPin = 61
txPin = 60
volume = 26

api.DFPlayerBegin(treeDev, playerId, rxPin, txPin)
sleep(0.2)
api.DFPlayerVolume(treeDev, playerId, volume)
api.GPIOSet(mainDev, 21, False)  # Lighter Locker

''' 
    Функция для воспроизведения звука 
'''
def playVoice(n):
    api.DFPlayerStop(treeDev, playerId)
    api.DFPlayerPlayFolder(treeDev, playerId, folderId, treeSounds[n])

''' 
    Функция для добавления элементов в стек 
'''
def stackAppend(n):
    nonCount = stack.count(None)
    if nonCount > 0:
        stack[5 - nonCount] = n
    else:
        for i in range(4):
            stack[i] = stack[i + 1]
        stack[4] = n

prev = api.GPIOReadList(treeDev, treePins)

while True:
    read = api.GPIOReadList(treeDev, treePins)
    
    if 14 > sum(read) >= 10:
        diff = [x - y for x, y in zip(prev, read)]
        
        if sum(diff) == 1:
            art = diff.index(1)
            playVoice(art)
            stackAppend(art)
            api.Log('you put: ' + str(art))
            
            if firstHint and art == 1:
                firstHint = False
                treeSounds[1] = 22
                
                if lang == 1:
                    treeSounds[1] = 222  # TODO: change to short

    if stack == answer:
        sleep(9)
        break
    
    prev = deepcopy(read)
    sleep(0.2)

api.LocksUnlock(11)