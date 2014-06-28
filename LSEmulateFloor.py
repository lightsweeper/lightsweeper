# Lightsweeper classes

from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog,
        QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
        QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit,
        QVBoxLayout)

# Lightsweeper additions
from PyQt5.QtWidgets import (QLCDNumber, QWidget, QFrame, QSpinBox, QStyle, QStyleOption, QToolButton)
from PyQt5.QtGui import (QPainter)

from LSEmulateTile import LSEmulateTile

class LSEmulateFloor(QGroupBox):

    def __init__(self, rows=6, cols=8):
        super(QGroupBox, self).__init__("Lightsweeper Floor Emulator")
        self.rows = rows
        self.cols = cols
        floorLayout = QVBoxLayout()
        self.setContentsMargins(0,0,0,0)

        # make all the rows
        self.tileRows = []
        for row in range(rows):
            thisRow = QFrame()
            thisRow.setContentsMargins(0,0,0,0)
            layout = QHBoxLayout()
            tiles = []
            # make the LSEmulateTile in each row
            for col in range(cols):
                tile = LSEmulateTile(row, col)
                tile.setContentsMargins(0,0,0,0)
                #tile.setMinimumSize(60, 80)
                #tile.display(col+1)
                tile.show()
                tiles.append(tile)
                count = len(tiles)
                layout.addWidget(tile)
                if col == 0:
                    tile.setColor("red")
                elif col == 1:
                    tile.setColor("green")
                elif col == 2:
                    tile.setColor("blue")
                else:
                    tile.setColor("white")
                thisRow.setLayout(layout)

            self.tileRows.append(tiles)
            floorLayout.addWidget(thisRow)

        self.setLayout(floorLayout)
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

    def setColor(self, row, column, color, setItNow = True):
        tileList = self._getTileList(row, column)
        for tile in tileList:
            tile.setColor(color)

    def _setDigit(self, row, column, digit, setItNow = True):
        tileList = self._getTileList(row, column)
        for tile in tileList:
            tile.setShape(digit)

    #Implementation of the Lightsweeper API:

    def printboard(self):
        return

    def clearboard(self):
        return

    def showboard(self):
        return

    def refreshboard(self):
        return

    def resetboard(self):
        return

    def purgetile(self,tile):
        return FALSE 

    def clock(self):
        return


