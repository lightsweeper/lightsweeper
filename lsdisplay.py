""" The main point of interface to the LightSweeper API. Launches simulated and real floors (if available) and keeps them in sync """

from lsfloor import LSRealFloor
from lsemulate import LSPygameFloor
from LSFloorConfigure import LSFloorConfig

import Shapes
import Colors
import time

wait = time.sleep
EmulateFloor = LSPygameFloor # Use pygame as the emulator

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
         #   wait(6.0)


    def splash(self):
        if self.rows > 1 and self.cols > 7:
            self.setAllColor(Colors.BLACK)
            #LIGHTSWEEPER
            self.set(0, 1, Shapes.L, Colors.RED)
            self.set(0, 2, Shapes.I, Colors.YELLOW)
            self.set(0, 3, Shapes.G, Colors.GREEN)
            self.set(0, 4, Shapes.h, Colors.BLUE)
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

    def setAll(self, shape, color):
        if self.realFloor:
            self.realFloor.setAll(shape, color)
        if self.simulatedFloor:
            self.simulatedFloor.setAll(shape, color)

    #segColors is a list of seven colors in A,...,G order of segments
    def setCustom(self, row, col, segColors):
        if self.simulatedFloor:
            self.simulatedFloor.setSegments(row, col, Colors.segmentsToRgb(segColors)) # Below this level segments are set by RGB color mask
        if self.realFloor:
            self.realFloor.setSegments(row, col, Colors.segmentsToRgb(segColors))

    def setAllCustom(self, segColors):
        if self.simulatedFloor:
            self.simulatedFloor.setSegmentsAll(Colors.segmentsToRgb(segColors))
        if self.realFloor:
            self.realFloor.setSegmentsAll(Colors.segmentsToRgb(segColors))

    def setColor(self, row, col, color):
        if self.realFloor:
            self.realFloor.setColor(row, col, color)
        if self.simulatedFloor:
            self.simulatedFloor.setColor(row, col, color)

    def setAllColor(self, color):
        if self.realFloor:
            self.realFloor.setAllColor(color)
        if self.simulatedFloor:
            self.simulatedFloor.setAllColor(color)

    def setShape(self, row, col, shape):
        if self.realFloor:
            self.realFloor.setShape(row, col, shape)
        if self.simulatedFloor:
            self.simulatedFloor.setShape(row, col, shape)

    def setAllShape(self, shape):
        if self.realFloor:
            self.realFloor.setAllShape(shape)
        if self.simulatedFloor:
            self.simulatedFloor.setAllShape(shape)

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

    def clearAll(self):
        if self.realFloor:
            self.realFloor.clearBoard()
        if self.simulatedFloor:
            self.simulatedFloor.clearBoard()

#    def setSegmentsCustom(self, row, col, colors):
#        pass

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
