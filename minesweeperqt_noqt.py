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
    serial = Serial(comPort, 19200, timeout=0.001)
    debug = True
    if debug:
        tile = LSRealTile(serial)
        tile.serialOpen = True
        tile.assignAddress(40)
        lastTime = time.time()
        print("setting color and shape of initial tile")
        tile.setColor(3)
        tile.setDigit(1)
        while time.time() - lastTime < 2:
            pass
        lastTime = time.time()
        tile.setColor(2)
        tile.setDigit(2)
        while time.time() - lastTime < 2:
            pass
        lastTime = time.time()
        tile.setColor(4)
        tile.setDigit(3)
        while time.time() - lastTime < 2:
            pass

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

if __name__ == '__main__':
    main()
