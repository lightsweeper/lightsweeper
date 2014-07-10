from PyQt5.QtWidgets import (QGroupBox, QHBoxLayout,QVBoxLayout)

# Lightsweeper additions
from PyQt5.QtWidgets import (QFrame)
from LSApi import LSApi
from LSEmulateTile import LSEmulateTile

class LSEmulateFloor(QGroupBox, LSApi):

    def __init__(self, rows=6, cols=8):
        super(QGroupBox, self).__init__("Lightsweeper Floor Emulator")
        self.rows = rows
        self.cols = cols
        self.setContentsMargins(0,0,0,0)
        floorLayout = QVBoxLayout()
        floorLayout.setContentsMargins(0,0,0,0)

        # make all the rows
        self.tileRows = []
        for row in range(rows):
            thisRow = QFrame()
            #thisRow.setContentsMargins(0,0,0,0)
            layout = QHBoxLayout()
            layout.setContentsMargins(0,0,0,0) # collapses space between rows
            tiles = []
            # make the LSEmulateTile in each row
            for col in range(cols):
                tile = LSEmulateTile(row, col)
                #tile.setContentsMargins(0,0,0,0)
                tiles.append(tile)
                count = len(tiles)
                layout.addWidget(tile)
                #tile.setColor("white")
                thisRow.setLayout(layout)

            self.tileRows.append(tiles)
            floorLayout.addWidget(thisRow)

        self.setLayout(floorLayout)
        # is that all ?

    def flushQueue(self):
        for row in self.tileRows:
            for tile in row:
                tile.flushQueue()

    def getTileList (self, row, column):
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

    def setColor(self, row, column, color, setItNow = True):
        tileList = self.getTileList(row, column)
        for tile in tileList:
            tile.setColor(color, setItNow)

    # set immediately or queue these segments in addressed tiles
    # segments is a seven-tuple interpreted as True or False
    def setSegments(self, row, column, segments, setItNow = True):
        tileList = self.getTileList(row, column)
        for tile in tileList:
            tile.setSegments(segments, setItNow)

    def setDigit(self, row, column, digit, setItNow = True):
        tileList = self.getTileList(row, column)
        for tile in tileList:
            tile.setDigit(digit, setItNow)
