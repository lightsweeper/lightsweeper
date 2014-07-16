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
    comPort = "COM5"
    print("connecting to ", comPort)
    serial = None
    try:
        serial = Serial(comPort, 19200, timeout=0.001)
    except IOError:
        print("Could not open ", comPort)
    debug = True
    if debug:
        testPatternCritical(serial)

    print("creating main class")
    addresses = [32, 40, 48]
    floor = LSRealFloor(1, 3, 1, addresses, serial)
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
    for i in range(36):
        tile.assignAddress(i * 8)
        tile.setColor(LSRealFloor.RED)
        tile.setDigit(8)
    for i in range(36):
        tile.assignAddress(i * 8)
        tile.setColor(LSRealFloor.YELLOW)
        tile.setDigit(8)
    for i in range(36):
        tile.assignAddress(i * 8)
        tile.setColor(LSRealFloor.RED)
        tile.setDigit(8)
    for i in range(36):
        tile.assignAddress(i * 8)
        tile.setColor(LSRealFloor.RED)
        tile.setDigit(8)
    for i in range(36):
        tile.assignAddress(i * 8)
        tile.setColor(LSRealFloor.RED)
        tile.setDigit(8)

if __name__ == '__main__':
    main()
