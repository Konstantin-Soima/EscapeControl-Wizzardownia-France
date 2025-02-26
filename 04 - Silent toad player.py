from api import EscapeControlAPI
from time import sleep
from time import time
api = EscapeControlAPI()


beastDev = 3  #рядом с животным

RX = 9#7
TX = 54#8
DF = 2
volume = 25
folder_id = 2
frog_song = 3
wakeup_sound = 2
api.DFPlayerBegin(beastDev, DF, RX, TX)
sleep(1)
api.DFPlayerVolume(beastDev, DF, int(volume//2))
sleep(1)
api.SetParameter('frogSongEnd', 0) 
notePins = [3,4,5,6]
api.DFPlayerPlayFolder(beastDev,DF,folder_id,frog_song)
api.LocksWait(4)
for vlm in range(volume//2,int(volume/1.25)):
    sleep(1)
    api.DFPlayerVolume(beastDev, DF, vlm)
api.LocksWait(5)
for vlm in range(int(volume/1.25),volume):
    api.DFPlayerVolume(beastDev, DF, vlm)
    sleep(0.5)
api.DFPlayerVolume(beastDev, DF, volume)
played = True
while played:
    readNotes = api.GPIOReadList(beastDev, notePins)
    if api.GetParameter('frogSongEnd'):
        played = False
    if sum(readNotes) == 0:

        break
    sleep(0.2)
api.LocksUnlock(1 + 5)
api.DFPlayerStop(beastDev,DF)