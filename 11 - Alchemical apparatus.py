from api import EscapeControlAPI
from time import sleep
from time import time
from copy import deepcopy

api = EscapeControlAPI()
alchiDev = 7
rfidBall = 6
rfidAlch = [2, 3, 4, 5]
LEDpin = 10
read = ['0000000000000000'] * 4
preread = ['0000000000000000'] * 4
answer = [['0172A7B100390028', '014F3BB100390019', '0111E4B100390015', '01E4E3B1003900DD'],['01E4E3B1003900DD', '0111E4B100390015', '014F3BB100390019', '0172A7B100390028']]
# 01A3B625003E00EB - Peruvian Dust (Yellow)
# 0144859F003E0007 - Pixie wings extract (47/100)
# 01E30B4C000B00EC - Ground Mandrake (2nd grade)
# 0195B09E003E002D 010D347000010080 01E23370000100DC 01D9347000010098 01DC337000010022
# 0148FA6F0001003C - Natural Mana Crystals (middle)
player_sfx = api.connectToPlayer(2)  # Плеер ситуационных звуков
player_sfx.volume(300)
player_sfx.setLoop(False)

def playSfx(sound):
    player_sfx.playSound(sound + ".mp3")
playSfx("click_on_books_trigger")
sleep(0.05)
api.GPIOSet(alchiDev, 14, True) # RFID -
api.GPIOSet(alchiDev, LEDpin, True)  # LED-
count = 0
haveError = False
while True:
    for i in range(4):
        read[i] = api.RFIDGetCard(alchiDev, rfidAlch[i])
        if 'FFFFF' in read[i]:
            haveError = True
    '''    if read != preread and not haveError:
        api.Log(str(read))
    '''

    if read in answer:
        api.Log("Correct: " + str(read))
        break
    count = +1
    preread = deepcopy(read)
    if count > 180 or haveError:
        api.GPIOSet(alchiDev, 14, False)
        sleep(1)
        count = 0
        api.GPIOSet(alchiDev, 14, True)
        haveError = False
    else:
        sleep(0.3)
api.LocksUnlock(13)
