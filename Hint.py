from api import EscapeControlAPI
from time import sleep
from time import time
api = EscapeControlAPI()


count = api.GetParameter("Hint2")
player_txt = api.connectToPlayer(3)
if count == 0:
    player_txt.playSound("release_the_ghost_1.mp3")
elif count == 1:
    player_txt.playSound("release_the_ghost_2.mp3")
elif count >= 2:
    player_txt.playSound("release_the_ghost_1.mp3")
    sleep(8)
    player_txt.playSound("release_the_ghost_2.mp3")
count += 1
api.SetParameter("Hint2", count)