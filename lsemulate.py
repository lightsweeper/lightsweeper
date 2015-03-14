import lsfloor
import Colors

import time
import types

import pygame
from pygame.locals import *


class Move():
    def __init__(self, row, col, val):
        self.row = row
        self.col = col
        self.val = val

wait = time.sleep

def loadImage(self):
 #   self.segments += [Colors.BLACK] * (7 - len(self.segments))
    image = pygame.image.load("images/segments.png")
    horizontal = (42,10)
    vertical = (10,30)
    segMap = [(29,10),(71,17),(71,52),(29,79),(19,52),(19,17),(29,45)]
    image.fill(Colors.intToRGB(self.segments["a"]), pygame.Rect(segMap[0],horizontal))
    image.fill(Colors.intToRGB(self.segments["b"]), pygame.Rect(segMap[1],vertical))
    image.fill(Colors.intToRGB(self.segments["c"]), pygame.Rect(segMap[2],vertical))
    image.fill(Colors.intToRGB(self.segments["d"]), pygame.Rect(segMap[3],horizontal))
    image.fill(Colors.intToRGB(self.segments["e"]), pygame.Rect(segMap[4],vertical))
    image.fill(Colors.intToRGB(self.segments["f"]), pygame.Rect(segMap[5],vertical))
    image.fill(Colors.intToRGB(self.segments["g"]), pygame.Rect(segMap[6],horizontal))
    return image

# Tweaks LSFloor to update pygame emulator
class LSPygameFloor(lsfloor.LSFloor):

    def __init__(self, rows=0, cols=0):
        # Call parent init
        lsfloor.LSFloor.__init__(self, rows=rows, cols=cols)

        width=cols*100
        height=rows*100
        print("Making the screen ({:d}x{:d})".format(width,height))
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        for tile in self.tileList:
            tile.loadImage = types.MethodType(loadImage, tile) # Bind the loadImage function to each tile


    def heartbeat(self):
        #gets the images from the individual tiles, blits them in succession
        #print("heartbeat drawing floor")
        background = pygame.Surface(((self.cols*100), (self.rows*100)))
        background.fill(Colors.BLACK)
        self.screen.blit(background, (0,0))
        for r in range(self.rows):
            for c in range(self.cols):
                tile = self.tiles[r][c]
                image = tile.loadImage()
                self.screen.blit(image, (100 * c, 100 * r))
        pygame.display.update()


    def pollSensors(self):
        sensorsChanged = []
        reading = 1
        for event in pygame.event.get():
            rowCol = self._whereDidIPutMyMouse(pygame.mouse.get_pos())
            if event.type == QUIT:
                exit()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                exit()
            if event.type == MOUSEBUTTONUP:
                print("Clicked off {:d},{:d} ({:d})".format(rowCol[0], rowCol[1],reading)) # Debugging
            if event.type == MOUSEBUTTONDOWN:
                print("Clicked on {:d},{:d} ({:d})".format(rowCol[0], rowCol[1],reading)) # Debugging
                move = Move(rowCol[0], rowCol[1], reading)
                sensorsChanged.append(move)
                self.handleTileStepEvent(rowCol[0], rowCol[1], reading)
        return sensorsChanged

    def _whereDidIPutMyMouse(self, mousePointer):
        (x, y) = mousePointer
        col = int(x/100)
        row = int(y/100)
        return (row,col)