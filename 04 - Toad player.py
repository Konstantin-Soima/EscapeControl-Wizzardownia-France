from api import EscapeControlAPI
from time import sleep
from time import time
api = EscapeControlAPI()


beastDev = 3  #рядом с животным

RX = 6#7
TX = 7#8
DF = 4
volume = 22
folder_id = 2
frog_song = 3
wakeup_sound = 2
api.DFPlayerBegin(beastDev, DF, RX, TX)
sleep(0.2)
api.DFPlayerVolume(beastDev, DF, int(volume//4))
sleep(0.2)
api.SetParameter('frogSongEnd', 0) 
notePins = [2,3,4,5]
api.ScenarioStop(55) #Stop silent player
api.DFPlayerPlayFolder(beastDev,DF,folder_id,frog_song)
sleep(0.1)
for vlm in range(int(volume/4),volume):
    api.DFPlayerVolume(beastDev, DF, vlm)
    sleep(0.5)
    api.Log("Level:"+str(vlm))
api.DFPlayerVolume(beastDev, DF, volume)
played = True
api.Log("Loud")
while played:
    readNotes = api.GPIOReadList(beastDev, notePins)
    if api.GetParameter('frogSongEnd'):
        played = False
    if sum(readNotes) == 0:

        break
    sleep(0.2)
api.LocksUnlock(6)
api.DFPlayerStop(beastDev,DF)