#!/usr/bin/python3

from LSRealFloor import LSRealFloor
from LSRealTile import LSRealTile
from serial import Serial
from serial import SerialException
import time
import os

def main():
    availPorts = list(serial_ports())
    print("Available serial ports:" + str(availPorts))
    # top-left, A1,2,3
    comPort1 = "COM1"
    # top-right, A4,5,6
    comPort2 = "COM2"
    # bottom-left, B1,2,3
    comPort3 = "COM3"
    # bottom-right, B4,5,6
    comPort4 = "COM4"
    print("connecting to ", comPort1, comPort2, comPort3, comPort4)
    serial1 = None
    serial2 = None
    serial3 = None
    serial4 = None
    try:
        serial1 = Serial(comPort1, 19200, timeout=0.001)
    except IOError:
        print("Could not open", comPort1)
    try:
        serial2 = Serial(comPort2, 19200, timeout=0.001)
    except IOError:
       print("Could not open", comPort2)
    try:
        serial3 = Serial(comPort3, 19200, timeout=0.001)
    except IOError:
        print("Could not open", comPort3)
    try:
        serial4 = Serial(comPort4, 19200, timeout=0.001)
    except IOError:
        print("Could not open", comPort4)
    print("finished with COM ports")
    debug = False
    if debug:
        testPatternCritical(serial1)
        testPatternCritical(serial2)
        testPatternCritical(serial3)
        testPatternCritical(serial4)
    else:
        print("creating main class")
        serials = [serial1, serial2, serial3, serial4]
        floor = LSRealFloor(6, 6, 8, serials)
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
        tile.setColor(LSRealFloor.RED)
        tile.setDigit(8)
        tiles.append(tile)
    lastTime = time.time()
    while time.time() - lastTime < 2:
        pass
    for tile in tiles:
        tile.setColor(LSRealFloor.YELLOW)
        tile.setDigit(8)
    lastTime = time.time()
    while time.time() - lastTime < 2:
        pass
    for tile in tiles:
        tile.setColor(LSRealFloor.GREEN)
        tile.setDigit(8)
    lastTime = time.time()
    while time.time() - lastTime < 2:
        pass
    for tile in tiles:
        tile.setColor(LSRealFloor.BLUE)
        tile.setDigit(8)
    lastTime = time.time()
    while time.time() - lastTime < 2:
        pass
    for tile in tiles:
        tile.setColor(LSRealFloor.VIOLET)
        tile.setDigit(8)
    lastTime = time.time()
    while time.time() - lastTime < 2:
        pass
    for tile in tiles:
        tile.setColor(LSRealFloor.BLACK)
        tile.setDigit(8)
if __name__ == '__main__':
    main()
