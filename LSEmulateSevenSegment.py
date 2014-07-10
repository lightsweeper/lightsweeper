from PyQt5.QtWidgets import (QGridLayout)

# Lightsweeper additions
from PyQt5.QtWidgets import (QWidget, QFrame)
from LSApi import LSApi

# individually addressable segment class
# not derived from the API, this only does segment display
class LSEmulateSevenSegment(QFrame):

    # class vbles - do not change these in objects :)
    backgroundColor = "black"

    def __init__(self, row=0, col=0):
        super(QFrame, self).__init__()
        # prefer to remove spacing, but at least make it background
        str = "QFrame {{background-color: {0} }}".format(self.backgroundColor)
        self.setStyleSheet(str)
        self.row = row
        self.col = col
        # just a blank thing to paint on
        #self.segments = QWidget()
        #self.segments.setMinimumSize(30, 40)
        # define seven individual segments as color strings
        self.colorA = "white"
        self.colorB = "white"
        self.colorC = "white"
        self.colorD = "white"
        self.colorE = "white"
        self.colorF = "white"
        self.colorG = "white"
        self.segColors = [self.colorG, self.colorF, self.colorE, self.colorD, self.colorC, self.colorB, self.colorA]
        self.queueColor = "white "
        self.queueDigit = 8;
        self.setContentsMargins(0,0,0,0)
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)
        rows = 5 #7
        cols = 5 # 3 #5
        for row in range(rows):
            for col in range(cols):
                segment = QWidget()
                segment.setContentsMargins(0,0,0,0)
                newColor = LSEmulateSevenSegment.backgroundColor
                #if (row == 0) or (row == 6):
                #    segment.setMaximumSize(300,2)
                #elif (col == 0) or (col == 4):
                #    segment.setMaximumSize(2,300)
                if (row == 0) and (col == 2):
                    segment.setMinimumSize(20,5)
                    self.segA = segment
                    newColor = "blue"
                elif (row == 2) and (col == 2):
                    segment.setMinimumSize(20,5)
                    self.segG = segment
                    newColor = "blue"
                elif (row == 4) and (col == 2):
                    segment.setMinimumSize(20,5)
                    self.segD = segment
                    newColor = "blue"
                elif (row == 1) and ((col == 1) or col == 3):
                    segment.setMinimumSize(5,20)
                    if col == 1:
                        self.segF = segment
                    else:
                        self.segB = segment
                    newColor = "blue"
                elif (row == 3) and ((col == 1) or col == 3):
                    segment.setMinimumSize(5,20)
                    if col == 1:
                        self.segE = segment
                    else:
                        self.segC = segment
                    newColor = "blue"
                else:
                    segment.setMinimumSize(5,5)
                str = "QWidget {{background-color: {0} }}".format(newColor)
                segment.setStyleSheet(str)
                layout.addWidget(segment, row, col)

        layout.setRowStretch(0, 1.0)
        layout.setRowStretch(1, 4.0) # stretch vertical segments lengthwise
        layout.setRowStretch(2, 1.0)
        layout.setRowStretch(3, 4.0)
        layout.setRowStretch(4, 1.0)
        layout.setColumnStretch(0, 1.0)
        layout.setColumnStretch(1, 1.0)
        layout.setColumnStretch(2, 4.0) # stretch horizontal segments lengthwise
        layout.setColumnStretch(3, 1.0)
        layout.setColumnStretch(4, 1.0)

        # all segments are made
        self.segments = [self.segA, self.segB, self.segC, self.segD, self.segE, self.segF, self.segG]
        self.setLayout(layout)
        self.update()

    def flushQueue(self):
        self.display()

    def setColor (self, newColor, setItNow = True):
        self.queueColor = newColor;
        if setItNow:
            self.display()

    # set immediately or queue these segments in addressed tiles
    # segments is a seven-tuple interpreted as True or False
    def setSegments(self, row, column, segments, setItNow = True):
        self.segments.setSegments(segments, setItNow)
	# TODO - split out part of display() to here
	# and make each segment color independent

    def setDigit (self, newDigit, setItNow = True):
        self.queueDigit = newDigit;
        if setItNow:
            self.display()

    def display (self):
        segs = LSApi.segMasks[self.queueDigit]  # map digit to segment mask
        for idx in range(len(segs)):
            litSeg = segs[idx]
            if litSeg:
                newColor = self.queueColor
            else:
                newColor = LSEmulateSevenSegment.backgroundColor
            self.segColors[idx] = newColor
            str = "QWidget {{background-color: {0} }}".format(newColor)
            self.segments[idx].setStyleSheet(str)

    def getCol (self):
        return self.col

    def getRow (self):
        return self.row