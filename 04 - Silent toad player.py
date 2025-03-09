from api import EscapeControlAPI
from time import sleep
from time import time
api = EscapeControlAPI()


beastDev = 3  #рядом с животным

RX = 6
TX = 7
DF = 4
volume = 5
folder_id = 2
frog_song = 3
wakeup_sound = 2
api.DFPlayerBegin(beastDev, DF, RX, TX)
sleep(0.5)
api.DFPlayerVolume(beastDev, DF, volume)
sleep(0.5)
api.SetParameter('frogSongEnd', 0) 
notePins = [2,3,4,5]
api.DFPlayerPlayFolder(beastDev,DF,folder_id,frog_song)