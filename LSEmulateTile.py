# Lightsweeper additions
from lightsweeper import LSApi
import Colors
import Shapes
import pygame

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
        self.set(self.shape, self.color)

    def flushQueue(self):
        pass

    def set(self, shape=Shapes.ZERO, color=Colors.BLACK):
        self.segments = []
        if shape & Shapes.SEG_A:
            self.segments.append(color)
        else:
            self.segments.append(Colors.BLACK)
        if shape & Shapes.SEG_B:
            self.segments.append(color)
        else:
            self.segments.append(Colors.BLACK)
        if shape & Shapes.SEG_C:
            self.segments.append(color)
        else:
            self.segments.append(Colors.BLACK)
        if shape & Shapes.SEG_D:
            self.segments.append(color)
        else:
            self.segments.append(Colors.BLACK)
        if shape & Shapes.SEG_E:
            self.segments.append(color)
        else:
            self.segments.append(Colors.BLACK)
        if shape & Shapes.SEG_F:
            self.segments.append(color)
        else:
            self.segments.append(Colors.BLACK)
        if shape & Shapes.SEG_G:
            self.segments.append(color)
        else:
            self.segments.append(Colors.BLACK)

    def setShape(self, shape):
        pass
        
    def setColor(self, shape):
        pass
        
    def setCustom(self, segments):
        self.segments = segments
        pass

    def getShape(self):
        return self.shape

    def loadImage(self):
        image = pygame.image.load("images/segments.png")
        horizontal = (42,10)
        vertical = (10,30)
        image.fill(Colors.intToRGB(self.segments[0]), pygame.Rect((29,10),horizontal))
        image.fill(Colors.intToRGB(self.segments[1]), pygame.Rect((71,17),vertical))
        image.fill(Colors.intToRGB(self.segments[2]), pygame.Rect((71,52),vertical))
        image.fill(Colors.intToRGB(self.segments[3]), pygame.Rect((29,79),horizontal))
        image.fill(Colors.intToRGB(self.segments[4]), pygame.Rect((19,52),vertical))
        image.fill(Colors.intToRGB(self.segments[5]), pygame.Rect((19,17),vertical))
        image.fill(Colors.intToRGB(self.segments[6]), pygame.Rect((29,45),horizontal))
        return image

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
