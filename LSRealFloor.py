### Implementation of the Lightsweeper floor
from LSRealTile import LSRealTile
from minesweeper.board import Board
from serial import Serial
import LSApi

class LSRealFloor():

    COLS = 8
    ROWS = 6
    MINES = 9

    def __init__(self):
        rows = 6
        cols = 8
        mines = 9
        self.rows = 6
        self.cols = 8
        self.mines = 9
        # Initialize board
        self.board = Board()
        self.board.create_board(self.rows, self.cols, self.mines)
        print("board created")

        #make sharedSerial
        self.sharedSerial = Serial()

        # make all the rows
        self.tileRows = []
        for row in range(rows):
            tiles = []
            self.tileAddresses = []
            for col in range(cols):
                tile = LSRealTile(self.sharedSerial)
                #assign address
                tiles.append(tile)
                self.tileRows.append(tiles)
                return

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

    def printboard(self, board):
        tiles = self._getTileList(0,0)
        for tile in tiles:
            if board != None:
                (row, col) = (tile.getAddress() // self.cols, tile.getAdddress() % self.cols)
                cell = board.mine_repr(row, col)
                if cell == "D":
                        #Defused
                        tile.setColor("violet")
                        tile.setsShape("-")
                elif cell == '.':
                        tile.setColor("green")
                        tile.setShape("0")
                elif cell == ' ' or cell == '':
                        tile.setColor("black")
                        tile.setShape("8")
                elif cell == 'M':
                        tile.setColor("red")
                        tile.setShape("8")
                elif cell == 'F':
                        break
                else:
                        tile.setColor("yellow")
                        tile.setShape(cell)
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
        return False

    def clock(self):
        return
