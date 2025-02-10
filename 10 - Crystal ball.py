from api import EscapeControlAPI
from time import sleep
from time import time
from threading import Thread
import math

api = EscapeControlAPI()

work = True
mainDev = 1
alchiDev = 7
rfidBall = 6
api.GPIOSet(alchiDev, 11, True)  # RFID-
api.GPIOSet(alchiDev, 12, True)  # LED-
api.GPIOSet(mainDev, 22, False)  # Magic balls door
lang = api.GetParameter("language")
balls = ['01A1819F003E00DA', '0153FA6F0001009F', '01B4769F003E009D', '0110347000010091']
#                                                                     010E164B000B0099
hint = ['manifestation_of_predictions_1_peruvian_dust', 'manifestation_of_predictions_2_pixie_wings', 'manifestation_of_predictions_3_mana_crystals', 'manifestation_of_predictions_4_ground_mandrake']
if lang == 1:
    hint = ['Manifestation_of_predictions_1_peruvian_dust_DE', 'Manifestation_of_predictions_2_pixie_wings_DE', 'Manifestation_of_predictions_3_mana_crystals_DE', 'Manifestation_of_predictions_4_ground_mandrake_DE']
player_sfx = api.connectToPlayer(2)  # Плеер ситуационных звуков
player_sfx.volume(300)
player_sfx.setLoop(False)
played = '0000000000000000'
pausedCnt = 0
resetCnt = 0

def playSfx(sound):
    player_sfx.playSound(sound + ".mp3")


def waitAlchimy():
    api.LocksWait(13)
    global work
    work = False
    #player_sfx.stop()


tread = Thread(target=waitAlchimy)
tread.start()
while work:
    whatIs = api.RFIDGetCard(alchiDev, rfidBall)
    if whatIs != '0000000000000000':
        pausedCnt = 0
        # api.GPIOSet(alchiDev, 14, False)
        if whatIs in balls and played != whatIs:
            ballId = balls.index(whatIs)
            player_sfx.volume(300)
            sleep(0.1)
            playSfx(hint[ballId])
            played = whatIs
            api.Log("Paly " + hint[ballId] + " for: " + str(whatIs))
        elif whatIs not in balls:
            api.GPIOSet(alchiDev, 11, False)
            api.Log("Error: "+str(whatIs))
            sleep(0.3)
            api.GPIOSet(alchiDev, 11, True)
            resetCnt = 0
        continue
    else:
        pausedCnt+=1
        if pausedCnt >= 3:
            pausedCnt = 0
            played = '0000000000000000'
            player_sfx.stop()
    if resetCnt > 100:
        api.GPIOSet(alchiDev, 11, False)
        api.Log("Reset with: "+str(whatIs))
        sleep(0.3)
        api.GPIOSet(alchiDev, 11, True)
        resetCnt = 0
        continue
    sleep(0.1)
    resetCnt += 1
api.GPIOSet(alchiDev, 11, False)
tread.join()
