import sys
# Lightsweeper additions
from lsfloor import LSFloor
from LSEmulateTile import EmulateTile
from Move import Move
import Colors

import pygame
import time

class EmulateFloor(LSFloor):

    def __init__(self, rows=0, cols=0):
        # Call parent init
        LSFloor.__init__(self, rows=rows, cols=cols)

        print("Making the screen")
        self.screen = pygame.display.set_mode((800, 800))


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


if __name__ == "__main__":
    print("testing EmulateFloor")
    floor = EmulateFloor(3, 3)
    #floor.setDigit(0, 0, 0)
