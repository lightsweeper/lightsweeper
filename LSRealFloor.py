### Implementation of the Lightsweeper floor
from LSRealTile import LSRealTile
from serial import Serial
from serial import SerialException
import time
import winsound
import os
import Colors
import Shapes
from Move import Move

#handles all communications with RealTile objects, serving as the interface to the
#actual lightsweeper floor. thus updates are pushed to it (display) and also pulled from it
#(sensor changes)
class LSRealFloor():
    COLS = 8
    ROWS = 6
    MINES = 9

    def __init__(self, rows=ROWS, cols=COLS, serials=None):
        self.rows = rows
        self.cols = cols
        print("RealFloor init", rows, cols)
        if serials is None:
            # top-left, A1,2,3
            comPort1 = "COM5"
            # top-right, A4,5,6
            comPort2 = "COM12"
            # bottom-left, B1,2,3
            comPort3 = "COM13"
            # bottom-right, B4,5,6
            comPort4 = "COM15"
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
        pickle = open('floor_small_config', 'r')
        #print(pickle)
        i = 0
        for row in range(rows):
            tiles = []
            self.tileAddresses = []
            for col in range(cols):
                line = (pickle.readline()).strip('()\n').replace('\'','')
                line = tuple(line.split(','))
                # the COM entry should just be the number 1, 2, 3, or 4 instead of the COM port.
                # 1 being top-left, 4 bottom-right
                comNumber = int(line[2]) - 1
                tile = LSRealTile(self.sharedSerials[comNumber])
                tile.comNumber = comNumber
                address = int(line[3])
                tile.assignAddress(address)
                self.addressToRowColumn[(address,comNumber)] = (row, col)
                tile.setColor(Colors.WHITE)
                tile.setShape(Shapes.ZERO)
                #print("address assigned:", tile.getAddress())
                #print("test getAddress", tile.getAddress())
                i += 1
                #assign address
                tiles.append(tile)
            self.tileRows.append(tiles)
        return

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
            if val < 15:
                #self.handleTileSensed(tile.address, tile.comNumber)
                rowCol = self.addressToRowColumn[(tile.address, tile.comNumber)]
                move = Move(rowCol[0], rowCol[1], val)
                sensorsChanged.append(move)
                #print("tile sensed: ", tile.address, tile.comNumber, "min=",min, "val=", val, "max=", max)
        return sensorsChanged

    def handleTileSensed(self, address, comNumber):
        rowCol = self.addressToRowColumn[(address, comNumber)]
        if not self.board.board[rowCol[0]][rowCol[1]].is_visible:
            winsound.PlaySound('sounds/BetweenGames1.wav', winsound.SND_FILENAME and winsound.SND_LOOP and winsound.SND_ASYNC)
            winsound.PlaySound('sounds/Blop.wav', winsound.SND_FILENAME and winsound.SND_ASYNC)
        self.board.show(rowCol[0], rowCol[1])
        if self.board.showingMultiple:
            winsound.PlaySound('sounds/Reveal.wav', winsound.SND_FILENAME and winsound.SND_ASYNC)
        pass

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

if __name__ == "__main__":
    print("todo: testing RealFloor")
    floor = LSRealFloor(3, 3)
    #call not implemented yet
    #floor.setSegmentsCustom(0, 0, [Colors.RED, Colors.YELLOW, Colors.GREEN, Colors.CYAN, Colors.BLUE, Colors.VIOLET, Colors.WHITE])
    floor.RAINBOWMODE(0.1)
    print("Floor should be displaying things now")
    floor.RAINBOWMODE(0.1)
    floor.RAINBOWMODE(0.1)
    while True:
        floor.RAINBOWMODE(1)
