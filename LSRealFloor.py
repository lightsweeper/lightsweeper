### Implementation of the Lightsweeper floor
from LSRealTile import LSRealTile
from minesweeper.board import Board
from serial import Serial
import time
import random
import winsound

class LSRealFloor():
    COLS = 8
    ROWS = 6
    MINES = 9

    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    VIOLET = 5  # Really more pink than violet
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
        pickle = open('floor_small_config', 'r')
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
                tile.setColor(LSRealFloor.BLACK)
                tile.setShape(1)
                tile.setDebug(0)
                #assign address
                tiles.append(tile)
            self.tileRows.append(tiles)
        for row in self.tileRows:
            for tile in row:
                tile.setShape(1)
                tile.setColor(LSRealFloor.YELLOW)
        #self.printboard(self.board)
        #self.printToConsole()

        #create calibration dictionary
        self.tileMinPressure = {}
        self.tileMaxPressure = {}
        for row in self.tileRows:
            for tile in row:
                self.tileMinPressure[(tile.address, tile.comNumber)] = 255
                self.tileMaxPressure[(tile.address, tile.comNumber)] = 0
        return

    def startLoop(self):
        #winsound.Beep(400, 300)
        #self.playSong()
        # use to turn on and off game
        game =  True
        # use to turn on and off other modes
        interactiveMode = False
        self.rainbowMode = False
        self.board.is_playing = True
        # animating tiles
        #self.animFrame = 0
        lastSensorPoll = time.time()
        wonGame = False
        while True:
            self.playSong()
            self.blankFloor()
            if self.board.is_playing and game:
                print("* * * minesweeper * * *")
            while self.board.is_playing and game:
                if time.time() - lastSensorPoll > 0.2:
                    self.pollSensors()
                    lastSensorPoll = time.time()
                    if self.board.is_solved():
                        self.board.set_all_defused()
                        print("Well done! You solved the board!")
                        wonGame = True
                    elif not self.board.is_playing:
                        print("Uh oh! You blew up!")
                        self.board.show_all()
                        wonGame = False
                        winsound.PlaySound('sounds/Explosion.wav', winsound.SND_FILENAME and winsound.SND_ASYNC)jkkkkkkkhjkl
                    self.printboard(self.board)
            self.wait(3)
            if wonGame and game:
                print("A winner is you!")
                winsound.PlaySound('sounds/Success.wav', winsound.SND_FILENAME and winsound.SND_ASYNC)
                self.RAINBOWMODE()
                self.RAINBOWMODE()
                self.RAINBOWMODE()
            elif game:
                print("You lost! Insert coins to continue")
                winsound.PlaySound('sounds/Explosion.wav', winsound.SND_FILENAME and winsound.SND_ASYNC)
                self.setAllColor(LSRealFloor.RED)
                for row in self.tileRows:
                    for tile in row:
                        tile.setDigit(8)
                blargflarg = time.time()
                black = False
                while time.time() - blargflarg < 4:
                    #if random.randint(0, 20) is 1:
                    #    winsound.PlaySound('sounds/Explosion.wav', winsound.SND_FILENAME and winsound.SND_ASYNC)
                    self.wait(0.1)
                    if black:
                        self.setAllColor(LSRealFloor.RED)
                        black = False
                    else:
                        self.setAllColor(LSRealFloor.BLACK)
                        black = True
            self.board.create_board(self.rows, self.cols, random.randint(2,3))
            self.blankFloor()
            self.wait(1)
            if interactiveMode:
                print("__interactive mode__")
                self.wait(2)
                self.setAllColor(LSRealFloor.BLACK)
                self.wait(45)
            self.blankFloor()
            if self.rainbowMode:
                # wait for it
                self.wait(2)
                print("~~~~~RAINBOWMODE ENGAGE~~~~~")
                self.RAINBOWMODE()
                self.RAINBOWMODE()
                self.RAINBOWMODE()
                self.RAINBOWMODE()
                self.RAINBOWMODE()
            self.blankFloor()

    def wait(self, seconds):
        # self.pollSensors()
        lastSensorPoll = time.time()
        while time.time() - lastSensorPoll < seconds:
            pass

    def setAllColor(self, color):
        for row in self.tileRows:
            for tile in row:
                tile.setColor(color)

    def playSong(self):
        rand = random.randint(0,3)
        if rand is 0:
            print("playing 1")
            winsound.PlaySound('sounds/BetweenGames1.wav', winsound.SND_FILENAME and winsound.SND_LOOP and winsound.SND_ASYNC)
        if rand is 1:
            print("playing 2")
            winsound.PlaySound('sounds/BetweenGames2.wav', winsound.SND_FILENAME and winsound.SND_LOOP and winsound.SND_ASYNC)
        if rand is 2:
            print("playing 3")
            winsound.PlaySound('sounds/BetweenGames3.wav', winsound.SND_FILENAME and winsound.SND_LOOP and winsound.SND_ASYNC)
        if rand is 3:
            print("playing 4")
            winsound.PlaySound('sounds/BetweenGames4.wav', winsound.SND_FILENAME and winsound.SND_LOOP and winsound.SND_ASYNC)

    def blankFloor(self):
        #for row in self.tileRows:
        #    for tile in row:
        #        tile.setColor(LSRealFloor.BLACK)
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

    def RAINBOWMODE(self):
        self.pollSensors()
        updateFrequency = 0.4
        for row in self.tileRows:
            for tile in row:
                tile.setColor(LSRealFloor.WHITE)
                tile.setShape(126)
        self.wait(updateFrequency)
        for row in self.tileRows:
            for tile in row:
                tile.setColor(LSRealFloor.YELLOW)
                tile.setShape(126)
        self.wait(updateFrequency)
        for row in self.tileRows:
            for tile in row:
                tile.setColor(LSRealFloor.GREEN)
                tile.setShape(126)
        self.wait(updateFrequency)
        for row in self.tileRows:
            for tile in row:
                tile.setColor(LSRealFloor.CYAN)
                tile.setShape(126)
        self.wait(updateFrequency)
        for row in self.tileRows:
            for tile in row:
                tile.setColor(LSRealFloor.BLUE)
                tile.setShape(126)
        self.wait(updateFrequency)
        for row in self.tileRows:
            for tile in row:
                tile.setColor(LSRealFloor.VIOLET)
                tile.setShape(126)
        self.wait(updateFrequency)
        for row in self.tileRows:
            for tile in row:
                tile.setColor(LSRealFloor.WHITE)
                tile.setShape(126)

    def printAddresses(self):
        s = ""
        for row in range(0,self.rows):
            for col in range(0, self.cols):
                s += str(self.tileRows[row][col].getAddress()) + " "
            #print(s)
            s = ""

    def pollSensors(self):
        # the minimum difference between min and max sensor values required for a sensor to be sensed
        minMaxSpread = 100
        tiles = self._getTileList(0,0)
        for tile in tiles:
            val = tile.sensorStatus()
            min = self.tileMinPressure[(tile.address, tile.comNumber)]
            max = self.tileMaxPressure[(tile.address, tile.comNumber)]
            if min > val:
                self.tileMinPressure[(tile.address, tile.comNumber)] = val
            if max < val:
                self.tileMaxPressure[(tile.address, tile.comNumber)] = val
            #if max > min + minMaxSpread and val < (max - min) / 20 + min:
            if val < 12:
                if not self.rainbowMode:
                    self.handleTileSensed(tile.address, tile.comNumber)
                print("tile sensed: ", tile.address, tile.comNumber, "min=",min, "val=", val, "max=", max)
            #elif not max > min + 20:
            #    print("window not reached", tile.address, tile.comNumber)
        return None

    def handleTileSensed(self, address, comNumber):
        rowCol = self.addressToRowColumn[(address, comNumber)]
        if not self.board.board[rowCol[0]][rowCol[1]].is_visible:
            winsound.PlaySound('sounds/BetweenGames1.wav', winsound.SND_FILENAME and winsound.SND_LOOP and winsound.SND_ASYNC)
            winsound.PlaySound('sounds/Blop.wav', winsound.SND_FILENAME and winsound.SND_ASYNC)
        self.board.show(rowCol[0], rowCol[1])
        if self.board.showingMultiple:
            winsound.PlaySound('sounds/Reveal.wav', winsound.SND_FILENAME and winsound.SND_ASYNC)
        pass

    def printToConsole(self):
        boardString = ""
        for row in self.tileRows:
            for tile in row:
                boardString += str(tile.getShape()) + " "
            #print(boardString)
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
        lastTileUpdated = time.time()
        #print(self.rows, self.cols)
        for row in range(0,self.rows):
            for col in range(0,self.cols):
                tile = self.tileRows[row][col]
                while time.time() - lastTileUpdated < 0.01:
                    pass
                lastTileUpdated = time.time()
                if board != None:
                    #(row, col) = (tile.getAddress() // self.cols, tile.getAdddress() % self.cols)
                    cell = board.mine_repr(row, col)
                    if cell == "D":
                            #Defused
                            tile.setColor(LSRealFloor.VIOLET)
                            tile.setShape(1)
                            print("DEFUSED")
                    elif cell == '.':
                            tile.setColor(LSRealFloor.GREEN)
                            tile.setDigit(0)
                    elif cell == ' ' or cell == '':
                            tile.setColor(LSRealFloor.BLACK)
                            tile.setDigit(8)
                    elif cell == 'M':
                            # mine symbol
                            tile.setColor(LSRealFloor.RED)
                            tile.setShape(1)
                     #       tile.setShape(55)  # "X"
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
