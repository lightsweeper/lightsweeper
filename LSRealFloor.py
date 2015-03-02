### Implementation of the Lightsweeper floor
from LSRealTile import LSRealTile
from LSRealTile import LSOpen

import time
import os
import random
import Colors
import Shapes
from Move import Move
from LSAudio import Audio
from LSFloorConfigure import LSFloorConfig
from LSFloorConfigure import userSelect

# Maximum speed of loop before serial corruption (on 24 tiles split between two com ports)
OURWAIT = .005

#handles all communications with RealTile objects, serving as the interface to the
#actual lightsweeper floor. thus updates are pushed to it (display) and also pulled from it
#(sensor changes)
class LSRealFloor():
    SENSOR_THRESHOLD = 100
    sharedSerials = dict()

    def __init__(self, rows=0, cols=0, serials=None, configFile=None, eventCallback=None):
        # Load the configuration
        if configFile is None:
            conf = LSFloorConfig()
            conf.selectConfig()
        else:
            conf = LSFloorConfig(configFile)

        self.rows = conf.rows
        self.cols = conf.cols
        self.eventCallback = eventCallback

        # Initialize the serial ports
        self.realTiles = LSOpen()

        # Initialize calibration map
        self.calibrationMap = dict()

        self.addressToRowColumn = {}
        # single-dimensional array of tiles to iterate over
        self.tileList = []
        # double array of tile objects
        self.tileRows = []
        
        for row in conf.board:
            tiles = []
            self.tileAddresses = []
            for col in conf.board[row]:
                (port, address) = conf.board[row][col]
                tile = LSRealTile(self.realTiles.sharedSerials[port])
                tile.comNumber = port
                self.calibrationMap[address] = [127,127]
                tile.active = 0
                tile.assignAddress(address)
                tile.eepromRead(0)
                self.addressToRowColumn[(address,port)] = (row, col)
                tile.setColor(Colors.WHITE)
                tile.setShape(Shapes.ZERO)
                tiles.append(tile)
                self.tileList.append(tile)
                wait(.05)
            self.tileRows.append(tiles)
        print("Loaded " + str(conf.rows) + " rows and " + str(conf.cols) + " columns (" + str(conf.cells) + " tiles)")

        print("\nClearing floor...")
        self.clearBoard()


    def heartbeat(self):
        pass

    def handleTileStepEvent(self, row, col, val):
        if self.eventCallback is not None:
            self.eventCallback(row, col, val)

    def setAllColor(self, color):
        for port in self.realTiles.sharedSerials.keys():
            zeroTile = LSRealTile(self.realTiles.sharedSerials[port])
            zeroTile.assignAddress(0)
            zeroTile.setColor(color)


    def setAllShape(self, shape):
        for port in self.realTiles.sharedSerials.keys():
            zeroTile = LSRealTile(self.realTiles.sharedSerials[port])
            zeroTile.assignAddress(0)
            zeroTile.setShape(shape)


    def set(self, row, col, shape=0, color=0):
        tile = self.tileRows[row][col];
        tile.setColor(color)
        tile.setShape(shape)
        wait(0.005)

    def setColor(self, row, col, color):#
        tile = self.tileRows[row][col]
        tile.setColor(color)
        wait(0.005)

    def setShape(self, row, col, shape):
        tile = self.tileRows[row][col]
        tile.setShape(shape)
        wait(0.005)

    def setSegmentsCustom(self, row, col, segments):
        tile = self.tileRows[row][col]
        tile.setSegmentsCustom(segments)

    def RAINBOWMODE(self, updateFrequency = 0.4):
        self.setAllShape(Shapes.EIGHT)
        RAINBOW = [Colors.RED,
                Colors.YELLOW,
                Colors.GREEN,
                Colors.CYAN,
                Colors.BLUE,
                Colors.MAGENTA,
                Colors.WHITE]

        for COLOR in RAINBOW:
            self.setAllColor(COLOR)
            wait(updateFrequency)


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



    def _getTileList(self,row,column):
    # __init__ makes this for us now:
    # Unused functionality of this method should be split into _getRow and _getCol methods (perhaps public?)
#        tileList = []
#        #whole floor
#        # whole floor
#        if row < 1 and column < 1:
#            for tileRow in self.tileRows:
#                for tile in tileRow:
#                    tileList.append(tile)
#                    count = len(tileList)
#        # whole row
#        elif column < 1:
#            tileRow = self.tileRows[row-1]
#            for tile in tileRow:
#                tileList.append(tile)
#                count = len(tileList)
#        # whole column
#        elif row < 1:
#            for tileRow in self.tileRows:
#                tile = tileRow[column-1]
#                tileList.append(tile)
#                count = len(tileList)
#        # single tile
#        else:
#            tileRow = self.tileRows[row-1]
#            tileList = [tileRow[column-1]]
#        return tileList
        return self.tileList


    def clearBoard(self):
        for port in self.sharedSerials:
            zeroTile = LSRealTile(port)
            zeroTile.assignAddress(0)
            zeroTile.blank()



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


    def showboard(self):
        return


    def refreshboard(self):
        return


    def resetboard(self):
        return


    def purgetile(self,tile):
        return False


    def clock(self):
        return


def wait(seconds):
    # self.pollSensors()
    currentTime = time.time()
    while time.time() - currentTime < seconds:
        pass

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
    
