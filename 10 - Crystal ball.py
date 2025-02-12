from api import EscapeControlAPI
from time import sleep, time
from threading import Thread
import math

api = EscapeControlAPI()

work = True
mainDev = 1
alchiDev = 7
rfidBall = 6

rfidControlPin = 12         # Пин для управления RFID (ON/OFF)
magicBallsLedControlPin = 11          # Пин для управления LED
magicBallsDoorPin = 22      # Пин для двери с магическими шарами

api.GPIOSet(alchiDev, rfidControlPin, True)
api.GPIOSet(alchiDev, magicBallsLedControlPin, True)
api.GPIOSet(mainDev, magicBallsDoorPin, False) 

lang = api.GetParameter("language")
balls = ['014DE4B100390046', '015780B1003900DC', '01293CB100390039', '01213BB1003900C9']
hint = ['manifestation_of_predictions_1_peruvian_dust',
        'manifestation_of_predictions_2_pixie_wings',
        'manifestation_of_predictions_3_mana_crystals_',
        'manifestation_of_predictions_4_ground_mandrake_']
if lang == 1:
    hint = ['Manifestation_of_predictions_1_peruvian_dust_FR',
            'Manifestation_of_predictions_2_pixie_wings_FR',
            'Manifestation_of_predictions_3_mana_crystals_FR',
            'Manifestation_of_predictions_4_ground_mandrake_FR']

playerSfx = api.connectToPlayer(2)  # Плеер ситуационных звуков
playerSfx.volume(300)
playerSfx.setLoop(False)

played = '0000000000000000'
pausedCnt = 0
resetCnt = 0

''' 
    Функция для воспроизведения звукового эффекта 
'''
def playSfx(sound):
    playerSfx.playSound(sound + ".mp3")

api.GPIOSet(alchiDev, rfidControlPin, True)  # RFID-
while work:
    whatIs = api.RFIDGetCard(alchiDev, rfidBall)
    if whatIs != '0000000000000000':
        pausedCnt = 0
        # api.GPIOSet(alchiDev, 14, False)
        if whatIs in balls and played != whatIs:
            api.GPIOSet(alchiDev, magicBallsLedControlPin, False)
            ballId = balls.index(whatIs)
            playerSfx.volume(300)
            sleep(0.1)
            playSfx(hint[ballId])
            played = whatIs
            api.Log("Paly " + hint[ballId] + " for: " + str(whatIs))
            api.GPIOSet(alchiDev, magicBallsLedControlPin, True)
        elif whatIs not in balls:
            api.GPIOSet(alchiDev, rfidControlPin, False)
            api.Log("Error: " + str(whatIs))
            sleep(0.3)
            api.GPIOSet(alchiDev, rfidControlPin, True)
            resetCnt = 0
        continue
    else:
        pausedCnt += 1
        if pausedCnt >= 3:
            pausedCnt = 0
            played = '0000000000000000'
            playerSfx.stop()
    if resetCnt > 100:
        api.GPIOSet(alchiDev, rfidControlPin, False)
        api.Log("Reset with: " + str(whatIs))
        sleep(0.3)
        api.GPIOSet(alchiDev, rfidControlPin, True)
        resetCnt = 0
        continue
    sleep(0.1)
    resetCnt += 1

api.GPIOSet(alchiDev, rfidControlPin, False)