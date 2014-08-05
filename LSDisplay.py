from LSRealFloor import LSRealFloor
import Shapes
from PyQt5.QtWidgets import (QApplication, QDialog, QHBoxLayout, QWidget)
from PyQt5.QtCore import (QEvent)
from LSEmulateFloor import LSEmulateFloor
import sys
import Move

#handles animations as well as allowing a common controller for displaying
#the state of the game on the real floor, on a simulated floor, on the console, or
#any combination thereof
class Display():
    def __init__(self, row, col, realFloor = False, simulator = False, console = False):
        self.row = row
        self.col = col
        if realFloor:
            print("realfloor true")
            self.realFloor = LSRealFloor(row, col)
        else:
            self.realFloor = None
        if simulator:
            print("simulator true")
            self.simulator = True
            self.app = QApplication(sys.argv)
            self.emulateFloor = LSEmulateFloor(row, col)
            self.dialog = LSDialog(None, self.emulateFloor)
        else:
            self.simulator = None
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
        if self.simulator:
            sensorsChanged = self.emulateFloor.pollSensors()
        if self.console and not self.realFloor and not self.simulator:
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
        if self.simulator:
            self.emulateFloor.setColor(row, col, color, True)
            self.emulateFloor.setSegments(row, col, shape)
        if self.realFloor:
            self.realFloor.set(row, col, shape, color)

    def setFrame(self, frame):
        print("set frame called")
        for row in range(self.row):
            for col in range(self.col):
                if frame.hasChangesFor(row, col):
                    self.set(row, col, frame.getShape(row, col), frame.getColor(row, col))
                    print("...")

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

#handles timer events from the emulated floor dialog
class LSDialog(QDialog):
    def __init__(self, parent, floor):
        wid = QWidget()
        super(LSDialog, self).__init__()
        self.mainLayout = QHBoxLayout()
        self.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)
        self.setWindowTitle("Lightsweeper")
        self.setVisible(True)
        self.mainLayout.addWidget(floor)

    def timerEvent(self, *args, **kwargs):
        #print("got timer event", *args, **kwargs)
        self.enterFrame()
