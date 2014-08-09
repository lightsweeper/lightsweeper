#!/usr/bin/python3

from LSRealFloor import LSRealFloor
from LSRealTile import LSRealTile
from serial import Serial
from serial import SerialException
import time
import os
import random

def main():
    debug = False
    availPorts = list(serial_ports())
    print("Available serial ports:" + str(availPorts))
    # top-left, A1,2,3
    comPort1 = "COM5"
    # top-right, A4,5,6
    comPort2 = "COM7"
    # bottom-left, B1,2,3
    comPort3 = "COM8"
    # bottom-right, B4,5,6
    comPort4 = "COM9"
    print("connecting to ", comPort1, comPort2, comPort3, comPort4)
    serial1 = None
    serial2 = None
    serial3 = None
    serial4 = None
    try:
        serial1 = Serial(comPort1, 19200, timeout=0.005)
    except IOError:
        print("Could not open", comPort1)
    try:
        serial2 = Serial(comPort2, 19200, timeout=0.005)
    except IOError:
       print("Could not open", comPort2)
    try:
        serial3 = Serial(comPort3, 19200, timeout=0.005)
    except IOError:
        print("Could not open", comPort3)
    try:
        serial4 = Serial(comPort4, 19200, timeout=0.005)
    except IOError:
        print("Could not open", comPort4)
    print("finished with COM ports")
    zeroTile = LSRealTile(serial1)
    zeroTile.assignAddress(0)
    zeroTile.blank()
    zeroTile = LSRealTile(serial2)
    zeroTile.assignAddress(0)
    zeroTile.blank()
    zeroTile = LSRealTile(serial3)
    zeroTile.assignAddress(0)
    zeroTile.blank()
    zeroTile = LSRealTile(serial4)
    zeroTile.assignAddress(0)
    zeroTile.blank()
    if debug:
        print("testing serial 1")
        testPatternCritical(serial1)
        print("testing serial 2")
        testPatternCritical(serial2)
        print("testing serial 3")
        testPatternCritical(serial3)
        print("testing serial 4")
        testPatternCritical(serial4)
        sensorTest(serial1)
        sensorTest(serial2)
        sensorTest(serial3)
        sensorTest(serial4)
    else:
        print("creating main class")
        serials = [serial1, serial2, serial3, serial4]
        floor = LSRealFloor(3, 3, random.randint(2,3), serials)
        print("starting loop")
        floor.startLoop()

def serial_ports():
    """
    Returns a generator for all available serial ports
    """
    if os.name == 'nt':
        # windows
        for i in range(256):
            try:
                s = Serial(i)
                s.close()
                yield 'COM' + str(i + 1)
            except SerialException:
                pass

def testPatternCritical(serial):
    tile = LSRealTile(serial)
    tiles = []
    for i in range(1, 10):
        tile = LSRealTile(serial)
        tile.assignAddress(i * 8)
        tile.setDigit(8)
        tiles.append(tile)
    lastTime = time.time()
    while time.time() - lastTime < 0.2:
            pass
    for tile in tiles:
        tile.setColor(LSRealFloor.RED)
    lastTime = time.time()
    while time.time() - lastTime < 0.2:
            pass
    for tile in tiles:
        tile.setColor(LSRealFloor.RED)
    lastTime = time.time()
    while time.time() - lastTime < 2:
        pass
    for tile in tiles:
        tile.setColor(LSRealFloor.YELLOW)
    lastTime = time.time()
    while time.time() - lastTime < 0.2:
            pass
    for tile in tiles:
        tile.setColor(LSRealFloor.YELLOW)
    lastTime = time.time()
    while time.time() - lastTime < 0.2:
            pass
    for tile in tiles:
        tile.setColor(LSRealFloor.YELLOW)

    lastTime = time.time()
    while time.time() - lastTime < 2:
        pass
    for tile in tiles:
        tile.setColor(LSRealFloor.GREEN)
    lastTime = time.time()
    while time.time() - lastTime < 0.2:
            pass
    for tile in tiles:
        tile.setColor(LSRealFloor.GREEN)
    lastTime = time.time()
    while time.time() - lastTime < 0.2:
            pass
    for tile in tiles:
        tile.setColor(LSRealFloor.GREEN)
    lastTime = time.time()
    while time.time() - lastTime < 0.2:
            pass
    for tile in tiles:
        tile.setColor(LSRealFloor.GREEN)
    lastTime = time.time()
    while time.time() - lastTime < 0.2:
            pass
    lastTime = time.time()
    while time.time() - lastTime < 2:
        pass
    for tile in tiles:
        tile.setColor(LSRealFloor.BLUE)
    lastTime = time.time()
    while time.time() - lastTime < 0.2:
            pass
    for tile in tiles:
        tile.setColor(LSRealFloor.BLUE)
    lastTime = time.time()
    while time.time() - lastTime < 0.2:
            pass
    for tile in tiles:
        tile.setColor(LSRealFloor.BLUE)
    lastTime = time.time()
    while time.time() - lastTime < 0.2:
            pass
    for tile in tiles:
        tile.setColor(LSRealFloor.BLUE)
    lastTime = time.time()
    while time.time() - lastTime < 0.2:
            pass
    lastTime = time.time()
    while time.time() - lastTime < 2:
        pass
    for tile in tiles:
        tile.setColor(LSRealFloor.VIOLET)
    lastTime = time.time()
    while time.time() - lastTime < 0.2:
            pass
    for tile in tiles:
        tile.setColor(LSRealFloor.VIOLET)
    lastTime = time.time()
    while time.time() - lastTime < 0.2:
            pass
    for tile in tiles:
        tile.setColor(LSRealFloor.VIOLET)

    lastTime = time.time()
    while time.time() - lastTime < 2:
        pass
    for tile in tiles:
        tile.setColor(LSRealFloor.BLACK)
    lastTime = time.time()
    while time.time() - lastTime < 0.2:
            pass
    for tile in tiles:
        tile.setColor(LSRealFloor.BLACK)

def sensorTest(serial):
    serial.write([0, 1])

if __name__ == '__main__':
    main()
