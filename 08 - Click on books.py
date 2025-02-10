from api import EscapeControlAPI
from time import sleep
from time import time

api = EscapeControlAPI()

mainDev = 1
cabinet2Dev = 6
pins = [6, 5, 7, 2, 3, 4]
answer = [6, 2, 4, 5, 3, 7]
stack = [None] * 6
player_sfx = api.connectToPlayer(2)  # Плеер ситуационных звуков

def playSfx(sound):
    player_sfx.playSound(sound + ".mp3")

def stackAppend(n):
    non = stack.count(None)
    if non > 0:
        stack[6 - non] = n
    else:
        for i in range(5):
            stack[i] = stack[i + 1]
        stack[5] = n


last = [None] * 6
api.Log(api.GPIOReadList(cabinet2Dev, pins))
while True:
    sleep(0.2)
    books = api.GPIOReadList(cabinet2Dev, pins)
    if books == last:
        continue
    if sum(books) == 5:
        #playSfx("click_on_books_trigger")
        api.Log(books)
        pined = pins[books.index(0)]
        stackAppend(pined)
        api.Log(stack)
        last = books
    if stack == answer:
        api.GPIOSet(mainDev, 21, False)  # Lighter Locker
        api.LocksUnlock(10)
        break
api.LocksUnlock(9 + 1)
