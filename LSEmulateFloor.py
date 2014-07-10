# Lightsweeper classes

from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog,
        QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
        QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit,
        QVBoxLayout)

# Lightsweeper additions
from PyQt5.QtWidgets import (QLCDNumber, QWidget, QFrame, QSpinBox, QStyle, QStyleOption, QToolButton)
from PyQt5.QtGui import (QPainter)

from LSEmulateTile import LSEmulateTile

#Basic Minesweeper classes
from board import Board, Cell

class LSEmulateFloor(QGroupBox):

    def __init__(self, board, rows=6, cols=8):
        super(QGroupBox, self).__init__("Lightsweeper Floor Emulator")
        self.rows = rows
        self.cols = cols
        self.board = board 
        floorLayout = QVBoxLayout()
        self.setContentsMargins(0,0,0,0)

        # make all the rows
        self.tileRows = []
        for row in range(rows):
            #print("creating row:", row) 
            thisRow = QFrame()
            thisRow.setContentsMargins(0,0,0,0)
            layout = QHBoxLayout()
            tiles = []
            tileAddresses = []
            # make the LSEmulateTile in each row
            for col in range(cols):
                tile = LSEmulateTile(self, row, col)
                tile.setContentsMargins(0,0,0,0)
                tile.assignAddress(row*cols+col)
                tile.blank()
        
                # Debug: 
                #print(tile.getAddress())
                
                tileAddresses.append((row, col))
                #tile.setMinimumSize(60, 80)
                #tile.display(col+1)
                tile.show()
                tiles.append(tile)
                count = len(tiles)
                layout.addWidget(tile)
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

    def init(self, rows, cols):
        __init__(self,rows, cols)
        return

    def printboard(self,board=None):
        print("printboard")
        tiles = self._getTileList(0,0)
        for tile in tiles:
            if board != None:
                (row, col) = (tile.getAddress() // self.cols, tile.getAddress() % self.cols)
                #print( "Printing:", row, col)
                cell = board.mine_repr(row,col)
                if cell == '.':
                    tile.blank()
                    #print(row, col, "blank")
                elif cell == 'M':
                    tile.setColor("red")
                    tile.setShape("8")
                    tile.update('NOW')
                    print("mine!")
                elif cell == 'F':
                    print(row, col, "Flagged")
                    break
                else:
                    print("Setting shape to:", cell) 
                    tile.setColor("black")
                    tile.setShape(cell)
                    tile.update('NOW')
                    print(row, col, "setting to", cell)
            tile.update('NOW')
        return
        
    def clearboard(self):
        tiles = self._getTileList(0,0)
        for tile in tiles:
            tile.blank()
        return

    def showboard(self):
        tiles = self._getTileList(0,0)
        for tile in tiles:
            tile.show()
        self.printboard(self.board)
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
        return FALSE

    def show(self,row,col):
        tile = LSEmulateTile(self, row, col)
        print("showing tile", row, col, tile)
        cell = self.board.mine_repr(row,col)
        if cell == '.':
            blank()
            #print(row, col, "blank")
        elif cell == 'M':
            tile.setColor("red")
            tile.setShape("8")
            tile.update('NOW')
            print("mine!")
        elif cell == 'F':
            print(row, col, "Flagged")
        else:
            print("Setting shape to:", cell) 
            tile.setColor("black")
            tile.setShape(cell)
            tile.update('NOW')
            print(row, col, "setting to", cell)
            tile.update('NOW')
        tile.show()
        #tile.update('NOW')
		
    def clock(self):
        tiles = self._getTileList(0,0)
        for tile in tiles:
            try:
                tile.read()
            except:
                print ("unexpected error on tile", tileAddresses[tile.getAddress()])
        self.refreshboard()
        return TRUE

    def get_move(self, row, col):
        self.board.get_move(row, col)

