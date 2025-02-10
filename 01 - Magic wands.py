from api import EscapeControlAPI
from time import sleep
from time import time

api = EscapeControlAPI()

beastDev = 3  # рядом с животным
wandsPins = 2  # D2 - провода скручены последовательно

while not api.GPIORead(beastDev, wandsPins):
    # Любая поднятая палочка должна активировать
    sleep(0.1)

# Какое освещение, LED или лампа на реле?
api.LocksUnlock(3)
api.LocksUnlock(1 + 2)
