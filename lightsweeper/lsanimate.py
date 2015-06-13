""" Tools for creating and manipulating animations

Animations are objects created from classes derived from LSAnimation. Each
LSAnimation object maintains a list of frames which can be manipulated using
methods specific to the subclass. Each frame is a list of integers representing
segments that need to be illuminated. The first item in the list represents the
width of the frame in columns. All of the frames that make up a given animation
must have the same dimensions.

The rest of a the numbers in the frame object are a repeating pattern of Red,
Green, and Blue color masks, every three belonging to tiles succesively scanned
from the left to the right and the top to the bottom. A color mask is an integer
defining a certain shape on the 7 segment display. The shapes referenced in Red,
Green, and Blue will be composited over eachother on the display. Look at the
documentation in the Shapes module for more information on the scheme used to
encode different shapes.

Frames can be constructed and manipulated using the LSFrameGen class. Objects
created by LSFrameGen maintain an internal representation of a frame and output
the compacted list-type frames required by LSAnimation whenever the get() method
is called. A simple technique for programatically generating animations is thus
to maintain one or more LSFrameGen objects that you apply transformations to
while iteratively adding the output of get() to your LSAnimation object.

Using the mergeFrames tool you can merge the contents of a frame, at an
arbitrary offset, into another frame of equal or greater size. By unpacking and
merging the frames from two animations you can create a new combined animation.

"""

from collections import defaultdict
import time
import itertools


from lightsweeper import Shapes
from lightsweeper import Colors
from lightsweeper import lsdisplay

# TODO: Custom error handlers

def validateFrame(frame):
   # print(repr(frame)) # Debugging
    frameLen = len(frame) - 1
    if frameLen % 3 is not 0:
        return False
    cells = frameLen/3
    if (cells/frame[0]).is_integer() is False:
        return False
    if all(i <= 128 for i in frame[1:]) is False:
        return False
    return True
    
def mergeFrames(baseFrame, subFrame, offset=(0,0)):
    # TODO: Alpha channel
    rows = bRows = frameRows(baseFrame)
    cols = bCols = baseFrame.pop(0)
    sRows = frameRows(subFrame)
    sCols = subFrame.pop(0)
    if sRows+offset[0] > rows or sCols+offset[1] > cols:
        raise Exception("Cannot merge frames, subFrame plus offset must be smaller than baseFrame")
    out = list()
    hiddenLayer = list()
    out.append(cols)
    out.extend([baseFrame.pop(0) for _ in range(offset[0]*bCols*3)])
    while len(subFrame) > 0:
        out.extend([baseFrame.pop(0) for _ in range(offset[1]*3)])
        hiddenLayer.extend([baseFrame.pop(0) for _ in range(sCols*3)])
        out.extend([subFrame.pop(0) for _ in range(sCols*3)])
        out.extend([baseFrame.pop(0) for _ in range((bCols-sCols-offset[1])*3)])
    out.extend(baseFrame)
    return(out)

    

def frameRows (frame):
    return(len(frame[1:])/frame[0]/3)

def frameCols (frame):
    return(frame[0])
    
class LSAnimation:

    def __init__(self):
        self._frames = list()

    def addFrame(self, frame):
        if len(self._frames) is 0:
            self.rows = int(len(frame[1:])/frame[0]/3)
            self.cols = frame[0]
        self.insertFrame(len(self._frames), frame)
        return True

    def insertFrame(self, index, frame):
    # Inserts before given frame
        if validateFrame(frame) is False:
            print("Error frame is invalid")
            raise Exception
        if self._checkIndex(index) is True:
            self._frames.insert(index,frame)
        return True

    def deleteFrame(self, index):
        index -= 1
        if self._checkIndex(index) is True:
            frames = self._frames[0:index]
            frames.extend(self._frames[index+1:])
            self._frames = frames
        return True

    def dropFrames(self):
        # Discard all stored frames
        self._frames = list()

    def showFrames(self):
        Frame = self.nextFrame()
        i = 0
        while True:
            i += 1
            try:
                print("Frame {:d}: {:s}".format(i, str(next(Frame))))
            except StopIteration:
                print("Out of frames")
                break

    def nextFrame(self):
        if len(self._frames) is 0:
            print("No frames!")
        else:
            for frame in self._frames:
                yield(frame)

    def play(self, display, frameRate = 30):
        if frameRows(self._frames[0]) > display.rows or frameCols(self._frames[0]) > display.cols:
            raise Exception("Animation is too large for this display!")  # TODO: support clipping
        if frameRate < 0:
            raise ValueError("Please specify a non-negative frame rate")
        print("Starting animation ({:d} frames at {:d} fps)".format(len(self._frames), frameRate))
        Frame = self.nextFrame()
        i = 0
        for frame in Frame:
            i+=1
            if frameRate is 0:
                input("Press any key to advance the animation...\n")
                print("Frame {:d}: {:s}".format(i, str(frame)))
            stime = time.time()
            display.floor.renderFrame(frame)
            display.heartbeat()
            renderTime = time.time() - stime

            if frameRate is not 0:
                fps = 1.0/renderTime
                if fps < frameRate:
                    print("[Animation]{0:.4f} FPS".format(1.0/renderTime), end="\r")
                else:
                    time.sleep((1.0/frameRate) - renderTime)
        if frameRate is 0:
            print("Animation ended.")
        print(" " * 22, end = "\r")

        

    def _checkIndex(self, index):
        if index not in range(-1,len(self._frames)+1):
            print("Error frame index out of range")
            raise Exception
        return True

