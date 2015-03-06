from lsfloor import LSRealFloor
from LSFloorConfigure import LSFloorConfig
import lsfloor

import Shapes
import Colors
import random
import time
import pygame
from pygame.locals import *


wait = time.sleep

# Tweaks LSFloor to update pygame emulator
class EmulateFloor(lsfloor.LSFloor):

    def __init__(self, rows=0, cols=0):
        # Call parent init
        lsfloor.LSFloor.__init__(self, rows=rows, cols=cols)

        width=cols*100
        height=rows*100
        print("Making the screen ({:d}x{:d})".format(width,height))
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))


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

class Move():
    def __init__(self, row, col, val):
        self.row = row
        self.col = col
        self.val = val

#handles animations as well as allowing a common controller for displaying
#the state of the game on the real floor, on a simulated floor, on the console, or
#any combination thereof
class LSDisplay():


    def __init__(self, rows=None, cols=None, realFloor = False, simulatedFloor = False, console = False, eventCallback=None, initScreen=True, conf=None):
        if conf is None:
            if rows is None or cols is None:
                conf = LSFloorConfig()
                conf.selectConfig()
            else:
                conf = LSFloorConfig(rows=rows, cols=cols)

        if conf.containsVirtual() is True:
            realFloor = False

        self.rows = conf.rows
        self.cols = conf.cols
        self.eventCallback = eventCallback
        self.lastTileSetTimestamp = time.time()
        self.shapes = dict()
        self.colors = dict()

        if realFloor:
            print("Display instantiating real floor")
            self.realFloor = LSRealFloor(conf=conf, eventCallback=self.handleTileStepEvent)
        else:
            self.realFloor = None
        self.floor = []
        for r in range(self.rows):
            self.floor.append([])
            for c in range(self.cols):
                self.floor[r].append('-')
        self.console = console
        if simulatedFloor:
            print("Display instantiating simulated floor")
            self.simulatedFloor = EmulateFloor(self.rows, self.cols)
        else:
            self.simulatedFloor = None
        if initScreen is True:
            self.splash()

            if self.simulatedFloor:
                self.simulatedFloor.heartbeat()
            wait(6.0)


    def splash(self):
        if self.rows > 1 and self.cols > 7:
            self.setAllColor(Colors.BLACK)
            #LIGHTSWEEPER
            self.set(0, 1, Shapes.L, Colors.RED)
            self.set(0, 2, Shapes.I, Colors.YELLOW)
            self.set(0, 3, Shapes.G, Colors.GREEN)
            self.set(0, 4, Shapes.H, Colors.BLUE)
            self.set(0, 5, Shapes.T, Colors.MAGENTA)
            self.set(1, 0, Shapes.S, Colors.RED)
            self.set(1, 1, Shapes.u, Colors.YELLOW)
            self.set(1, 2, Shapes.V, Colors.YELLOW)
            self.set(1, 3, Shapes.E, Colors.GREEN)
            self.set(1, 4, Shapes.E, Colors.CYAN)
            self.set(1, 5, Shapes.P, Colors.BLUE)
            self.set(1, 6, Shapes.E, Colors.MAGENTA)
            self.set(1, 7, Shapes.R, Colors.WHITE)
        else:
            self.setAllColor(Colors.RANDOM())

    #this is to handle display functions only
    def heartbeat(self):
        if self.simulatedFloor:
            self.simulatedFloor.heartbeat()
        if self.realFloor:
            self.realFloor.heartbeat()
        #check pygame for position and click ness of mouse
        pass

    def handleTileStepEvent(self, row, col, val):
        if self.eventCallback is not None:
            self.eventCallback(row, col, val)

    def pollSensors(self):
        sensorsChanged = []
        if self.realFloor:
            sensorsChanged += self.realFloor.pollSensors()
        if self.simulatedFloor:
            sensorsChanged += self.simulatedFloor.pollSensors()
        if self.console and not self.realFloor:
            self.printFloor()
            consoleIn = input("Type in the next move")
            consoleIn = consoleIn.split(',')
            move = Move(int(consoleIn[0]), int(consoleIn[1]), 0)
            sensorsChanged.append(move)
        #we want to ensure we never return a NoneType
        if sensorsChanged is None:
            return []
        return sensorsChanged


    def set(self, row, col, shape, color):
        if self.realFloor:
            self.realFloor.set(row, col, shape, color)
        if self.simulatedFloor:
            self.simulatedFloor.set(row, col, shape, color)
        self.shapes[(row, col)] = shape
        self.colors[(row, col)] = color
        # wait(0.005)

    def setAll(self, shape, color):
        if self.realFloor:
            self.realFloor.setAll(shape, color)
        if self.simulatedFloor:
            self.simulatedFloor.setAll(shape, color)
        self.allShapes(shape)
        self.allColors(color)

    #colors is a list of seven colors in A,...,G order of segments
    def setCustom(self, row, col, segments):
        if self.simulatedFloor:
            self.simulatedFloor.setSegments(row, col, segments)
        if self.realFloor:
            self.realFloor.setSegments(row, col, segments)

    def setAllCustom(self, segments):
        if self.simulatedFloor:
            self.simulatedFloor.setSegmentsAll(segments)
        if self.realFloor:
            self.realFloor.setSegmentsAll(segments)
        

    def setColor(self, row, col, color):
        if self.realFloor:
            self.realFloor.setColor(row, col, color)
        if self.simulatedFloor:
            self.simulatedFloor.setColor(row, col, color)
        self.colors[(row, col)] = color
        # wait(0.005)

    def setAllColor(self, color):
        if self.realFloor:
            self.realFloor.setAllColor(color)
        if self.simulatedFloor:
            self.simulatedFloor.setAllColor(color)
        self.allColors(color)

    def setShape(self, row, col, shape):
        if self.realFloor:
            self.realFloor.setShape(row, col, shape)
        if self.simulatedFloor:
            self.simulatedFloor.setShape(row, col, shape)
        self.shapes[(row, col)] = shape

    def setAllShape(self, shape):
        if self.realFloor:
            self.realFloor.setAllShape(shape)
        if self.simulatedFloor:
            self.simulatedFloor.setAllShape(shape)
        self.allShapes(shape)

    def setMessage(self, row, message, color = Colors.WHITE, start = 0, cutoff = -1):
        if cutoff is -1:
            cutoff = self.cols
        shapes = Shapes.stringToShapes(message)
        col = start
        while col < cutoff and len(shapes) > 0:
            self.set(row, col, shapes.pop(0), color)
            col += 1

    def setMessageSplit(self, row, message1, message2, color = Colors.WHITE):
        #first determine which tile is the middle--this one must be left blank
        middle = int(self.cols / 2)
        self.setMessage(row, message1, color, cutoff=middle)
        self.setMessage(row, message2, color, start=middle+1)
        #fill left side of middle with message1, left side with message2
        #TODO: ability to favor one message or the other, preferentially cutting off the less-favored one

    def showHighScores(self, highScores):
        self.setAll(Shapes.ZERO, Colors.BLACK)
        self.setMessage(0,"HIGH", color=Colors.BLUE)
        self.setMessage(1,"SCORES", color=Colors.GREEN)
        row = 2
        while row < self.rows and len(highScores) > 0:
            score = highScores.pop(0)
            self.setMessageSplit(row, score[0], score[1])
            row += 1

    def clear(self, row, col):
        if self.realFloor:
            self.realFloor.blank(row, col)
        if self.simulatedFloor:
            self.simulatedFloor.blank(row, col)
        self.shapes[(row, col)] = Shapes.OFF
        self.colors[(row, col)] = Colors.BLACK

    def clearAll(self):
        if self.realFloor:
            self.realFloor.clearBoard()
        if self.simulatedFloor:
            self.simulatedFloor.clearBoard()
        self.allShapes(Shapes.OFF)
        self.allColors(Colors.BLACK)

