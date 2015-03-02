#from LSRealFloor import LSRealFloor
import Shapes
import sys
import string
import Move

ClearScreen = "\x1b[37;40m" #"\x1b[2J"
SetColorFg = "\x1b[3%s;40m"
SetColorBg = "\x1b[4%s;30m"
"""
  0 
1   5
  6
2   4
  3
"""

def hbar(s):
    if s != "0":
        return "--"
    else:
        return "  "

def vbar(s):
    if s != "0":
        return "|"
    else:
        return " "

def getLinesForShape(shape):
    L = [ "", "", "", "", "" ]
    
    S = bin(shape)[2:]
    L[0] += " %s " % (hbar(S[0]))
    L[1] += "%s  %s" % (vbar(S[1]), vbar(S[5]))
    L[2] += " %s " % (hbar(S[6]))
    L[3] += "%s  %s" % (vbar(S[2]), vbar(S[4]))
    L[4] += " %s " % (hbar(S[3]))

    return L

#handles animations as well as allowing a common controller for displaying
#the state of the game on the real floor, on a simulated floor, on the console, or
#any combination thereof
class Display():
    def __init__(self, rows, cols, realFloor = False, simulator = False, console = False):
        self.row = rows
        self.col = cols
        self.floor = [ [[]] * cols ] * rows
        self.keymap = string.ascii_lowercase + string.ascii_uppercase
        self.depressed = ""

    #this is to handle display functions only
    def heartbeat(self):
        pass

    def beginQtLoop(self, enterFrame, frameGap):
        print("setting up Qt timer event based loop")

    def printFloor(self):
        k=0
        print(ClearScreen)
        for r in range(self.row):
            lines = [ "", "", "", "", "" ]
            for c in range(self.col):
                shape, color = self.floor[r][c]
                L = getLinesForShape(shape)
                key = self.keymap[k]
                k += 1
                if key in self.depressed:
                    colorcode = SetColorBg % color
                else:
                    colorcode = SetColorFg % color
                L[0] = key + L[0][1:]
                for i in range(len(L)):
                    lines[i] += colorcode + " " + L[i]
            print("\n".join(lines))

    def pollSensors(self):
        sensorsChanged = []
        self.printFloor()
        for x in input(""):
            if x not in self.keymap:
                print ("invalid move '%s', ignoring" % x)
                continue

            if x in self.depressed:
                i = self.depressed.index(x)
                self.depressed = self.depressed[:i] + self.depressed[i+1:]
                print(self.depressed)
            else:
                self.depressed += x

            n = self.keymap.index(x)
            r = int(n / self.row)
            c = int(n % self.row)
            move = Move.Move(r,c,0)
            sensorsChanged.append(move) #we want to ensure we never return a NoneType

        return sensorsChanged

    def set(self, row, col, shape, color):
        self.floor[row][col] = [ shape, color ]

    def setColor(self, row, col, color):
        self.floor[row][col][1] = color

    def setShape(self, row, col, shape):
        self.floor[row][col][0] = shape

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