class ScrollingText(LSAnimation):

    height = 1
    width = 1
    color = Colors.WHITE
    direction = "left"
    iterations = 1

    def __init__(self, text, color=Colors.WHITE, height=1, width=None):
        super().__init__()
        self.charString = Shapes.stringToShapes(text)
        self.direction="left"
        self.height = height
        self.color = color
        if width is None:
            self.width = len(self.charString)
        else:
            self.width = width

    def __setattr__ (self, name, value):
        super().__setattr__(name, value)
        if name in ["height", "width", "color", "direction", "iterations"]:
            self._buildAnimation()

    def _buildAnimation (self):
        self.dropFrames()
        self.frame = LSFrameGen(self.height, self.width)
        cs = self.charString[:]
        if "right" in self.direction.lower():
            cs = reversed(cs)
        if self.height is 1:
            endCap = lambda x: self.width-1 if "left" in x.lower() else 0
            for i in range(0,self.iterations):
                for char in cs:
                    try:
                        color = next(self.color)
                    except TypeError:
                        color = self.color
                    colorMask = Colors.intToRGB(color)
                    charR = charG = charB = 0
                    (charR, charG, charB) = [char if i is not 0 else 0 for i in colorMask]
                    self.frame.edit(0, endCap(self.direction), (charR, charG, charB))
                    self.addFrame(self.frame.get())
                    self._pickShift()
                if True:
                    for i in range(0,self.width):
                        self.frame.edit(0, endCap(self.direction), (0, 0, 0))
                        self.addFrame(self.frame.get())
                        self._pickShift()
        else:
            raise NotImplementedError("height cannot be more than 1")


    def _pickShift(self):
        lowerD = self.direction.lower()
        if "left" in lowerD:
            self.frame.shiftLeft()
        elif "right" in lowerD:
            self.frame.shiftRight()



class LSFrameGen:

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.frame = defaultdict(lambda: defaultdict(int))

    # Allows you to edit an existing frame structure, if no colormask is set
    # then the tile will keep its current colormask
    def edit(self, row, col, colormask):
        if row > self.rows or col > self.cols:
            print("Edit error, index out of range")
            raise Exception
        self.frame[row][col] = [colormask]

    def fill(self, colormask):
        for row in range(0, self.rows):
            for col in range(0, self.cols):
                self.frame[row][col] = [colormask]

    def shiftLeft (self):
        for col in range(0, self.cols-1):
            for row in range(0, self.rows):
                self.frame[row][col] = self.frame[row][col+1]
        for row in range(0, self.rows):
            self.frame[row][self.cols-1] = [(0,0,0)]

    def shiftRight (self):
        for col in reversed(range(0, self.cols)):
            for row in range(0, self.rows):
                self.frame[row][col] = self.frame[row][col-1]
        for row in range(0, self.rows):
            self.frame[row][0] = [(0,0,0)]

    def shiftUp (self):
        for row in range(0, self.rows-1):
            for col in range(0, self.cols):
                self.frame[row][col] = self.frame[row+1][col]
        for col in range(0, self.cols):
            self.frame[self.rows-1][col] = [(0,0,0)]

    def shiftDown (self):
        for row in reversed(range(0, self.rows)):
            for col in range(0, self.cols):
                self.frame[row][col] = self.frame[row-1][col]
        for col in range(0, self.cols):
            self.frame[0][col] = [(0,0,0)]

