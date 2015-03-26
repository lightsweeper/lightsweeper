from collections import defaultdict
import time


import Shapes
import Colors
import lsdisplay
import lsanimate



def makeWaves(origin):
# This is a generator that produces a list of cells in expanding "waves" from the origin
    irange = lambda low, high: range(low, high+1) # inclusive range function
    step = 1
    x = origin[0]
    y = origin[1]
    while True:
        thisWave = list()
        for r in irange(x-step, x+step):
            for c in irange(y-step, y+step):
                if r == x-step or r == x+step or c == y-step or c == y+step: # We only want the edges
                    rowCol = (r, c)
                    thisWave.append(rowCol)
        yield(thisWave)
        step += 1

def exploder():
# This generator returns a sequence of masks that makes a tile look as though it is exploding
    explosionSequence =[(0,0,0),
                        (Shapes.DASH, 0,0),
                        (Shapes.H, Shapes.DASH,0),
                        (Shapes.EIGHT, Shapes.H, Shapes.DASH),
                        (Shapes.EIGHT, Shapes.EIGHT, Shapes.H),
                        (Shapes.EIGHT, Shapes.EIGHT, Shapes.EIGHT),
                        (Shapes.ZERO, Shapes.ZERO, Shapes.ZERO),
                        (Shapes.OFF, Shapes.OFF, Shapes.OFF)
                       ]
    for mask in explosionSequence:
        yield mask


# TODO - decide if this should subclass LSFrameGen
class LSExplosion:
#class OBS_LSFrameGen:

    blank = (0, 0, 0)
    #colormask = (Shapes.ZERO, 0,0)
    #diffmask = (Shapes.ONE, Shapes.TWO, Shapes.THREE)
    redZero = (Shapes.ZERO, Shapes.OFF, Shapes.OFF)
    yellowZero = (Shapes.ZERO, Shapes.ZERO, 0)
    whiteZero = (Shapes.ZERO, Shapes.ZERO, Shapes.ZERO)
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
    bomb7 = (Shapes.ZERO, Shapes.ZERO, Shapes.ZERO)
    bomb8 = (Shapes.OFF, Shapes.OFF, Shapes.OFF)
    bombs = [bomb0, bomb0, bomb1, bomb2, bomb3, bomb4, bomb7, bomb6]

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
        self.wavefront = makeWaves(mine)
        self.boom = exploder()
        self.stage = 0
        self.throbbing = False
        self.wi = 0  # A cyclic iterator, each wavefront stays active for 3 frames
        self.allCells = list()
        for row in range(self.rows):
            for col in range(self.cols):
                rowCol = (row, col)
                self.allCells.append(rowCol)

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
            if self.stage is 1:
                if self.wi == 0:
                    self.thisWave = next(self.wavefront)
                    self.wi += 1
                elif self.wi == 2:
                    self.wi = 0
                else:
                    self.wi += 1
            else:
                self.thisWave = list()
            if (True not in [ i in self.allCells for i in self.thisWave ]) and len(self.thisWave) > 0:
                # The wave has reached the edge of the board
                self.stage = 2      # Stop making waves
                self.boom = exploder() # Reset the explosion for the untriggered mines
            if self.stage is 2:
                try:
                    self.boomMask = next(self.boom)
                except StopIteration:
                    self.stage = 3
                    self.throbbing = True

            for col in range(0,self.cols):
                for row in range(0,self.rows):
                    tile = (row,col)
                    # mine cells blow up then throb forever
                    if  tile == self.firstMine:
                        mask = self.blank
                        if self.stage is 0:
                            try:
                                mask = next(self.boom)
                            except StopIteration:
                                self.stage = 1
                    elif self.stage is 2 and tile in self.allMines:
                        mask = self.boomMask
                    else:
                        #mask = self.redZero
                        mask = self.blank
                        # TODO - would be better to not disturb until wavefront gets here
                    if tile in self.thisWave:
                        if self.wi == 1:
                            mask = self.redZero
                        elif self.wi == 2:
                            mask = self.yellowZero
                        else:
                            mask = self.whiteZero
                    if self.throbbing is True and tile in self.allMines:
                        maskIdx = self.frameNum % len(self.bombThrobs)
                        mask = self.bombThrobs[maskIdx]
                    self.edit(row,col,mask)
            self.frameNum = self.frameNum + 1
            #print("Computed frame " + repr(self.frameNum))


def main():
    print("TODO: testing lsexplosion")

    useRealFloor = True
    try:
        realTiles = LSOpen()
    except Exception as e:
        useRealFloor = False

    d = lsdisplay.LSDisplay(realFloor = True, simulatedFloor = True, initScreen=False)
    rows = d.rows
    cols = d.cols

    ourAnimation = lsanimate.LSAnimation()

    #frame = lsanimate.LSFrameGen(rows,cols)
    mine = (4,5)   # this mine is the first to blow
    mines = [(0,1), (1,2), (2,4), (3,1), mine]  # all the mines in the floor
    # TODO - should initialize the frame from the existing floor
    # and not modify tiles until the wavefront reaches them
    print(mines)
    frame = LSExplosion(rows,cols, mine, mines)
    
    for frameNum in range(0,50):
        frame.flamefront()
        ourAnimation.addFrame(frame.get())

    ourAnimation.deleteFrame(7) # Because I'm too lazy to do it right
    ourAnimation.deleteFrame(7) # Yes, we need both of these

    ourAnimation.play(d)


if __name__ == '__main__':
    main()

