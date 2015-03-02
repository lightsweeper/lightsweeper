import lsfloor
from lsfloor import LSRealFloor
import Shapes
import Colors
import random
from Move import Move
import time
import pygame

class EmulateFloor(lsfloor.LSFloor):

    def __init__(self, rows=0, cols=0):
        # Call parent init
        lsfloor.LSFloor.__init__(self, rows=rows, cols=cols)

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

#handles animations as well as allowing a common controller for displaying
#the state of the game on the real floor, on a simulated floor, on the console, or
#any combination thereof
class Display():
    def __init__(self, rows, cols, realFloor = False, simulatedFloor = False, console = False, eventCallback=None, initScreen=True):
        self.rows = rows
        self.cols = cols
        self.eventCallback = eventCallback
        self.lastTileSetTimestamp = time.time()
        if realFloor:
            print("Display instantiating real floor")
            self.realFloor = LSRealFloor(rows, cols, eventCallback=self.handleTileStepEvent)
        else:
            self.realFloor = None
        self.floor = []
        for r in range(rows):
            self.floor.append([])
            for c in range(cols):
                self.floor[r].append('-')
        self.console = console
        if simulatedFloor:
            print("Display instantiating simulated floor")
            self.simulatedFloor = EmulateFloor(rows, cols)
        else:
            self.simulatedFloor = None
        if initScreen and rows > 1 and cols > 7:
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

            # self.set(0, 1, Shapes.G, Colors.RED)
            # self.set(0, 2, Shapes.O, Colors.YELLOW)
            # self.set(0, 3, Shapes.O, Colors.GREEN)
            # self.set(0, 4, Shapes.D, Colors.CYAN)
            #
            # self.set(1, 0, Shapes.R, Colors.RED)
            # self.set(1, 1, Shapes.N, Colors.RED)
            # self.set(1, 2, Shapes.O, Colors.YELLOW)
            # self.set(1, 3, Shapes.R, Colors.GREEN)
            # self.set(1, 4, Shapes.N, Colors.CYAN)
            # self.set(1, 5, Shapes.i, Colors.BLUE)
            # self.set(1, 6, Shapes.N, Colors.MAGENTA)
            # self.set(1, 7, Shapes.G, Colors.WHITE)
            #
            # self.set(2, 1, Shapes.D, Colors.RED)
            # self.set(2, 2, Shapes.A, Colors.YELLOW)
            # self.set(2, 3, Shapes.U, Colors.GREEN)
            # self.set(2, 4, Shapes.E, Colors.CYAN)

            if self.simulatedFloor:
                self.simulatedFloor.heartbeat()
            wait(6.0)

    #this is to handle display functions only
    def heartbeat(self):
        #print("Display heartbeat")
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
            sensorsChanged = self.realFloor.pollSensors()
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
        # wait(0.005)

    #colors is a list of seven colors in A,...,G order of segments
    def setCustom(self, row, col, segments):
        if self.simulatedFloor:
            self.simulatedFloor.setCustom(row, col, segments)

    def setColor(self, row, col, color):
        if self.realFloor:
            self.realFloor.setColor(row, col, color)
        if self.simulatedFloor:
            self.simulatedFloor.setColor(row, col, color)
        # wait(0.005)

    def setAllColor(self, color):
        if self.realFloor:
            self.realFloor.setAllColor(color)

    def setShape(self, row, col, shape):
        if self.realFloor:
            self.realFloor.setShape(row, col, shape)
        if self.simulatedFloor:
            self.simulatedFloor.setShape(row, col, shape)
        # wait(0.005)

    def setSegmentsCustom(self, row, col, colors):
        pass

    def setFrame(self, frame):
        for row in range(self.rows):
            for col in range(self.cols):
                #if frame.hasChangesFor(row, col):
                if frame.hasColorChangesFor(row, col):
                    self.setColor(row, col, frame.getColor(row, col))
                if frame.hasShapeChangesFor(row, col):
                    self.setShape(row, col, frame.getShape(row, col))

    def add(self, row, col, shape, color):
        pass

    def addCustom(self, row, col, colors):
        pass

    def addAnimation(self, row, col, animation, loops):
        pass

    def clear(self):
        pass

def wait(seconds):
    # self.pollSensors()
    currentTime = time.time()
    while time.time() - currentTime < seconds:
        pass

def main():
    print("Testing LSDisplay realfloor and emulatedfloor")
    display = Display(3, 8, True, True, False)

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