#TODO: (shiftDiag?)



    def print(self):
        for row in self.frame:
            print([self.frame[row][col] for col in self.frame[row]])

    def get(self):
        frameOut = list()
        frameOut.append(self.cols)
        for row in range(0, self.rows):
            for col in range(0, self.cols):
                try:
                    cell = self.frame[row][col][0]
                    frameOut.append(cell[0])
                    frameOut.append(cell[1])
                    frameOut.append(cell[2])
                except:
                #    print("Warning: ({:d},{:d}) has no update".format(row,col)) # Debugging
                    frameOut.append(128)
                    frameOut.append(128)
                    frameOut.append(128)
        return(frameOut)  # frameOut is a list consisting of the number of columns in the frame
                          # followed by a repeating pattern of 3 integers, each representing a
                          # subsequent tile's red, green, and blue colormasks

  #  def put(self, frame):
  #      if not validateFrame(frame):
  #          raise Exception("Cannot put frame. Frame is invalid")
  #      cols = frame.pop()
  #      row = col = 0
  #      for _ in itertools.repeat(None, int(len(frame)/3)):
  #          if col is cols:
  #              row += 1
  #              col = 0
  #          rMask, gMask, bMask = frame.pop(0), frame.pop(0), frame.pop(0)
  #          if rMask is not 128:
  #              self.frame[row][col] = (rMask, gMask, bMask)
  #          col += 1


def example():

    # Import the LightSweeper API
    from lightsweeper.lsapi import *

    # Also import the animation library
    from lightsweeper import lsanimate

    # We'll start by creating a frame the size of our desired animation
    # Let's make this one 3 rows by 3 columns
    frame = lsanimate.LSFrameGen(3, 3)

    # We'll also need a fresh animation object to put our generated frames in
    ourAnimation = lsanimate.LSAnimation()

    # I want the background of this animation to be all pink so I need to
    # build a colormask that looks like a magenta Eight. Magenta is red+blue
    # so:
    pinkEight = (redMask, greenMask, blueMask) = (Shapes.EIGHT, 0, Shapes.EIGHT)

    # Then fill the frame with it
    frame.fill(pinkEight)

    # Now for my animation I'd like to make a vertical green stripe that
    # moves down the the height of the frame. I'll define three new masks:
    bottomLine = (Shapes.A, Shapes.UNDERSCORE, Shapes.A)
    midLine = (Shapes.ZERO, Shapes.DASH, Shapes.ZERO)
    topLine = (Shapes.U+Shapes.DASH, Shapes.SEG_A, Shapes.U+Shapes.DASH)

    # Now we'll programatically animate the scanning line:
    for _ in range(0, 10):
        for thisRow in range(frame.rows):
            for i in range(4):
                for thisCol in range(frame.cols):
                    if i is 0:
                        frame.edit(thisRow, thisCol, topLine)
                    elif i is 1:
                        frame.edit(thisRow, thisCol, midLine)
                    elif i is 2:
                        frame.edit(thisRow, thisCol, bottomLine)
                    else:
                        frame.edit(thisRow, thisCol, pinkEight)
                ourAnimation.addFrame(frame.get())
                
    d = LSDisplay()

    ourAnimation.play(d, frameRate=10)

def main():
    print("Importing LSDisplay")
    import lsdisplay

    d = lsdisplay.LSDisplay(initScreen=False)

    colormask = (Shapes.ZERO, 0,0)
    diffmask = (Shapes.ONE, Shapes.TWO, Shapes.THREE)
    redZero = (Shapes.ZERO, Shapes.OFF, Shapes.OFF)
    greenZero = (0, Shapes.ZERO, 0)
    blueZero = (0, 0, 126)

    ourAnimation = LSAnimation()

    frame = LSFrameGen(3,d.cols)
    
    for _ in range(0,100):
        for i in range(d.cols):
            frame.edit(0,i,redZero)
            frame.edit(1,i,greenZero)
            frame.edit(2,i,blueZero)
        ourAnimation.addFrame(frame.get())
        for i in range(0,d.cols):
            frame.edit(1,i,redZero)
            frame.edit(2,i,greenZero)
            frame.edit(0,i,blueZero)
        ourAnimation.addFrame(frame.get())
        for i in range(0,d.cols):
            frame.edit(2,i,redZero)
            frame.edit(0,i,greenZero)
            frame.edit(1,i,blueZero)
        ourAnimation.addFrame(frame.get())



   # ourAnimation.deleteFrame(1)

  #  ourAnimation.showFrames()


    ourAnimation.play(d, frameRate=15)



if __name__ == '__main__':
    main()
