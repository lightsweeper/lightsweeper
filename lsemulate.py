""" Contains methods to emulate LightSweeper floors on your computer """

import lsfloor
import Colors

import os
import random
import sys
import time
import types

import pygame
from pygame.locals import *

wait = time.sleep


class LSEmulateFloor(lsfloor.LSFloor):

    def init(self):
        """
            This method gets called once when the emulator becomes initialized.
            Use this to set up any environment your emulator needs to operate.
        """
        pass
    
    def heartbeat(self):
        """
            This method gets called at the end of each heartbeat. Use this
            to update your display.
        """
        pass
        
    def pollEvents(self):
        """
            This method should be a generator that yields tuples of the form
            (row, col, sensor-reading)
        """
        pass


# Tweaks LSFloor to update pygame emulator
class LSPygameFloor(LSEmulateFloor):

    
    
    def init(self):

        pygame.init()

        width=self.cols*100
        height=self.rows*100
        print("Making the screen ({:d}x{:d})".format(width,height))
        pygame.display.init()

        self.screen = pygame.display.set_mode((width, height))
        self.background = pygame.Surface(self.screen.get_size())
        self.background.fill(Colors.intToRGB(Colors.BLACK))
        systemFonts = pygame.font.get_fonts()
        monoFonts = [f for f in systemFonts if "mono" in f.lower()]
        if len(monoFonts) is 0:
            useFont = random.choice(systemFonts)
        else:
            useFont = random.choice(monoFonts)
        if "freemono" in systemFonts:   # I like it
            useFont = "freemono"
        self.font = pygame.font.SysFont(useFont, 14)


    def heartbeat(self):
        #gets the images from the individual tiles, blits them in succession
        self.screen.blit(self.background, (0,0))
        for r in range(self.rows):
            for c in range(self.cols):
                tile = self.tiles[r][c]
                image = self._loadImage(tile)
                self.screen.blit(image, (100 * c, 100 * r))
        pygame.display.update()

    def _addText(self, text, surface, pos):
        surfaceMeta = surface.get_rect()
        text = self.font.render(text, 1, Colors.intToRGB(Colors.WHITE))
        textMeta = text.get_rect()
        if str(pos[0]) == "center":
            pos = (surfaceMeta.width/2 - textMeta.width/2, pos[1])
        if str(pos[1]) == "center":
            pos = (pos[0], surfaceMeta.height/2 - textMeta.height/2)
        surface.blit(text, pos)
        return(surface)

    def _loadImage(self, tile):
        try:
            t = self._root.tiles[tile.row][tile.col].sensor
        except AttributeError:
            t = 0
        image = pygame.Surface((100, 100))
        if t is not 0:
            image = self._addText(str(t), image, ("center",25))
        horizontal = (42,10)
        vertical = (10,30)
        segMap = [(29,10),(71,17),(71,52),(29,79),(19,52),(19,17),(29,45)]
        image.fill(Colors.intToRGB(tile.segments["a"]), pygame.Rect(segMap[0],horizontal))
        image.fill(Colors.intToRGB(tile.segments["b"]), pygame.Rect(segMap[1],vertical))
        image.fill(Colors.intToRGB(tile.segments["c"]), pygame.Rect(segMap[2],vertical))
        image.fill(Colors.intToRGB(tile.segments["d"]), pygame.Rect(segMap[3],horizontal))
        image.fill(Colors.intToRGB(tile.segments["e"]), pygame.Rect(segMap[4],vertical))
        image.fill(Colors.intToRGB(tile.segments["f"]), pygame.Rect(segMap[5],vertical))
        image.fill(Colors.intToRGB(tile.segments["g"]), pygame.Rect(segMap[6],horizontal))
        return image


    def pollEvents(self):
        level = 50
        while True:
            for event in pygame.event.get():
             #   print(event)                   # Debugging
                rowCol = self._whereDidIPutMyMouse(pygame.mouse.get_pos())
                if event.type == QUIT:
                    self.saveAndExit(0)
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    self.saveAndExit(0)
                if event.type == MOUSEBUTTONDOWN:
                    if event.button is 1: # Left mouse button
                        lastClick = rowCol
                        print(level)
                        yield((rowCol[0], rowCol[1], level))
                    elif event.button is 4: # Mousewheel up
                        if level < 100:
                            level += 10
                            if level > 100:
                                level = 100
                            print(level)
                            yield((rowCol[0], rowCol[1], level))
                    elif event.button is 5: # Mousewheel down
                        if level > 0:
                            level -= 10
                            print(level)
                            yield((rowCol[0], rowCol[1], level))
                if event.type == MOUSEBUTTONUP:
                 #   print("Clicked off {:d},{:d} ({:d})".format(rowCol[0], rowCol[1],reading)) # Debugging
                    if event.button is 1:
                        yield((lastClick[0], lastClick[1], 0))

    def _whereDidIPutMyMouse(self, mousePointer):
        (x, y) = mousePointer
        col = int(x/100)
        row = int(y/100)
        return (row,col)
