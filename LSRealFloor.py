### Implementation of the Lightsweeper floor
from LSRealTile import LSRealTile
from LSRealTile import lsOpen

import time
import os
import random
import Colors
import Shapes
import json
from collections import defaultdict
from Move import Move
from LSAudio import Audio

# Maximum speed of loop before serial corruption (on 24 tiles split between two com ports)
OURWAIT = 0.005

#handles all communications with RealTile objects, serving as the interface to the
#actual lightsweeper floor. thus updates are pushed to it (display) and also pulled from it
#(sensor changes)
class LSRealFloor():
    COLS = 8
    ROWS = 6
    SENSOR_THRESHOLD = 230
    sharedSerials = dict()


    def __init__(self, rows=ROWS, cols=COLS, serials=None):
        fileName = 'Bfloor' # Testing
        self.rows = rows
        self.cols = cols
        print("RealFloor init", rows, cols)

        tilepile = lsOpen()

        for port in tilepile.lsMatrix:
            newSerial = tilepile.lsSerial(port)
            self.sharedSerials[newSerial.name] = (newSerial)
        print("Shared serials are: " + repr(self.sharedSerials.keys()))  #debugging

        self.addressToRowColumn = {}
        # make all the rows
        self.tileRows = []
        conf = lsConfig(fileName)
        print("Loaded " + str(conf.rows) + " rows and " + str(conf.cols) + " columns (" + str(conf.cells) + " tiles)")
                
        for row in conf.board:
            tiles = []
            self.tileAddresses = []
            for col in conf.board[row]:
                (port, address) = conf.board[row][col]
                tile = LSRealTile(self.sharedSerials[port])
                tile.comNumber = port

                tile.assignAddress(address)
                self.addressToRowColumn[(address,port)] = (row, col)
                tile.setColor(Colors.WHITE)
                tile.setShape(Shapes.ZERO)
                print("address assigned:", tile.getAddress())
                tiles.append(tile)
                wait(.1)
            self.tileRows.append(tiles)
            
        return


    def heartbeat(self):
        pass


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


    def pollSensors(self):
        sensorsChanged = []
        tiles = self._getTileList(0,0)
        for tile in tiles:
            val = tile.sensorStatus()
            if val < self.SENSOR_THRESHOLD:
                rowCol = self.addressToRowColumn[(tile.address, tile.comNumber)]
                move = Move(rowCol[0], rowCol[1], val)
                sensorsChanged.append(move)
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



        
class lsConfig:

    def __init__(self, configFile):
        
        config = self.loadConfig(configFile)
        self._parseConfig(config)

        
    def loadConfig(self, fileName):
        print("Loading board mappings from " + fileName)
        with open(fileName) as configFile:    
            return json.load(configFile)


    def _parseConfig(self, config):
        def defdict():
            return defaultdict(int)
        self.cells = 0
        self.rows = 0
        self.cols = 0
        self.board = defaultdict(defdict)
        for (row, col, port, addr) in config:
            self.cells += 1
            if row >= self.rows:
                self.rows = row + 1
            if col >= self.cols:
                self.cols = col + 1
            self.board[row][col] = (port, addr)
        
            
        

def wait(seconds):
    # self.pollSensors()
    currentTime = time.time()
    while time.time() - currentTime < seconds:
        pass


def playRandom8bitSound(audio):
    val = random.randint(0, 10)
    if val is 0:
        audio.playSound("8bit/10.wav")
    if val is 1:
        audio.playSound("8bit/12.wav")
    if val is 2:
        audio.playSound("8bit/13.wav")
    if val is 3:
        audio.playSound("8bit/15.wav")
    if val is 4:
        audio.playSound("8bit/16.wav")
    if val is 5:
        audio.playSound("8bit/23.wav")
    if val is 6:
        audio.playSound("8bit/34.wav")
    if val is 7:
        audio.playSound("8bit/38.wav")
    if val is 8:
        audio.playSound("8bit/46.wav")
    if val is 9:
        audio.playSound("8bit/Reveal_G_4.wav")
    if val is 10:
        audio.playSound("8bit/Reveal_G_2.wav")


def playRandomCasioSound(audio):
    val = random.randint(0, 7)
    if val is 0:
        audio.playSound("8bit/casio_C_2.wav")
    if val is 1:
        audio.playSound("8bit/casio_C_3.wav")
    if val is 2:
        audio.playSound("8bit/casio_C_4.wav")
    if val is 3:
        audio.playSound("8bit/casio_C_5.wav")
    if val is 4:
        audio.playSound("8bit/casio_C_6.wav")
    if val is 5:
        audio.playSound("8bit/casio_D.wav")
    if val is 6:
        audio.playSound("8bit/casio_E.wav")
    if val is 7:
        audio.playSound("8bit/casio_G.wav")


if __name__ == "__main__":
    print("todo: testing RealFloor")
    audio = Audio()
    floor = LSRealFloor(3, 3)
    #audio.playSound("8bit/46.wav")
    #wait(5)
    print("Clearing floor")
    #call not implemented yet
    #floor.setSegmentsCustom(0, 0, [Colors.RED, Colors.YELLOW, Colors.GREEN, Colors.CYAN, Colors.BLUE, Colors.VIOLET, Colors.WHITE])
    while True:
        floor.RAINBOWMODE()
        floor.RAINBOWMODE_NoAddress(0.01)
        print("detecting changes")
        shitChanged = floor.pollSensors_NoAddress(60)
        playCasio = random.randint(0, 3)
        if playCasio is 0:
            playRandomCasioSound(audio)
        #shitChanged = []
        for change in shitChanged:
            tile = LSRealTile(floor.sharedSerials[change[1]])
            tile.assignAddress(change[0])
            tile.setColor(Colors.RANDOM())
            #playRandom8bitSound(audio)
            val = random.randint(0, 2)
            if val is 0:
                audio.playSound("8bit/46.wav")
            else:
                playRandom8bitSound(audio)
