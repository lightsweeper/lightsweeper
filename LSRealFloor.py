### Implementation of the Lightsweeper floor
from LSRealTile import LSRealTile
from serial import Serial
from serial import SerialException
import time
import os
import random
import Colors
import Shapes
from Move import Move
from LSAudio import Audio

#handles all communications with RealTile objects, serving as the interface to the
#actual lightsweeper floor. thus updates are pushed to it (display) and also pulled from it
#(sensor changes)
class LSRealFloor():
    COLS = 8
    ROWS = 6
    SENSOR_THRESHOLD = 230

    def __init__(self, rows=ROWS, cols=COLS, serials=None):
        self.rows = rows
        self.cols = cols
        print("RealFloor init", rows, cols)
        if serials is None:
            # top-left, A1,2,3
            comPort1 = "COM5"
            # top-right, A4,5,6
            comPort2 = "COM6"
            # bottom-left, B1,2,3
            comPort3 = "COM7"
            # bottom-right, B4,5,6
            comPort4 = "COM8"
            availPorts = list(serial_ports())
            print("Available serial ports:" + str(availPorts))
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
            self.sharedSerials = [serial1, serial2, serial3, serial4]
            print("finished with COM ports")
        else:
            self.sharedSerials = serials

        self.addressToRowColumn = {}
        # make all the rows
        self.tileRows = []
        print("Using Jay-Daddy's pickling system")
        pickle = open('floor_config', 'r')
        self.tileRows = []
        for i in range(rows):
            self.tileRows.append([])
            for j in range(cols):
                self.tileRows[i].append(None)

        for line in pickle:
            line = (line).strip('()\n').replace('\'', '')
            line = tuple(line.split(','))
            comNumber = int(line[2]) - 1
            tile = LSRealTile(self.sharedSerials[comNumber])
            tile.comNumber = comNumber
            address = int(line[3])
            tile.assignAddress(address)
            row = int(line[0])
            col = int(line[1])
            self.addressToRowColumn[(address, comNumber)] = (row, col)
            tile.setColor(Colors.WHITE)
            tile.setShape(Shapes.ZERO)
            print("storing tile:", row, col)
            self.tileRows[row][col] = tile

        for i in range(rows):
            s = ""
            for j in range(cols):
                tile = self.tileRows[i][j]
                if tile is None:
                    s += "No" + '\t'
                else:
                    s += str(tile.getAddress()) + "\t"
            print(s)

        print("Real floor done instantiating")
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
        self.pollSensors()
        for row in self.tileRows:
            for tile in row:
                tile.setColor(Colors.RED)
                tile.setShape(126)
        wait(updateFrequency)
        for row in self.tileRows:
            for tile in row:
                tile.setColor(Colors.YELLOW)
                tile.setShape(126)
        wait(updateFrequency)
        for row in self.tileRows:
            for tile in row:
                tile.setColor(Colors.GREEN)
                tile.setShape(126)
        wait(updateFrequency)
        for row in self.tileRows:
            for tile in row:
                tile.setColor(Colors.CYAN)
                tile.setShape(126)
        wait(updateFrequency)
        for row in self.tileRows:
            for tile in row:
                tile.setColor(Colors.BLUE)
                tile.setShape(126)
        wait(updateFrequency)
        for row in self.tileRows:
            for tile in row:
                tile.setColor(Colors.VIOLET)
                tile.setShape(126)
        wait(updateFrequency)
        for row in self.tileRows:
            for tile in row:
                tile.setColor(Colors.WHITE)
                tile.setShape(126)
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
    # TODO: Linux

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
    floor.clearboard()
    while True:
        print("RAINBOWMODE: BLIND EDITION")
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