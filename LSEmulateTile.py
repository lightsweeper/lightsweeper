from PyQt5.QtWidgets import (QPushButton, QVBoxLayout)

# Lightsweeper additions
from PyQt5.QtWidgets import (QFrame)
from LSApi import LSApi
from LSEmulateSevenSegment import LSEmulateSevenSegment

# this class holds a seven segment display and a button to mimic the pressure sensor
# it does no segment processing, it just passes thru to the seven segment display
class LSEmulateTile(QFrame, LSApi):

    def __init__(self, row=0, col=0):
        super(QFrame, self).__init__()
        self.row = row
        self.col = col
        self.segments = LSEmulateSevenSegment()
        self.setContentsMargins(0,0,0,0) # maybe should use layout
        self.button = QPushButton("%d %d" % (row+1, col+1))
        self.button.setCheckable(True)
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.segments)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def flushQueue(self):
        self.segments.flushQueue()

    def setColor (self, newColor, setItNow = True):
        self.segments.setColor(newColor, setItNow)

    # set immediately or queue these segments in addressed tiles
    # segments is a seven-tuple interpreted as True or False
    def setSegments(self, row, column, segments, setItNow = True):
        self.segments.setSegments(segments, setItNow)

    def setDigit (self, newDigit, setItNow = True):
        self.segments.setDigit(newDigit, setItNow)

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
