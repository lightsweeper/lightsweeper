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
    redH = (Shapes.H, Shapes.OFF, Shapes.OFF)
    redEight = (Shapes.EIGHT, Shapes.OFF, Shapes.OFF)
    whiteEight = (Shapes.EIGHT, Shapes.EIGHT, Shapes.EIGHT)
    yellowEight = (Shapes.EIGHT, Shapes.EIGHT, Shapes.OFF)
    redDash = (Shapes.DASH, Shapes.OFF, Shapes.OFF)
    greenDash = (Shapes.OFF, Shapes.DASH, Shapes.OFF)
    blueDash = (Shapes.OFF, Shapes.OFF, Shapes.DASH)
    redX = (Shapes.H, 0, 0)
    yellowEightPlus = (Shapes.EIGHT, Shapes.EIGHT, Shapes.H)

    waves = (whiteZero, redZero, yellowZero)
    waves = (greenDash, greenZero, blueZero, blueDash)

    #bomb0 = (Shapes.DASH, 0,0)
    #bomb1 = (Shapes.H, Shapes.DASH,0)
    #bomb2 = (Shapes.EIGHT, Shapes.H, Shapes.DASH)
    #bomb3 = (Shapes.EIGHT, Shapes.EIGHT, Shapes.H)
    #bomb4 = whiteEight # (Shapes.EIGHT, Shapes.EIGHT, Shapes.EIGHT)
    #bomb5 = redEight # (Shapes.EIGHT, Shapes.OFF, Shapes.OFF)
    #bomb6 = (Shapes.OFF, Shapes.OFF, Shapes.OFF)
    #bomb7 = (Shapes.ZERO, Shapes.ZERO, Shapes.ZERO)
    #bomb8 = (Shapes.OFF, Shapes.OFF, Shapes.OFF)
    #bombs = [bomb0, bomb0, bomb1, bomb2, bomb3, bomb4, bomb7, bomb6]
    #explosion = [bomb0, bomb1, bomb2, bomb3, bomb4, bomb5, bomb6, bomb7]
    explosion = [redDash, redZero, redEight, yellowEightPlus, whiteEight, redEight, yellowEight, whiteZero]

    bombThrob0 = (Shapes.EIGHT, Shapes.OFF, Shapes.OFF)
    bombThrob1 = (Shapes.H, Shapes.OFF, Shapes.OFF)
    bombThrob2 = (Shapes.DASH, Shapes.OFF, Shapes.OFF)
    bombThrobs = [bombThrob0, bombThrob1, bombThrob2]

    bombThrob0 = (Shapes.ZERO, Shapes.OFF, Shapes.OFF)
    bombThrob1 = (Shapes.SEG_A+Shapes.SEG_B+Shapes.SEG_C+Shapes.SEG_D, Shapes.OFF, Shapes.OFF)
    bombThrob2 = (Shapes.ZERO, Shapes.OFF, Shapes.OFF)
    bombThrob3 = (Shapes.SEG_D+Shapes.SEG_E+Shapes.SEG_F+Shapes.SEG_A, Shapes.OFF, Shapes.OFF)
    bombThrobs = [bombThrob0,bombThrob1,  bombThrob2, bombThrob3]

    bombThrob0 = (Shapes.ZERO, Shapes.OFF, Shapes.OFF)
    bombThrob1 = (Shapes.SEG_A+Shapes.SEG_B+Shapes.SEG_C+Shapes.SEG_D, Shapes.OFF, Shapes.OFF)
    bombThrob2 = (Shapes.ZERO, Shapes.OFF, Shapes.OFF)
    bombThrob3 = (Shapes.SEG_C+Shapes.SEG_D+Shapes.SEG_E+Shapes.SEG_F, Shapes.OFF, Shapes.OFF)
    bombThrob4 = (Shapes.ZERO, Shapes.OFF, Shapes.OFF)
    bombThrob5 = (Shapes.SEG_E+Shapes.SEG_F+Shapes.SEG_A+Shapes.SEG_B, Shapes.OFF, Shapes.OFF)
    bombThrobs = [bombThrob0,bombThrob1,bombThrob2,bombThrob3,bombThrob4,bombThrob5]

    bombThrob0 = redZero # (Shapes.ZERO, Shapes.OFF, Shapes.OFF)
    bombThrob1 = redH # (Shapes.H, Shapes.OFF, Shapes.OFF)
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
                self.edit(row,col, self.blank) # TODO - init to last display
        #self.phase = 0  # phase of wavefronts
        self.explosionStarts = {} # track when each mine starts explosion
        self.explosionStarts[mine] = self.frameNum
        self.wavefrontPassed = set() # track tiles passed by wavefront

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
        if True:
            self.newflamefront()
        else:

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

    def newflamefront(self):
            print("Computing frame " + repr(self.frameNum))
            self.phasePerWave = len(self.waves)
            wavePhase = self.frameNum % self.phasePerWave
            throbPhase = self.frameNum % len(self.bombThrobs) # all throb together
            for tile in self.allCells:
                row = tile[0]
                col = tile[1]
                # run explosion animation for explosion in-process
                if tile in self.explosionStarts.keys():
                    animIdx = self.frameNum - self.explosionStarts[tile]
                    # mine cells blow up
                    if animIdx < len(self.explosion):
                        mask = self.explosion[animIdx] # TODO - merge explosion with exploder() animation
                        #print(repr(tile) + " is exploding") 
                    # then throb forever
                    else:
                        mask = self.bombThrobs[throbPhase]
                        #print(repr(tile) + " is throbbing") 
                    self.edit(row,col,mask)

                # animation for wavefront passing tile
                elif self.inWavefront(tile):
                    if tile in self.allMines:
                        self.explosionStarts[tile] = self.frameNum
                        mask = self.explosion[0]
                        #print(repr(tile) + " just exploded!")
                    else:
                        mask = self.waves[wavePhase]
                        self.wavefrontPassed.add(tile) # can always add to set
                        #print(repr(tile) + " is in wavefront") 
                    self.edit(row,col,mask)

                # if wavefront has passed tile, it should be blank
                elif tile in self.wavefrontPassed:
                    self.edit(row,col,self.blank)

                else:
                    pass

            self.frameNum = self.frameNum + 1

    def inWavefront(self, tile):
        for mine in self.explosionStarts.keys():
            if self.distToMine(tile,mine) == ((self.frameNum - self.explosionStarts[mine]) // self.phasePerWave):
                #print(repr(tile) + " is in wavefront of " + repr(mine)) 
                return True
        return False

    def distToMine(self, tile, mine):
        rowDist = abs(tile[0] - mine[0])
        colDist = abs(tile[1] - mine[1])
        # round off wavefront by noting the corners of the square are farther out
        if rowDist == colDist and rowDist >= 2:
            dist = rowDist + 1
            return dist
        dist = max(rowDist, colDist)
        #print(repr(tile) + " to " + repr(mine) + " = " + repr(dist)) 
        return dist

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
    mine = (2,3)   # this mine is the first to blow
    #mines = [(0,1), (1,2), (2,4), (3,1), mine]  # all the mines in the floor
    mines = [(0,1), (1,2), (3,0), mine]  # all the mines in the floor
    # TODO - should initialize the frame from the existing floor
    # and not modify tiles until the wavefront reaches them
    print(mines)
    frame = LSExplosion(rows,cols, mine, mines)

    # HACK - pretend to initialize per existing display
    # TODO - add init function or arg to constructor
    frame.edit(mine[0],mine[1]-1, LSExplosion.yellowEight)
    frame.edit(mine[0],mine[1]-2, LSExplosion.yellowEight)
    frame.edit(mine[0]-1,mine[1], LSExplosion.yellowEight)
    frame.edit(mine[0]-2,mine[1], LSExplosion.yellowEight)
    
    #for frameNum in range(0,50):
    for frameNum in range(0,40):
        frame.flamefront()
        ourAnimation.addFrame(frame.get())

    ourAnimation.deleteFrame(7) # Because I'm too lazy to do it right
    ourAnimation.deleteFrame(7) # Yes, we need both of these

    ourAnimation.play(d)


if __name__ == '__main__':
    main()

