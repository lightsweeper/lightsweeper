from LSRealFloor import LSRealFloor
import Shapes
import sys
from Move import Move

#handles animations as well as allowing a common controller for displaying
#the state of the game on the real floor, on a simulated floor, on the console, or
#any combination thereof
class Display():
    def __init__(self, row, col, realFloor = False, console = False):
        self.row = row
        self.col = col
        if realFloor:
            print("realfloor true")
            self.realFloor = LSRealFloor(row, col)
        else:
            self.realFloor = None
        self.floor = []
        for r in range(row):
            self.floor.append([])
            for c in range(col):
                self.floor[r].append('-')
        self.console = console

    #this is to handle display functions only
    def heartbeat(self):
        pass

    def beginQtLoop(self, enterFrame, frameGap):
        print("setting up Qt timer event based loop")
        #setup timer
        self.dialog.startTimer(frameGap)
        #setup callback for timer
        self.dialog.enterFrame = enterFrame
        self.dialog.exec()

    def printFloor(self):
        print("printing floor")
        s = ''
        for r in range(self.row):
            for c in range(self.col):
                s += ' ' + str(self.floor[r][c])
            print(s)
            s = ''

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
        #print("set:", row, col, shape, color)
        #if shape is not 126:
        #    print("set", row, col, bin(shape))
        if self.console:
            self.floor[row][col] = Shapes.hexToDigit(shape)
        if self.realFloor:
            self.realFloor.set(row, col, shape, color)

    def setColor(self, row, col, color):
        if self.realFloor:
            self.realFloor.setColor(row, col, color)

    def setShape(self, row, col, shape):
        if self.realFloor:
            self.realFloor.setShape(row, col, shape)

    def setFrame(self, frame):
        for row in range(self.row):
            for col in range(self.col):
                #if frame.hasChangesFor(row, col):
                if frame.hasColorChangesFor(row, col):
                    self.setColor(row, col, frame.getColor(row, col))
                if frame.hasShapeChangesFor(row, col):
                    self.setShape(row, col, frame.getShape(row, col))

    def setSegmentsCustom(self, row, col, colors):
        pass

    def add(self, row, col, shape, color):
        pass

    def addCustom(self, row, col, colors):
        pass

    def addAnimation(self, row, col, animation, loops):
        pass

    def clear(self):
        pass