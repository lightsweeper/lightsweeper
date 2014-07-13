### Implementation of the Lightsweeper floor
from LSRealTile import LSRealTile
from minesweeper.board import Board
from serial import Serial
import time
import random
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
        self.sharedSerial = self.initSerial()
        self.serialOpen = True
        try:
            self.sharedSerial.open()
        except IOError:
            self.serialOpen = False
            print("Serial not open")
        else:
            self.sharedSerial.close()

        # make all the rows
        self.tileRows = []
        #todo: request built-in address from physical tile
        i = 0
        for row in range(rows):
            tiles = []
            self.tileAddresses = []
            for col in range(cols):
                tile = LSRealTile(self.sharedSerial)
                tile.assignAddress(i)
                #print("test getAddress", tile.getAddress())
                i += 1
                tile.setShape(8)
                #assign address
                tiles.append(tile)
            self.tileRows.append(tiles)
        #self.printboard(self.board)
        #self.printToConsole()
        return

    def startLoop(self):
        lastSensorPoll = time.time()
        while self.board.is_playing:
            #print("Waiting for input")
            #s = input('--> ')
            #print("got ", s)
            if time.time() - lastSensorPoll > 1:
                self.pollSensors()
                if not self.serialOpen:
                    self.board.show(random.randrange(0, 8),random.randrange(0, 6))
                lastSensorPoll = time.time()
                self.printboard(self.board)
                self.printToConsole()

    def printAddresses(self):
        s = ""
        for row in range(0,6):
            for col in range(0, 8):
                s += str(self.tileRows[row][col].getAddress()) + " "
            print(s)
            s = ""

    def pollSensors(self):
        tiles = self._getTileList(0,0)
        dataReceived = False
        for tile in tiles:
            val = tile.eepromRead(tile.address)
            if len(val) > 0:
                print("received ", val)
                dataReceived = True
        if not dataReceived:
            print("nothing received")
        return

    def printToConsole(self):
        boardString = ""
        for row in self.tileRows:
            for tile in row:
                boardString += str(tile.getShape())
            print(boardString)
            boardString = ""

    def initSerial(self):
        serial = Serial()
        print("TODO: serial logic")
        return serial

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
        #tiles = self._getTileList(0,0)
        for row in range(0,6):
            for col in range(0,8):
                tile = self.tileRows[row][col]
                if board != None:
                    #(row, col) = (tile.getAddress() // self.cols, tile.getAdddress() % self.cols)
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
