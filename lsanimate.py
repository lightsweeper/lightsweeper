from collections import defaultdict
import itertools


import Shapes
import Colors
import lsdisplay

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

def renderFrame(floor, frame):
# TODO: Incomplete, should optimize tile calls

    cols = frame.pop(0)
    row = 0
    col = 0
    for _ in itertools.repeat(None, int(len(frame)/3)):
        if col is cols:
            row += 1
            col = 0
        rMask = frame.pop(0)
        gMask = frame.pop(0)
        bMask = frame.pop(0)
        if rMask is not 128:
            floor.tiles[row][col].setSegments((rMask,gMask,bMask))
          #  print("{:d},{:d} -> ({:d},{:d},{:d})".format(row,col,rMask,gMask,bMask)) # Debugging
        col += 1


class LSAnimation:

    def __init__(self):
        self._frames = list()

    def addFrame(self, frame):
        self.insertFrame(len(self._frames), frame)
        return True

    def insertFrame(self, index, frame):
    # Inserts before given frame
        if validateFrame(frame) is False:
            print("Error frame is invalid")
            raise Exception
        index -= 1
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

    def showFrames(self):
        Frame = self.nextFrame()
        i = 0
        while True:
            i += 1
            try:
                print("Frame {:d}: ".format(i) + str(next(Frame)))
            except:
                print("Out of frames")
                break

    def nextFrame(self):
        if len(self._frames) is 0:
            print("No frames!")
        else:
            for frame in self._frames:
                yield(frame)

    def _checkIndex(self, index):
        if index not in range(-1,len(self._frames)+1):
            print("Error frame index out of range")
            raise Exception
        return True


class LSFrameGen:

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.frame = defaultdict(lambda: defaultdict(int))

    # Allows you to edit an existing frame structure, if no colormask is set
    # then the tile will keep its current colormask
    def edit(self,row,col,colormask):
        if row > self.rows or col > self.cols:
            print("Edit error, index out of range")
            raise Exception
        self.frame[row][col] = [colormask]

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
                    print("Warning: ({:d},{:d}) has no update".format(row,col))
                    frameOut.append(128)
                    frameOut.append(128)
                    frameOut.append(128)
        return(frameOut)  # frameOut is a list consisting of the number of columns in the frame
                          # followed by a repeating pattern of 3 integers, each representing a
                          # subsequent tile's red, green, and blue colormasks



def main():
    import time
    print("TODO: testing lsanimate")

    colormask = (Shapes.ZERO, 0,0)
    diffmask = (Shapes.ONE, Shapes.TWO, Shapes.THREE)
    redZero = (Shapes.ZERO, Shapes.OFF, Shapes.OFF)
    greenZero = (0, Shapes.ZERO, 0)
    blueZero = (0, 0, 126)

    ourAnimation = LSAnimation()

    frame = LSFrameGen(3,8)
    
    for _ in range(0,100):
        for i in range(0,8):
            frame.edit(0,i,redZero)
            frame.edit(1,i,greenZero)
            frame.edit(2,i,blueZero)
        ourAnimation.addFrame(frame.get())
        for i in range(0,8):
            frame.edit(1,i,redZero)
            frame.edit(2,i,greenZero)
            frame.edit(0,i,blueZero)
        ourAnimation.addFrame(frame.get())
        for i in range(0,8):
            frame.edit(2,i,redZero)
            frame.edit(0,i,greenZero)
            frame.edit(1,i,blueZero)
        ourAnimation.addFrame(frame.get())




   # ourAnimation.deleteFrame(1)

  #  ourAnimation.showFrames()

    useRealFloor = True
    try:
        realTiles = LSOpen()
    except Exception as e:
        useRealFloor = False

    print("Importing LSDisplay")
    import lsdisplay

    d = lsdisplay.LSDisplay(realFloor = True, simulatedFloor = False, initScreen=False)

    
    stime = time.time()
    Frame = ourAnimation.nextFrame()
    f = 0
    for frame in Frame:
        renderFrame(d.realFloor, frame)
        #d.pollSensors()
        #time.sleep(.1)
        f += 1
        if (time.time() - stime > 1):
            print(f)
            stime = time.time()
            f = 0
        

    input()

if __name__ == '__main__':
    main()
