from collections import defaultdict
import time


import Shapes
import Colors
import lsdisplay

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
        if self.rows > display.rows or self.cols > display.cols:
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
        if width is None:
            self.width = len(charString)
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
                    colorMask = Colors.intToRGB(self.color)
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


    ourAnimation.play(d, frameRate=0)



if __name__ == '__main__':
    main()
