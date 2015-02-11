import sys
# Lightsweeper additions
from LSApi import LSApi
from LSEmulateTile import EmulateTile
from Move import Move
import Colors
import pygame

class EmulateFloor(LSApi):

    def __init__(self, rows, cols):
        print("Making the screen")
        self.screen = pygame.display.set_mode((800, 800))
        self.rows = rows
        self.cols = cols
        self.tiles = []
        for r in range(0,rows):
            self.tiles.append([])
            for c in range(0, cols):
                self.tiles[r].append(EmulateTile(self, r, c))

    def heartbeat(self):
        #gets the images from the individual tiles, blits them in succession
        #print("heartbeat drawing floor")
        background = pygame.Surface((800, 800))
        background.fill(Colors.BLACK)
        self.screen.blit(background, (0,0))
        for r in range(0, self.rows):
            for c in range(0, self.cols):
                tile = self.tiles[r][c]
                image = tile.loadImage()
                self.screen.blit(image, (100 * r, 100 * c))
        pygame.display.update()

    def _flushQueue(self):
        pass

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
        pass

    def handleTileSensed(self, row, col):
        pass

    def setColor(self, row, column, color, setItNow = True):
        #tileList = self._getTileList(row, column)
        #for tile in tileList:
        tile = self.tiles[row][column]
        tile.setColor(color, setItNow)

    def setShape(self, row, col, shape):
        tile = self.tiles[row][col]
        tile.setShape(shape)

    # set immediately or queue these segments in addressed tiles
    # segments is a byte
    def setSegments(self, row, col, segments, setItNow = True):
        tile = self.tileRows[row][col]
        tile.setSegments(segments)

    def setSegmentsCustom(self, row, col, colors):
        tile = self.tileRows[row][col]
        tile.setSegmentsCustom(colors)

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

if __name__ == "__main__":
    print("testing EmulateFloor")
    floor = EmulateFloor(3, 3)
    #floor.setDigit(0, 0, 0)
