# Lightsweeper additions
from LSApi import LSApi
import Colors
import Shapes
import pygame
from LSEmulateSevenSegment import LSEmulateSevenSegment

# this class holds a seven segment display and a button to mimic the pressure sensor
# it does no segment processing, it just passes thru to the seven segment display
class EmulateTile(LSApi):
    def __init__(self, floor, row=0, col=0, labelTiles = False):
        self.row = row
        self.col = col
        self.floor = floor
        self.color = Colors.BLACK
        self.shape = Shapes.ZERO
        if labelTiles:
            self.post = "_labels.png"
        else:
            self.post = ".png"

    def flushQueue(self):
        pass

    def setColor (self, newColor, setItNow = True):
        #change the state.
        self.color = newColor
        if not setItNow:
            print("[LSEmulateTile] Non-instantaneous setting not yet supported.")

    def getColor(self):
        return self.color

    def setShape(self, shape, setItNow = True):
        self.shape = shape

    def getShape(self):
        return self.shape

    def loadImage(self):
        shape = self.getShape()
        image = pygame.image.load("images/blank_tile.png")
        if shape & Shapes.SEG_A:
            seg = pygame.image.load("images/seg_A" + self.post)
            seg.fill(Colors.intToRGB(self.getColor()), special_flags=pygame.BLEND_RGBA_MULT)
            image.blit(seg, (0,0))
        if shape & Shapes.SEG_B:
            seg = pygame.image.load("images/seg_B" + self.post)
            seg.fill(Colors.intToRGB(self.getColor()), special_flags=pygame.BLEND_RGBA_MULT)
            image.blit(seg, (0,0))
        if shape & Shapes.SEG_C:
            seg = pygame.image.load("images/seg_C" + self.post)
            seg.fill(Colors.intToRGB(self.getColor()), special_flags=pygame.BLEND_RGBA_MULT)
            image.blit(seg, (0,0))
        if shape & Shapes.SEG_D:
            seg = pygame.image.load("images/seg_D" + self.post)
            seg.fill(Colors.intToRGB(self.getColor()), special_flags=pygame.BLEND_RGBA_MULT)
            image.blit(seg, (0,0))
        if shape & Shapes.SEG_E:
            seg = pygame.image.load("images/seg_E" + self.post)
            seg.fill(Colors.intToRGB(self.getColor()), special_flags=pygame.BLEND_RGBA_MULT)
            image.blit(seg, (0,0))
        if shape & Shapes.SEG_F:
            seg = pygame.image.load("images/seg_F" + self.post)
            seg.fill(Colors.intToRGB(self.getColor()), special_flags=pygame.BLEND_RGBA_MULT)
            image.blit(seg, (0,0))
        if shape & Shapes.SEG_G:
            seg = pygame.image.load("images/seg_G" + self.post)
            seg.fill(Colors.intToRGB(self.getColor()), special_flags=pygame.BLEND_RGBA_MULT)
            image.blit(seg, (0,0))
        return image

    # set immediately or queue these segments in addressed tiles
    # segments is a seven-tuple interpreted as True or False
    def setSegments(self, segments, setItNow = True):
        #change the state.
        pass

    def setSegmentsCustom(self, colors):
        #change the state.
        pass

    def setDigit (self, newDigit, setItNow = True):
        #change the state.
        pass

    def getSensors(self):
        if self.button.isChecked():
            return (self.row, self.col)
        else:
            return None

    def getTileList (self, row, column):
        return (self.row, self.col)

    def getCol (self):
        return self.col

    def getRow (self):
        return self.row

    #returns an object that EmulateFloor can simply blit in the right place.
    def getRenderable(self):
        return None

    def _display (self, val):
        return

    def _getButtonState(self):
        return self.button.isChecked()


    def _buttonPressed(self):
        print("Button state is", self.button.isChecked(), self.row, self.col)
        self.floor.handleTileSensed(self.row, self.col)

    ### Implementation of the Lightsweeper API
    def destroy(self):
        return


    def setTransition(self, transition):
        return

    def set(self,color=0, shape=0, transition=0):
        if (color != 0):
            self.setColor(color)
        if (shape != 0 ):
            self.setShape(shape)
        if(transition != 0):
            self.setTransition(transition)
        return

    def update(self,type):
        if (type == 'NOW'):
            return
        elif (type == 'CLOCK'):
            return
        elif (type == 'TRIGGER'):
            return
        else:
            return

    def version(self):
        return 1

    def blank(self):
        self.setColor('black')
        return

    def locate(self):
        return

    def demo (self, seconds):
        return

    def setAnimation(self):
        return

    def flip(self):
        return

    def status(self):
        return

    def reset(self):
        return

    def latch(self):
        return

    def unregister(self):
        return

    def assignAddress(self, address):
        self.address = address

    def getAddress(self):
        return self.address

    def calibrate(self):
        return

    def read(self):
        return self._getButtonState()
