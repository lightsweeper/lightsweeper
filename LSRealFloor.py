### Implementation of the Lightsweeper floor
from LSRealTile import LSRealTile
from LSRealTile import lsOpen

import time
import os
import random
import Colors
import Shapes
from Move import Move
from LSAudio import Audio
from LSFloorConfigure import lsFloorConfig
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
        if configFile is None:
            try:
                floorFiles = list(filter(lambda ls: ls.endswith(".floor"), os.listdir("./")))
            except:
                raise IOError("No floor configuration found. Try running LSFloorConfigure.py")
            if len(floorFiles) is 1:
                fileName = floorFiles[0]
            else:
                print("\nFound multiple configurations: \n")
                fileName = userSelect(floorFiles, "\nWhich floor configuration would you like to use? ")
        else:
            fileName = configFile
            

        # Load the configuration
        conf = lsFloorConfig(fileName)
        self.rows = conf.rows
        self.cols = conf.cols
        self.eventCallback = eventCallback
        print("RealFloor init", self.rows, self.cols)

        # Initialize the serial ports
        tilepile = lsOpen()

        # Initialize calibration map
        self.calibrationMap = dict()

        self.addressToRowColumn = {}
        # single-dimensional array of tiles to iterate over
        self.tileList = []
        # double array of tile objects
        self.tileRows = []
        print("Loaded " + str(conf.rows) + " rows and " + str(conf.cols) + " columns (" + str(conf.cells) + " tiles)")
                
        for row in conf.board:
            tiles = []
            self.tileAddresses = []
            for col in conf.board[row]:
                (port, address) = conf.board[row][col]
                tile = LSRealTile(tilepile.sharedSerials[port])
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
                #print("Address assigned:", tile.getAddress())
                wait(.01)
            self.tileRows.append(tiles)
            
        return

    def heartbeat(self):
        pass

    def handleTileStepEvent(self, row, col, val):
        if self.eventCallback is not None:
            self.eventCallback(row, col, val)

    def setAllColor(self, color):
        for row in self.tileRows:
            for tile in row:
                tile.setColor(color)


    def set(self, row, col, shape, color):
        tile = self.tileRows[row][col];
        tile.setColor(color)
        tile.setShape(shape)

    def setColor(self, row, col, color):
        tile = self.tileRows[row][col]
        tile.setColor(color)


    def setShape(self, row, col, shape):
        tile = self.tileRows[row][col]
        tile.setShape(shape)


    def setSegmentsCustom(self, row, col, segments):
        tile = self.tileRows[row][col]
        tile.setSegmentsCustom(segments)


    def RAINBOWMODE(self, updateFrequency = 0.4):
        for row in self.tileRows:
            for tile in row:
                tile.setColor(Colors.RED)
                tile.setShape(126)
                wait(OURWAIT)
        wait(updateFrequency)
        for row in self.tileRows:
            for tile in row:
                tile.setColor(Colors.YELLOW)
                tile.setShape(126)
                wait(OURWAIT)
        wait(updateFrequency)
        for row in self.tileRows:
            for tile in row:
                tile.setColor(Colors.GREEN)
                tile.setShape(126)
                wait(OURWAIT)
        wait(updateFrequency)
        for row in self.tileRows:
            for tile in row:
                tile.setColor(Colors.CYAN)
                tile.setShape(126)
                wait(OURWAIT)
        wait(updateFrequency)
        for row in self.tileRows:
            for tile in row:
                tile.setColor(Colors.BLUE)
                tile.setShape(126)
                wait(OURWAIT)
        wait(updateFrequency)
        for row in self.tileRows:
            for tile in row:
                tile.setColor(Colors.VIOLET)
                tile.setShape(126)
                wait(OURWAIT)
        wait(updateFrequency)
        for row in self.tileRows:
            for tile in row:
                tile.setColor(Colors.WHITE)
                tile.setShape(126)
                wait(OURWAIT)
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
                    
    # Old code:
#            val = tile.sensorStatus()
#            if val < self.SENSOR_THRESHOLD:
#                rowCol = self.addressToRowColumn[(tile.address, tile.comNumber)]
#                move = Move(rowCol[0], rowCol[1], val)
#                sensorsChanged.append(move)

        return sensorsChanged

    def _getTileList(self,row,column):
        tileList = []
        #whole floor
        # whole floor
        if row < 1 and column < 1:
            for tileRow in self.tileRows:
                for tile in tileRow:
                    tileList.append(tile)
                    count = len(tileList)
        # whole row
        elif column < 1:
            tileRow = self.tileRows[row-1]
            for tile in tileRow:
                tileList.append(tile)
                count = len(tileList)
        # whole column
        elif row < 1:
            for tileRow in self.tileRows:
                tile = tileRow[column-1]
                tileList.append(tile)
                count = len(tileList)
        # single tile
        else:
            tileRow = self.tileRows[row-1]
            tileList = [tileRow[column-1]]
        return tileList


    def clearboard(self):
        zeroTile = LSRealTile(self.sharedSerials[0])
        zeroTile.assignAddress(0)
        zeroTile.blank()
        zeroTile = LSRealTile(self.sharedSerials[1])
        zeroTile.assignAddress(0)
        zeroTile.blank()
        zeroTile = LSRealTile(self.sharedSerials[2])
        zeroTile.assignAddress(0)
        zeroTile.blank()
        zeroTile = LSRealTile(self.sharedSerials[3])
        zeroTile.assignAddress(0)
        zeroTile.blank()


    def RAINBOWMODE_NoAddress(self, interval):
        #print("RAINBOWMODE: BLIND EDITION")
        for ii in range(10):
            randTile = LSRealTile(self.sharedSerials[random.randint(0, 3)])
            randTile.assignAddress(random.randint(0, 200))
            randTile.setColor(Colors.RANDOM())
            randTile.setShape(random.randint(0, 127))


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
    print("todo: testing RealFloor")
    floor = LSRealFloor()
    #audio.playSound("8bit/46.wav")
    #wait(5)
    print("Clearing floor")
    #call not implemented yet
    #floor.setSegmentsCustom(0, 0, [Colors.RED, Colors.YELLOW, Colors.GREEN, Colors.CYAN, Colors.BLUE, Colors.VIOLET, Colors.WHITE])
    while True:
        floor.RAINBOWMODE()
