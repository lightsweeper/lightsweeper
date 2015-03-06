from collections import defaultdict
import itertools

import Shapes
import Colors
import lsdisplay

def validateFrame(frame):
    frameLen = len(frame) - 1
    if frameLen % 4 is not 0:
        return False
    cells = frameLen/4
    if (cells/frame[0]).is_integer() is False:
        return False
    if all(i < 128 for i in frame[1:]) is False:
        return False
    return True

def renderFrame(floor, frame):
# TODO: Incomplete, should optimize tile calls

    cols = frame.pop(0)
    row = 0
    col = 0
    for _ in itertools.repeat(None, int(len(frame)/4)):
        if col is cols:
            row += 1
            col = 0
        shape = frame.pop(0)
        rMask = frame.pop(0)
        gMask = frame.pop(0)
        bMask = frame.pop(0)
        floor.tiles[row][col].setSegments(rMask,gMask,bMask)
        print("{:d},{:d} -> {:d} ({:d},{:d},{:d})".format(row,col,shape,rMask,gMask,bMask)) # Debugging
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
    def edit(self,row,col,shape=None,colormask=None):
        if colormask is None:
            try:
                colormask = self.frame[row][col][1]
            except TypeError:
                print("Frame warning: No colormask set for cell at ({:d},{:d})".format(row,col))
                color = Colors.BLACK
        if shape is None:
            try:
                shape = self.frame[row][col][0]
            except TypeError:
                print("Frame warning: No shape set for cell at ({:d},{:d})".format(row,col))
                shape = Shapes.OFF
        self.frame[row][col] = [shape, colormask]

    def print(self):
        for row in self.frame:
            print([self.frame[row][col] for col in self.frame[row]])

    def get(self):
        frameOut = list()
        frameOut.append(self.cols)
        for row in self.frame:
            for col in self.frame:
                cell = self.frame[row][col]
         #       frameOut.append(row)
         #       frameOut.append(col)
                frameOut.append(cell[0])
                frameOut.append(cell[1][0])
                frameOut.append(cell[1][1])
                frameOut.append(cell[1][2])
        return(frameOut)  # frameOut is a list consisting of the number of columns in the frame
                          # followed by a repeating pattern of 4 integers, each representing a
                          # subsequent tile's shape, and red, green, and blue colormasks



def main():
    print("TODO: testing lsanimate")

    colormask = (Shapes.ZERO, Shapes.ZERO, Shapes.ZERO)
    diffmask = (Shapes.ONE, Shapes.TWO, Shapes.THREE)

    frame = LSFrameGen(2,2)
    frame.edit(1,1,Shapes.ZERO, colormask)
    frame.edit(1,1,Shapes.SEVEN)
    frame.edit(1,2,Shapes.ONE, colormask)
    frame.edit(2,2,Shapes.ZERO, diffmask)
    frame.edit(2,1,Shapes.ONE, diffmask)

    thisFrame = frame.get()

    ourAnimation = LSAnimation()



    ourAnimation.addFrame(thisFrame)
    ourAnimation.addFrame(thisFrame)

    frame.edit(2,2,Shapes.FOUR)
    thisFrame = frame.get()
    ourAnimation.insertFrame(1,thisFrame)
    ourAnimation.insertFrame(1,thisFrame)
    ourAnimation.insertFrame(1,thisFrame)
    ourAnimation.insertFrame(1,thisFrame)


    ourAnimation.deleteFrame(1)

    ourAnimation.showFrames()

    useRealFloor = True
    try:
        realTiles = LSOpen()
    except Exception as e:
        useRealFloor = False

    print("Importing LSDisplay")
    import lsdisplay

    d = lsdisplay.LSDisplay(realFloor = useRealFloor, simulatedFloor = True, initScreen=False)

    renderFrame(d.simulatedFloor, thisFrame)
    input()

if __name__ == '__main__':
    main()
