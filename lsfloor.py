from lightsweeper import wait

from LSRealTile import LSRealTile
from LSRealTile import LSOpen
from LSEmulateTile import EmulateTile
from LSFloorConfigure import LSFloorConfig
from LSFloorConfigure import userSelect
from Move import Move
import Colors
import Shapes

import sys
import time
import os
import random

class LSFloor():
    """
        This class describes an abstract lightsweeper floor.
    """

    def __init__(self, rows=0, cols=0, configFile=None, eventCallback=None):
        # Load the configuration, if provided
        if configFile is None:
            self.conf = LSFloorConfig()
            self.conf.selectConfig()
        else:
            self.conf = LSFloorConfig(configFile)

        if configFile is None:
            self.rows = rows
            self.cols = cols
        else:
            self.rows = conf.rows
            self.cols = conf.cols

        self.eventCallback = eventCallback
        self.tiles = []

        self.addressToRowColumn = {}
        # single-dimensional array of tiles to iterate over
        self.tileList = []
        # double array of tile objects
        self.tileRows = []

        self.addressToRowColumn = {}
        # single-dimensional array of tiles to iterate over
        self.tileList = []
        # double array of tile objects
        self.tileRows = []

        self._makeFloor()
        print("\nClearing floor...")
        self.clearBoard()

    def _makeFloor (self):
        for r in range(0,self.rows):
            self.tiles.append([])
            for c in range(0, self.cols):
                self.tiles[r].append(EmulateTile(self, r, c))

    def setColor(self, row, col, color):
        tile = self.tiles[row][col]
        tile.setColor(color)

    def setShape(self, row, col, shape):
        tile = self.tiles[row][col]
        tile.setShape(shape)
        print(row)

# TODO
    def setDigit(self, row, column, digit):
        pass

    def set(self, row, col, shape, color):  # set is a python type, we may want to rename this
        tile = self.tiles[row][col]
        tile.set(shape, color)

    #segments is a list of seven colors in A,...,G order of segments
    def setCustom(self, row, col, segments):
        tile = self.tiles[row][col]
        tile.setCustom(segments)

    def clearBoard(self):
        tiles = self.tileList
        for tile in tiles:
            tile.blank()
        return

    def clear(self, row, col):
        tile = self.tiles[row][col]
        tile.set()

    def clearAll(self):
        for tile in self.tiles:
            tile.set()

    def pollSensors(self):
        pass

    def heartbeat(self):
        pass

    def showBoard(self):
        pass

    def refreshBoard(self):
        tiles = self._getTileList(0,0)
        for tile in tiles:
            tile.update('CLOCK')
        return

    def resetBoard(self):
        for row in self.tileRows:
            for tile in row:
                tile.reset()
        return

    def purgeTile(self,tile):
        return False

    def clock(self):
        tiles = self._getTileList(0,0)
        for tile in tiles:
            try:
                tile.read()
            except:
                print ("unexpected error on tile", self.tileAddresses[tile.getAddress()])
        self.refreshBoard()
        return True

    def _flushQueue(self):  # What should this do?
        pass


    def handleTileSensed(self, row, col):
        pass

    # How is this different from pollSensors?
    def getSensors(self):
        activeSensors = []
        for row in self.tileRows:
            for tile in row:
                sensorChecked = tile.getSensors()
                if sensorChecked:
                    activeSensors.append(sensorChecked)
        return activeSensors


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




#handles all communications with RealTile objects, serving as the interface to the
#actual lightsweeper floor. thus updates are pushed to it (display) and also pulled from it
#(sensor changes)
class LSRealFloor(LSFloor):
    """
        This class extends LSFloor with methods specific to interacting with real Lightsweeper hardware
    """

    # This is a buffer against serial corruption, bigger numbers are slower but more stable
    # .005 = Fastest speed before observed corruption (on 24 tiles split between two com ports)
    LSWAIT = .005

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
            wait(self.LSWAIT)


    def setAllShape(self, shape):
        for port in self.realTiles.sharedSerials.keys():
            zeroTile = LSRealTile(self.realTiles.sharedSerials[port])
            zeroTile.assignAddress(0)
            zeroTile.setShape(shape)
            wait(self.LSWAIT)


    def set(self, *args, **kwargs):
        LSFloor.set(self, *args, **kwargs)
        wait(self.LSWAIT)

    def setColor(self, *args, **kwargs):
        LSFloor.setColor(self, *args, **kwargs)
        wait(self.LSWAIT)

    def setShape(self, *args, **kwargs):
        LSFloor.setShape(self, *args, **kwargs)
        wait(self.LSWAIT)

    def setCustom(self, *args, **kwargs):
        LSFloor.setShape(self, *args, **kwargs)
        wait(self.LSWAIT)

    def setSegmentsCustom(self, row, col, segments):
        tile = self.tileRows[row][col]
        tile.setSegmentsCustom(segments)

    def clearBoard(self):
        for port in self.sharedSerials:
            zeroTile = LSRealTile(port)
            zeroTile.assignAddress(0)
            zeroTile.blank()
        wait(self.LSWAIT)

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
    
