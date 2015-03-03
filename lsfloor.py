from lightsweeper import wait
from lightsweeper import Move

from LSRealTile import LSRealTile
from LSRealTile import LSOpen
from LSEmulateTile import EmulateTile
from LSFloorConfigure import LSFloorConfig
from LSFloorConfigure import userSelect

import Colors
import Shapes

import sys
import time
import os
import random

class LSFloor():
    """
        This class describes an abstract lightsweeper floor.

        Attributes:
            conf (LSFloorConfig):   An LSFloorConfig object containing the floor's configuration
            rows (int):             The number of rows
            cols (int):             The number of columns
            tileList (list):        A single array of tile objects
            tiles (list):           A double array of LSTile objects

    """
    def __init__(self, rows=None, cols=None, conf=None, eventCallback=None):
        # Load the configuration, if provided
        if conf is None:
            if rows is None or cols is None:
                conf = LSFloorConfig()
                conf.selectConfig()
            else:
                self.rows = rows
                self.cols = cols
                conf = LSFloorConfig(rows=rows, cols=cols)

        self.conf = conf
        
        self.rows = conf.rows
        self.cols = conf.cols
        

        self.eventCallback = eventCallback
        self.tiles = []
        self.tileList = []
        
        # Initialize calibration map
        self.calibrationMap = dict()
        
        self._addressToRowColumn = {}
        self.tileAddresses = []

        for row in range(0,self.rows):
            self.tiles.append([])
            for col in range(0, self.cols):
                (port, address) = self.conf.board[row][col]
                tile = self._returnTile(row, col, port)
                tile.comNumber = port
                self.calibrationMap[address] = [127,127]
                self._addressToRowColumn[(address,port)] = (row, col)
                tile.assignAddress(address)
                tile.setColor(Colors.WHITE)
                tile.setShape(Shapes.ZERO)
                tile.active=0
                wait(.05)
                self.tiles[row].append(tile)
                self.tileList.append(tile)
    
    def _returnTile(self, row, col, port=None):
        return(EmulateTile(self, row, col))


    def setColor(self, row, col, color):
        """
            Sets the color of the selected tile.
        """
        tile = self.tiles[row][col]
        tile.setColor(color)

    def setShape(self, row, col, shape):
        """
            Sets the shape of the selected tile.
        """
        tile = self.tiles[row][col]
        tile.setShape(shape)

    def setAllColor(self, color):
        for tile in self.tileList:
            self.setColor(tile.row, tile.col, color)


    def setAllShape(self, shape):
        for tile in self.tileList:
            self.setShape(tile.row, tile.col, shape)

# TODO
    def setDigit(self, row, column, digit, color=None):
        """
            Sets the tile at row, column to the provided digit.
        """
        pass

    def set(self, row, col, shape, color):  # set is a python type, we may want to rename this
        """
            Sets the color and shape simultaneously.
        """
        tile = self.tiles[row][col]
        tile.set(shape, color)

    def setAll(self, shape, color):
        for tile in self.tileList:
            self.set(tile.row, tile.col, shape, color)

    #segments is a list of seven colors in A,...,G order of segments
    def setCustom(self, row, col, segments):
        tile = self.tiles[row][col]
        tile.setCustom(segments)

    def blank(self, row, col):
        """
            Blanks the tile at row, col
        """
        tile = self.tiles[row][col]
        tile.blank()

    def clearBoard(self):
        """
            Blanks the whole floor.
        """
        for tile in self.tileList:
            tile.blank()
        return

#    def clear(self, row, col):
#        tile = self.tiles[row][col]
#        tile.set()

#    def clearAll(self):
#        for tile in self.tileList:
#            tile.set()

    def pollSensors(self):
        pass

    def heartbeat(self):
        pass

    def showBoard(self):
        pass

    def refreshBoard(self):
        for tile in self.tileList:
            tile.update('CLOCK')
        return

    def resetBoard(self):
        for tile in self.tileList:
            tile.reset()
        return

    def purgeTile(self,tile):
        return False

    def clock(self):
        for tile in self.tileList:
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
        for row in self.tiles:
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

    def __init__(self, rows=None, cols=None, serials=None, conf=None, eventCallback=None):

        # Initialize the serial ports
        self.realTiles = LSOpen()
        self.sharedSerials = dict()
        
        # Call parent init
        LSFloor.__init__(self, rows=rows, cols=cols, conf=conf, eventCallback=eventCallback)
        print("Loaded {:d} rows and {:d} columns ({:d} tiles)".format(self.rows, self.cols, self.conf.cells))
        print("\nClearing floor...")
        self.clearBoard()
        
        def _returnTile(self, row, col, port):
            return(LSRealTile(self.realTiles.sharedSerials[port], row, col))


  #  def _makeFloor(self):
  #      for row in self.conf.board:
  #          self.tileAddresses = []
  #          self.tiles.append([])
  #          for col in self.conf.board[row]:
  #              (port, address) = self.conf.board[row][col]
  #              tile = LSRealTile(self.realTiles.sharedSerials[port], row, col)
  #              tile.comNumber = port
  #              self.calibrationMap[address] = [127,127]
  #              tile.active = 0
  #              tile.assignAddress(address)
  #              self._addressToRowColumn[(address,port)] = (row, col)
  #              tile.setColor(Colors.WHITE)
  #              tile.setShape(Shapes.ZERO)
  #              self.tiles[row].append(tile)
  #              self.tileList.append(tile)
  #              wait(.05)


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

    # !!!
    def set(self, row, col, shape, color):
        tile = self.tiles[row][col]
        tile.setShape(shape)
        tile.setColor(color)
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
        tile = self.tiles[row][col]
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
                s += str(self.tiles[row][col].getAddress()) + " "
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
                    rowCol = self._addressToRowColumn[(tile.address, tile.comNumber)]
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



#    def pollSensors_NoAddress(self, limit):
#        sensorsChanged = []
#        polled = 0
#        for com in range(len(self.sharedSerials)):
#            for addy in range(1, 25):
#                tile = LSRealTile(self.sharedSerials[com])
#                tile.assignAddress(addy * 8)
#                val = tile.sensorStatus()
#                if val < self.SENSOR_THRESHOLD:
#                    print("sensor sensed", val)
#                    sensorsChanged.append((addy * 8, com))
#                polled += 1
#                if polled >= limit:
#                    return sensorsChanged
#        return sensorsChanged


def main():

    

    print("Importing LSDisplay")
    import LSDisplay

    d = LSDisplay.Display(realFloor = True, simulatedFloor = True)

    print("Testing set")
    d.set(0,1,Shapes.L,Colors.RED)
    d.set(0,1,Shapes.I,Colors.YELLOW)
    d.heartbeat()
    wait(2)

    print("Testing setAll")
    d.setAll(Shapes.B,Colors.BLUE)
    d.heartbeat()
    wait(2)

    print("Testing setColor")
    d.setColor(2,1,Colors.GREEN)
    d.heartbeat()
    wait(2)

    print("Testing setShape")
    d.setShape(1,1,Shapes.ZERO)
    d.heartbeat()
    wait(2)

    print("Testing setAllColor")
    d.setAllColor(Colors.MAGENTA)
    d.heartbeat()
    wait(2)

    print("Testing setAllShape")
    d.setAllShape(Shapes.DASH)
    d.heartbeat()
    wait(2)

    print("Testing clear")
    d.clear(1,1)
    d.heartbeat()
    wait(2)

    print("Testing clearAll")
    d.clearAll()
    d.heartbeat()
    wait(2)

    
if __name__ == '__main__':

    main()

