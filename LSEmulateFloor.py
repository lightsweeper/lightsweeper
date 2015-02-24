import sys
# Lightsweeper additions
from LSApi import LSApi
from LSEmulateTile import EmulateTile
from Move import Move
import Colors
import pygame
import time

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
        for r in range(self.rows):
            for c in range(self.cols):
                tile = self.tiles[r][c]
                image = tile.loadImage()
                self.screen.blit(image, (100 * c, 100 * r))
        pygame.display.update()

    def _flushQueue(self):
        pass

    def pollSensors(self):
        pass

    def handleTileSensed(self, row, col):
        pass

    def set(self, row, col, shape, color):
        tile = self.tiles[row][col]
        tile.set(shape, color)

    #segments is a list of seven colors in A,...,G order of segments
    def setCustom(self, row, col, segments):
        tile = self.tiles[row][col]
        tile.setCustom(segments)

    def clear(self, row, col):
        tile = self.tiles[row][col]
        tile.set()

    def clearAll(self):
        for tile in self.tiles:
            tile.set()

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
