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

    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    VIOLET = 5
    CYAN = 6
    WHITE = 7

    def __init__(self, rows=ROWS, cols=COLS, mines=MINES, serials=None):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        print("RealFloor init", rows, cols, mines)
        # Initialize board
        self.board = Board()
        self.board.create_board(self.rows, self.cols, self.mines)
        print("board created")
        #tile = LSRealTile(serial)
        #tile.assignAddress(40)
        #tile.setColor(5)
        #tile.setShape(2)
        self.sharedSerials = serials
        self.addressToRowColumn = {}
        # make all the rows
        self.tileRows = []
        pickle = open('floor_config', 'r')
        print(pickle)
        i = 0
        for row in range(rows):
            tiles = []
            self.tileAddresses = []
            for col in range(cols):
                line = (pickle.readline()).strip('()\n').replace('\'','')
                line = tuple(line.split(','))
                print(line)
                # the COM entry should just be the number 1, 2, 3, or 4 instead of the COM port.
                # 1 being top-left, 4 bottom-right
                comNumber = int(line[2]) - 1
                tile = LSRealTile(serials[comNumber])
                tile.comNumber = comNumber
                address = int(line[3])
                tile.assignAddress(address)
                self.addressToRowColumn[(address,comNumber)] = (row, col)
                print("address assigned:", tile.getAddress())
                #print("test getAddress", tile.getAddress())
                i += 1
                tile.setColor(LSRealFloor.YELLOW)
                tile.setDigit(8)
                #assign address
                tiles.append(tile)
            self.tileRows.append(tiles)
        #self.printboard(self.board)
        #self.printToConsole()
        return

    def startLoop(self):
        lastSensorPoll = time.time()
        while self.board.is_playing:
            if time.time() - lastSensorPoll > 3:
                sensors = self.pollSensors()
                ghost = False
                if ghost: #not self.serialOpen:
                    #have a ghost step on random tiles
                    print("ghost step")
                    self.board.show(random.randrange(0, self.rows),random.randrange(0, self.cols))
                lastSensorPoll = time.time()
                print("printing board")
                self.printboard(self.board)
                self.printToConsole()
        print("A winner or loser is you!")
        lastSensorPoll = time.time()
        while not self.board.is_playing:
            # do win screen

            if time.time() - lastSensorPoll > 7:
                #reset to initial state
                self.board.is_playing = True
                for row in self.tileRows:
                    for tile in row:
                        tile.setColor(LSRealFloor.YELLOW)
                        tile.setShape(1)

    def printAddresses(self):
        s = ""
        for row in range(0,self.rows):
            for col in range(0, self.cols):
                s += str(self.tileRows[row][col].getAddress()) + " "
            print(s)
            s = ""

    def pollSensors(self):
        tiles = self._getTileList(0,0)
        dataReceived = False
        for tile in tiles:
            val = tile.eepromRead(tile.address)
            if val and len(val) > 0:
                print("received ", val)
                self.handleTileSensed(tile.address, tile.comNumber)
        if not dataReceived:
            print("no poll data received")
        return None

    def handleTileSensed(self, address, comNumber):
        rowCol = self.addressToRowColumn[(address, comNumber)]
        self.tileRows[rowCol[0]][rowCol[1]].show()
        pass

    def printToConsole(self):
        boardString = ""
        for row in self.tileRows:
            for tile in row:
                boardString += str(tile.getShape()) + " "
            print(boardString)
            boardString = ""

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
        print(self.rows, self.cols)
        for row in range(0,self.rows):
            for col in range(0,self.cols):
                tile = self.tileRows[row][col]
                if board != None:
                    #(row, col) = (tile.getAddress() // self.cols, tile.getAdddress() % self.cols)
                    cell = board.mine_repr(row, col)
                    if cell == "D":
                            #Defused
                            tile.setColor(LSRealFloor.VIOLET)
                            tile.setsShape(1)
                    elif cell == '.':
                            tile.setColor(LSRealFloor.GREEN)
                            tile.setDigit(0)
                    elif cell == ' ' or cell == '':
                            tile.setColor(LSRealFloor.BLACK)
                            tile.setDigit(8)
                    elif cell == 'M':
                            tile.setColor(LSRealFloor.RED)
                            tile.setDigit(8)
                    elif cell == 'F':
                            break
                    else:
                            tile.setColor(LSRealFloor.YELLOW)
                            tile.setDigit(int(cell))
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
