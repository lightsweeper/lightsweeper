### Implementation of the Lightsweeper floor
from LSRealTile import LSRealTile
from LSRealTile import LSOpen

from lsfloor import LSFloor

import time
import os
import random
import Colors
import Shapes
from Move import Move
from LSAudio import Audio
from LSFloorConfigure import LSFloorConfig
from LSFloorConfigure import userSelect
from lightsweeper import wait

# This is a buffer against serial corruption, bigger numbers are slower but more stable
# .005 = Fastest speed before observed corruption (on 24 tiles split between two com ports)
LSWAIT = .005

#handles all communications with RealTile objects, serving as the interface to the
#actual lightsweeper floor. thus updates are pushed to it (display) and also pulled from it
#(sensor changes)
class LSRealFloor(LSFloor):
    SENSOR_THRESHOLD = 100
    sharedSerials = dict()

    def __init__(self, rows=0, cols=0, serials=None, configFile=None, eventCallback=None):

        # Call parent init
        LSFloor.__init__(self, rows=rows, cols=cols, configFile=configFile, eventCallback=eventCallback)

        # Initialize the serial ports
        self.realTiles = LSOpen()

        # Initialize calibration map
        self.calibrationMap = dict()


    def _makeFloor(self):
        for row in conf.board:
            self.tileAddresses = []
            for col in conf.board[row]:
                (port, address) = conf.board[row][col]
                tile = LSRealTile(self.realTiles.sharedSerials[port])
                tile.comNumber = port
                self.calibrationMap[address] = [127,127]
                tile.active = 0
                tile.assignAddress(address)
                self.addressToRowColumn[(address,port)] = (row, col)
                tile.setColor(Colors.WHITE)
                tile.setShape(Shapes.ZERO)
                self.tiles.append(tile)
                self.tileList.append(tile)
                wait(.05)
            self.tileRows.append(tiles)
        print("Loaded " + str(conf.rows) + " rows and " + str(conf.cols) + " columns (" + str(conf.cells) + " tiles)")


    def handleTileStepEvent(self, row, col, val):
        if self.eventCallback is not None:
            self.eventCallback(row, col, val)

    def setAllColor(self, color):
        for port in self.realTiles.sharedSerials.keys():
            zeroTile = LSRealTile(self.realTiles.sharedSerials[port])
            zeroTile.assignAddress(0)
            zeroTile.setColor(color)
            wait(LSWAIT)


    def setAllShape(self, shape):
        for port in self.realTiles.sharedSerials.keys():
            zeroTile = LSRealTile(self.realTiles.sharedSerials[port])
            zeroTile.assignAddress(0)
            zeroTile.setShape(shape)
            wait(LSWAIT)


    def set(self, *args, **kwargs):
        LSFloor.set(self, *args, **kwargs)
        wait(LSWAIT)

    def setColor(self, *args, **kwargs):
        LSFloor.setColor(self, *args, **kwargs)
        wait(LSWAIT)

    def setShape(self, *args, **kwargs):
        LSFloor.setShape(self, *args, **kwargs)
        wait(LSWAIT)

    def setCustom(self, *args, **kwargs):
        LSFloor.setShape(self, *args, **kwargs)
        wait(LSWAIT)

    def setSegmentsCustom(self, row, col, segments):
        tile = self.tileRows[row][col]
        tile.setSegmentsCustom(segments)

    def clearBoard(self):
        for port in self.sharedSerials:
            zeroTile = LSRealTile(port)
            zeroTile.assignAddress(0)
            zeroTile.blank()
        wait(LSWAIT)

    def printAddresses(self):
        s = ""
        for row in range(0,self.rows):
            for col in range(0, self.cols):
                s += str(self.tileRows[row][col].getAddress()) + " "
            #print(s)
            s = ""


    def pollSensors(self, sensitivity=.95):
        sensorsChanged = []
        #tiles = self._getTileList(0,0)
        tiles = self.tileList
        #sensorPoll = 0
        for tile in tiles:
            #currentTime = time.time()
            reading = tile.sensorStatus()
            #sensorPoll = sensorPoll + time.time() - currentTime
            cMap = self.calibrationMap[tile.address]
            lowest = cMap[0]
            highest = cMap[1]
            if reading < lowest:
                lowest = reading
                cMap[0] = lowest
            elif reading > highest:
                highest = reading
                cMap[1] = highest
            self.calibrationMap[tile.address] = cMap
            
            if reading < (((highest-lowest) * sensitivity) + lowest) and lowest < 127:
                if tile.active <= 0:
                    tile.active = 1
                    #print("Stepped on {:d} ({:d})".format(tile.address,reading)) # Debugging
                    rowCol = self.addressToRowColumn[(tile.address, tile.comNumber)]
                    move = Move(rowCol[0], rowCol[1], reading)
                    sensorsChanged.append(move)
                    self.handleTileStepEvent(rowCol[0], rowCol[1], reading)
                else:
                    tile.active += 1
            elif reading is highest:
                if tile.active > 0:
                    tile.active = 0
              #      print ("Stepped off {:d} ({:d})".format(tile.address,reading)) # Debugging
        #print("sensor polls took " + str(sensorPoll) + "ms")
        return sensorsChanged



    def pollSensors_NoAddress(self, limit):
        sensorsChanged = []
        polled = 0
        for com in range(len(self.sharedSerials)):
            for addy in range(1, 25):
                tile = LSRealTile(self.sharedSerials[com])
                tile.assignAddress(addy * 8)
                val = tile.sensorStatus()
                if val < self.SENSOR_THRESHOLD:
                    print("sensor sensed", val)
                    sensorsChanged.append((addy * 8, com))
                polled += 1
                if polled >= limit:
                    return sensorsChanged
        return sensorsChanged

if __name__ == "__main__":
    def HYPERRAINBOWMODE(oscLow = 1, oscHigh = 30):
        print("HYPER RAINBOW MODE!!")
        def minus(i):
            return i-1
        def plus(i):
            return i+1
        i = 0
        while True:  #Hyper rainbow mode
            floor.RAINBOWMODE(i * .005)
            if i > oscHigh:
                fun = minus
            if i < oscLow:
                fun = plus
            i = fun(i)
            
    def NOISESWEEPER(noise=.005):
        import random
        i = random.random()
        while True:  #Hyper rainbow mode
            floor.RAINBOWMODE(i * noise)
            i = random.random()
            print(i)    


    print("todo: testing RealFloor")
    floor = LSRealFloor()
    #audio.playSound("8bit/46.wav")
    #wait(5)
    #call not implemented yet
    #floor.setSegmentsCustom(0, 0, [Colors.RED, Colors.YELLOW, Colors.GREEN, Colors.CYAN, Colors.BLUE, Colors.VIOLET, Colors.WHITE])
    HYPERRAINBOWMODE()
   # NOISESWEEPER()
    
