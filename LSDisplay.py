from LSRealFloor import LSRealFloor
from LSEmulateFloor import EmulateFloor
import Shapes
import Colors
import random
import sys
from Move import Move
import pygame
import time

#handles animations as well as allowing a common controller for displaying
#the state of the game on the real floor, on a simulated floor, on the console, or
#any combination thereof
class Display():
    def __init__(self, row, cols, realFloor = False, simulatedFloor = False, console = False):
        self.row = row
        self.cols = cols
        if realFloor:
            print("Display instantiating real floor")
            self.realFloor = LSRealFloor(row, cols)
        else:
            self.realFloor = None
        self.floor = []
        for r in range(row):
            self.floor.append([])
            for c in range(cols):
                self.floor[r].append('-')
        self.console = console
        if simulatedFloor:
            print("Display instantiating simulated floor")
            self.simulatedFloor = EmulateFloor(row, cols)



    #this is to handle display functions only
    def heartbeat(self):
        #print("Display heartbeat")
        if self.simulatedFloor:
            self.simulatedFloor.heartbeat()
        if self.realFloor:
            self.realFloor.heartbeat()
        #check pygame for position and click ness of mouse
        pass

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
        if self.simulatedFloor:
            self.simulatedFloor.setColor(row, col, color)
            self.simulatedFloor.setShape(row, col, shape)
        wait(0.005)

    def setColor(self, row, col, color):
        if self.realFloor:
            self.realFloor.setColor(row, col, color)
        if self.simulatedFloor:
            self.simulatedFloor.setColor(row, col, color)
        wait(0.005)

    def setShape(self, row, col, shape):
        if self.realFloor:
            self.realFloor.setShape(row, col, shape)
        if self.simulatedFloor:
            self.simulatedFloor.setShape(row, col, shape)
        wait(0.005)

    def setFrame(self, frame):
        for row in range(self.row):
            for col in range(self.cols):
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
