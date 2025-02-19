from api import EscapeControlAPI
from time import sleep

api = EscapeControlAPI()

mainDev = 1
cabinet1Dev = 5
cabinet2Dev = 6

maglockCabinetDoor1 = 17  # Controlled by sensor on cabinet2Dev (Door 1)
maglockCabinetDoor2 = 16  # Controlled by sensor on cabinet1Dev (Door 2)

chainsLockPin = 20
cabinetDoorSensorCabinetDoor1 = 8   # Sensor for cabinet door 1 on cabinet1Dev
cabinetDoorSensorCabinetDoor2 = 9   # Sensor for cabinet door 2 on cabinet2Dev

cabinetUVControlPin = 11
cabinetOpensCounter = 0

api.GPIOSet(mainDev, chainsLockPin, False)  # Initialize chains lock
api.GPIOSetAnalog(cabinet1Dev, cabinetUVControlPin, 0)
while True: #TODO: сделать рабочим на протяжении 10 минут, потом выключать
    # Control for cabinet door 1 (sensor on cabinet1Dev)
    if api.GPIORead(cabinet1Dev, cabinetDoorSensorCabinetDoor1):
        api.GPIOSet(mainDev, maglockCabinetDoor1, True)
    else:
        api.GPIOSet(mainDev, maglockCabinetDoor1, False)
    
    # Control for cabinet door 2 (sensor on cabinet2Dev)
    if api.GPIORead(cabinet2Dev, cabinetDoorSensorCabinetDoor2):
        api.GPIOSet(mainDev, maglockCabinetDoor2, True)
        cabinetOpensCounter += 1
    else:
        api.GPIOSet(mainDev, maglockCabinetDoor2, False)

    if cabinetOpensCounter == 10 or cabinetOpensCounter == 15: #somebody in 2nd room
        api.LocksUnlock(9)

    # If both cabinet door sensors are active (doors closed), turn on the UV LED; otherwise, turn it off.
    if not api.GPIORead(cabinet1Dev, cabinetDoorSensorCabinetDoor1) and not api.GPIORead(cabinet2Dev, cabinetDoorSensorCabinetDoor2):
        api.GPIOSetAnalog(cabinet1Dev, cabinetUVControlPin, 255)
    else:
        api.GPIOSetAnalog(cabinet1Dev, cabinetUVControlPin, 0)
        
    sleep(0.2)