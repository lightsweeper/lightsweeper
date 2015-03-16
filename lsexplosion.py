from collections import defaultdict
import time


import Shapes
import Colors
import lsdisplay
import lsanimate

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



# TODO - decide if this should subclass LSFrameGen
class LSExplosion:
#class OBS_LSFrameGen:

    blank = (0, 0, 0)
    #colormask = (Shapes.ZERO, 0,0)
    #diffmask = (Shapes.ONE, Shapes.TWO, Shapes.THREE)
    redZero = (Shapes.ZERO, Shapes.OFF, Shapes.OFF)
    greenZero = (0, Shapes.ZERO, 0)
    blueZero = (0, 0, 126)
    redX = (Shapes.H, 0, 0)
    bomb0 = (Shapes.DASH, 0,0)
    bomb1 = (Shapes.H, Shapes.DASH,0)
    bomb2 = (Shapes.EIGHT, Shapes.H, Shapes.DASH)
    bomb3 = (Shapes.EIGHT, Shapes.EIGHT, Shapes.H)
    bomb4 = (Shapes.EIGHT, Shapes.EIGHT, Shapes.EIGHT)
    bomb5 = (Shapes.EIGHT, Shapes.OFF, Shapes.OFF)
    bomb6 = (Shapes.OFF, Shapes.OFF, Shapes.OFF)
    bomb7 = (Shapes.EIGHT, Shapes.OFF, Shapes.OFF)
    bomb8 = (Shapes.OFF, Shapes.OFF, Shapes.OFF)
    bombs = [bomb0, bomb1, bomb2, bomb3, bomb4, bomb5, bomb6, bomb7, bomb8]

    bombThrob0 = (Shapes.EIGHT, Shapes.OFF, Shapes.OFF)
    bombThrob0 = (Shapes.EIGHT, Shapes.OFF, Shapes.OFF)
    bombThrob1 = (Shapes.H, Shapes.OFF, Shapes.OFF)
    bombThrob2 = (Shapes.DASH, Shapes.OFF, Shapes.OFF)
    bombThrobs = [bombThrob0, bombThrob1, bombThrob2]

    bombThrob0 = (Shapes.ZERO, Shapes.OFF, Shapes.OFF)
    bombThrob1 = (Shapes.H, Shapes.OFF, Shapes.OFF)
    bombThrobs = [bombThrob0, bombThrob1]

    def __init__(self, rows, cols, mine, mines):
        self.rows = rows
        self.cols = cols
        self.frameNum = 0
        self.frame = defaultdict(lambda: defaultdict(int))
        self.firstMine = mine
        self.allMines = mines

    # Allows you to edit an existing frame structure, if no colormask is set
    # then the tile will keep its current colormask
    def edit(self,row,col,colormask):
        if row > self.rows or col > self.cols:
            print("Edit error, index out of range")
            raise Exception
        self.frame[row][col] = [colormask]

    def fill(self,colormask):
        for row in range(0, self.rows):
            for col in range(0, self.cols):
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

    def flamefront(self):
            for col in range(0,self.cols):
                for row in range(0,self.rows):
                    tile = (row,col)
                    # mine cells blow up then throb forever
                    #if tile == self.firstMine:
                    if tile in self.allMines:
                        if self.frameNum < len(self.bombs):
                            #maskIdx = self.frameNum % len(self.bombs)
                            mask = self.bombs[self.frameNum]
                        else:
                            maskIdx = self.frameNum % len(self.bombThrobs)
                            mask = self.bombThrobs[maskIdx]
                        self.edit(row,col,mask)
                    elif self.frameNum % 3 is not 0 and row == col:
                        #mask = self.redZero
                        mask = self.blank
                        # TODO - would be better to not disturb until wavefront gets here
                        self.edit(row,col,mask)
                    else:
                        #mask = self.greenZero
                        mask = self.blank
                        self.edit(row,col,mask)
            self.frameNum = self.frameNum + 1
            print("Computed frame " + repr(self.frameNum))


def main():
    print("TODO: testing lsexplosion")

    useRealFloor = True
    try:
        realTiles = LSOpen()
    except Exception as e:
        useRealFloor = False

    d = lsdisplay.LSDisplay(realFloor = False, simulatedFloor = True, initScreen=False)
    rows = d.rows
    cols = d.cols

    ourAnimation = lsanimate.LSAnimation()

    #frame = lsanimate.LSFrameGen(rows,cols)
    mine = (0,1)   # this mine is the first to blow
    mines = [mine, (1,2), (2,4), (3,1), (4,5)]  # all the mines in the floor
    # TODO - should initialize the frame from the existing floor
    # and not modify tiles until the wavefront reaches them
    frame = LSExplosion(rows,cols, mine, mines)
    
    for frameNum in range(0,50):
        frame.flamefront()
        ourAnimation.addFrame(frame.get())

    ourAnimation.play(d)


if __name__ == '__main__':
    main()
