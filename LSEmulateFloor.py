from PyQt5.QtWidgets import (QGroupBox, QHBoxLayout,QVBoxLayout)

# Lightsweeper additions
from PyQt5.QtWidgets import (QFrame)
from LSApi import LSApi
from LSEmulateTile import LSEmulateTile

class LSEmulateFloor(QGroupBox, LSApi):

    def __init__(self, rows=6, cols=8, board=None):
        super(QGroupBox, self).__init__("Lightsweeper Floor Emulator")
        self.rows = rows
        self.cols = cols
        self.board = board
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
            tileAddresses = []
            # make the LSEmulateTile in each row
            for col in range(cols):
                tile = LSEmulateTile(self, row, col)
                #tile.setContentsMargins(0,0,0,0)
                tile.assignAddress(row*cols+col)
                tile.blank()
        
                # Debug: 
                # print(tile.getAddress())
                
                tileAddresses.append((row, col))
                #tile.setMinimumSize(60, 80)
                #tile.display(col+1)
                # tile.show()
                tiles.append(tile)
                count = len(tiles)
                layout.addWidget(tile)
                tile.setColor("black")
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
            tile.setColor(color, setItNow)

    # set immediately or queue these segments in addressed tiles
    # segments is a seven-tuple interpreted as True or False
    def setSegments(self, row, column, segments, setItNow = True):
        tileList = self.getTileList(row, column)
        for tile in tileList:
            tile.setSegments(segments, setItNow)

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

    def printboard(self,board=None):
        tiles = self._getTileList(0,0)
        for tile in tiles:
            if board != None:
                (row, col) = (tile.getAddress() // self.cols, tile.getAddress() % self.cols)
                cell = board.mine_repr(row,col)
                # print( "Printing:", row, col, "cell: ", cell)
                if cell == '.' or cell == ' ' or cell == '':
                    # tile.blank()
                    # tile.update('NOW')
                    tile.setColor("black")
                    tile.setShape("8")
                    tile.update('NOW')
                elif cell == 'M':
                    tile.setColor("red")
                    tile.setShape("8")
                    tile.update('NOW')
                elif cell == 'F':
                    break
                else:
                    print("Setting shape to:", cell)
                    tile.setColor("blue")
                    tile.setShape(cell)
                    tile.update('NOW')
            tile.update('NOW')
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
                print ("unexpected error on tile", tileAddresses[tile.getAddress()])
        self.refreshboard()
        return True

    # Minesweeper specific addition
    def get_move(self, row, col):
        tiles = self._getTileList(0,0)

        print("Got move for", row, col)
        
        row_id = row
        col_id = col
        is_flag = False

        if self.board is None:
            return

        if self.board.is_playing and not self.board.is_solved:
            if (row_id <0 or col_id < 0):
                print ("invalid row or col")
                return
            if not is_flag:
                # print( "Showing:", row_id, col_id, "on: ", self.board)
    #            channelA.play(blop_sound)
                self.board.show(row_id, col_id)
            else:
                self.board.flag(row_id, col_id)
            self.printboard(self.board)


        if self.board.is_solved:
    #        channelA.play(success_sound)
            print("Well done! You solved the board!")
        elif not self.board.is_playing:
    #        channelA.play(explosion_sound)
            print("Uh oh! You blew up!")
            self.board.showall()
            self.printboard(self.board)
            #self.refreshboard()
        return