#    def setSegmentsCustom(self, row, col, colors):
#        pass

    def hasShapeChangesFor(self, row, col):
        val = True
        try:
            self.shapes[(row, col)]
        except:
            val = False
        return val

    def hasColorChangesFor(self, row, col):
        val = True
        try:
            self.colors[(row, col)]
        except:
            val = False
        return val

    def setFrame(self):
        self.heartbeat()
        self.colors = dict()
        self.shapes = dict()

    def getShape(self, row, col):
        return self.shapes[(row, col)]

    def getColor(self, row, col):
        return self.colors[(row, col)]

    def allShapes(self, shape):
        for row in range(self.rows):
            for col in range(self.cols):
                self.shapes[(row, col)] = shape

    def allColors(self, color):
        for row in range(self.rows):
            for col in range(self.cols):
                self.colors[(row, col)] = color

    def add(self, row, col, shape, color):
        pass

    def addCustom(self, row, col, colors):
        pass

    def addAnimation(self, row, col, animation, loops):
        pass


def main():
    print("Testing LSDisplay realfloor and emulatedfloor")
    display = LSDisplay(3, 8, True, True, False)

    for j in range(8):
        display.setColor(0, j, Colors.RED)
        display.setShape(0, j, Shapes.ZERO)
    wait(0.2)
    for j in range(8):
        display.setColor(1, j, Colors.YELLOW)
        display.setShape(1, j, Shapes.ZERO)
    wait(0.2)
    for j in range(8):
        display.setColor(2, j, Colors.GREEN)
        display.setShape(2, j, Shapes.ZERO)
    wait(0.2)
    for i in range(3):
        for j in range(8):
            display.setShape(i, j, Shapes.digitToHex(i))
            wait(0.01)
    wait(0.2)
    for i in range(0, 100):
        display.heartbeat()
        #display.setColor(random.randint(0, display.row-1), random.randint(0, display.cols-1), Colors.RANDOM())
        #display.setShape(random.randint(0, display.row-1), random.randint(0, display.cols-1), Shapes.randomDigitInHex())


if __name__ == '__main__':
    main()
