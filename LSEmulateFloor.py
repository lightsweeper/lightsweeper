from PyQt5.QtWidgets import (QGroupBox, QHBoxLayout,QVBoxLayout)

# Lightsweeper additions
from PyQt5.QtWidgets import (QFrame)
from LSApi import LSApi
from LSEmulateTile import LSEmulateTile
from Move import Move
import Colors

class LSEmulateFloor(QGroupBox, LSApi):
    COLS = 8
    ROWS = 6
    MINES = 9

    def __init__(self, rows=ROWS, cols=COLS):
        super(QGroupBox, self).__init__("Lightsweeper Floor Emulator")
        self.rows = rows
        self.cols = cols
        self.sensorsChanged = []
        # Initialize board
        # self.board.set_display(self)
        self.setContentsMargins(0,0,0,0)
        self.floorLayout = QVBoxLayout()
        self.floorLayout.setContentsMargins(0,0,0,0)

        # make all the rows
        self.tileRows = []
        for row in range(rows):
            self.thisRow = QFrame()
            #thisRow.setContentsMargins(0,0,0,0)
            self.layout = QHBoxLayout()
            self.layout.setContentsMargins(0,0,0,0) # collapses space between rows
            tiles = []
            self.tileAddresses = []
            # make the LSEmulateTile in each row
            for col in range(cols):
                tile = LSEmulateTile(self, row, col)
                #tile.setContentsMargins(0,0,0,0)
                tile.assignAddress(row*cols+col)
                tile.blank()
                
                self.tileAddresses.append((row, col))
                #tile.setMinimumSize(60, 80)
                #tile.display(col+1)
                # tile.show()
                tiles.append(tile)
                count = len(tiles)
                self.layout.addWidget(tile)
                tile.setColor("black")
                self.thisRow.setLayout(self.layout)

            self.tileRows.append(tiles)
            self.floorLayout.addWidget(self.thisRow)

        print("tiles in window:", self.floorLayout.count())
        self.setLayout(self.floorLayout)
        # is that all ?

    def _flushQueue(self):
        for row in self.tileRows:
            for tile in row:
                tile.flushQueue()

    def _getTileList (self, row, column):
        tileList = []
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
    
    def _getCols (self):
        return self.cols

    def _getRows (self):
        return self.rows

    def pollSensors(self):
        result = []
        for change in self.sensorsChanged:
            result.append(change)
        self.sensorsChanged = []
        return result

    def handleTileSensed(self, row, col):
        print("got move", row, col)
        move = Move(row, col, 0)
        self.sensorsChanged.append(move)

    def setColor(self, row, column, color, setItNow = True):
        tileList = self._getTileList(row, column)
        for tile in tileList:
            tile.setColor(Colors.intToName(color), setItNow)

    # set immediately or queue these segments in addressed tiles
    # segments is a byte
    def setSegments(self, row, col, segments, setItNow = True):
        tile = self.tileRows[row][col]
        tile.setSegments(segments)
        #tileList = self.getTileList(row, column)
        #for tile in tileList:
        #    tile.setSegments(segments, setItNow)

    def setDigit(self, row, column, digit, setItNow = True):
        tileList = self._getTileList(row, column)
        for tile in tileList:
            tile.setDigit(digit, setItNow)

    def getSensors(self):
        activeSensors = []
        for row in self.tileRows:
            for tile in row:
                sensorChecked = tile.getSensors()
                if sensorChecked:
                    activeSensors.append(sensorChecked)
        return activeSensors

    #Implementation of the Lightsweeper API:
    def init(self, rows, cols):
        # __init__(self, rows, cols)
        return

    def clearboard(self):
        tiles = self._getTileList(0,0)
        for tile in tiles:
            tile.blank()
        return

    def showboard(self):
        return

    def refreshboard(self):
        tiles = self._getTileList(0,0)
        for tile in tiles:
            tile.update('CLOCK')
        return

    def resetboard(self):
        for row in self.tileRows:
            for tile in row:
                tile.reset()
        return

    def purgetile(self,tile):
        return False

    def clock(self):
        tiles = self._getTileList(0,0)
        for tile in tiles:
            try:
                tile.read()
            except:
                print ("unexpected error on tile", self.tileAddresses[tile.getAddress()])
        self.refreshboard()
        return True