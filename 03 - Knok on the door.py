import collections
import threading
from time import sleep
from time import time

from api import EscapeControlAPI

api = EscapeControlAPI()

main = 1
ghost = 4

flashlightPin = 12
sensorPin = 7

flashTime = 0.3
phaseTime = 1

threshold = 2#50
flashSequence1 = [3, 1, 2]
flashSequence2 = [2, 1, 2]
flashSequences = [[3, 1, 2],[2, 1, 2],[1, 1, 2]]
knocks = [0] * 3

lastKnockTime = time()

analogValue = 0
pre_analogValue = 0


def readKnock():
    global analogValue, pre_analogValue
    pre_analogValue = analogValue
    analogValue = api.GPIOReadAnalog(ghost, sensorPin)
    #api.Log(analogValue)
    if analogValue > threshold and pre_analogValue < analogValue and time() - lastKnockTime > 0.1:
        api.Log(analogValue)
        return True
    return False


def toggle():
    api.GPIOSet(ghost, flashlightPin, 1)
    sleep(flashTime)
    api.GPIOSet(ghost, flashlightPin, 0)
    sleep(flashTime)


def flash():
    t = threading.current_thread()
    while getattr(t, "state") == 1:
        for phase in flashSequence1:
            for count in range(phase):
                toggle()
            sleep(phaseTime)
        sleep(3)


flashThread = threading.Thread(target=flash)
flashThread.state = 1
flashThread.start()

while True:
    if readKnock():
        if time() - lastKnockTime > 0.8:
            knocks.append(1)
            knocks = knocks[1: 4]
        else:
            knocks[2] += 1
        lastKnockTime = time()
        api.Log(knocks)
        #         here we have time expired after last knock so need to check the result
    if knocks in flashSequences:
        break

api.LocksUnlock(5)
api.LocksUnlock(4 + 1)
flashThread.state = 0