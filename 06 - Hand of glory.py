from api import EscapeControlAPI
from time import sleep
from time import time

api = EscapeControlAPI()

cabinet1Dev = 5
hand = 5
handLight = 14  # M- hand

while True:
    sleep(0.25)
    if api.GPIORead(cabinet1Dev, hand) == 0:
        api.GPIOSet(cabinet1Dev, handLight, True)
    else:
        api.GPIOSet(cabinet1Dev, handLight, False)