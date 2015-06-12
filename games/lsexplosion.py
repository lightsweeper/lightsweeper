from collections import defaultdict
import time


from lsapi import Shapes
from lsapi import Colors
import lsapi.lsdisplay as lsdisplay
import lsapi.lsanimate as lsanimate



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

def explodeThenThrob():
# This generator returns a sequence of masks that makes a tile look as though it is exploding
    idx = 0
    while True:
        if idx < len(LSExplosion.explosion):
            mask = LSExplosion.explosion[idx]
            #print("  explodeThenThrob yields " + repr(mask))
            idx = idx + 1
        else:
            mask = LSExplosion.bombThrobs[LSExplosion.throbPhase]
            #print("  explodeThenThrob throbs " + repr(mask))
        yield mask

def animateWavefront(dist = 1, mine = (0,0)):
# This generator returns a sequence of masks to animate a wavefront
# strength of wavefront depends on dist
#
# This generator can make several "random" styles of wavefronts
# that stay consistent for each mine, to represent different kinds of mines.
# This is disabled because the variety makes the wavefronts too confusing.
    idx = 0
    strongWave = dist<=2
    style = 0 # 1
    #style = 1
    #style = (mine[0] + mine[1]) % 3 # comment out for single style wavefronts
    #print("  animateWavefront making style " + repr(style))
    while True:
        if idx < len(LSExplosion.waves):
            if strongWave:
                if style == 0:
                    mask = LSExplosion.waves[idx]
                    mask = LSExplosion.wiggleWaves[idx]
                else:
                    mask = LSExplosion.waves2[idx]
            else:
                if style == 0:
                    mask = LSExplosion.weakWaves[idx]
                else:
                    mask = LSExplosion.weakWaves2[idx]

            #print("  animateWavefront yields " + repr(mask))
            idx = idx + 1
        else:
            mask = LSExplosion.blank
            #print("  animateWavefront blanking now")
        yield mask


# TODO - decide if this should subclass LSFrameGen
class LSExplosion:
#class OBS_LSFrameGen:

    blank = (0, 0, 0)
    #colormask = (Shapes.ZERO, 0,0)
    #diffmask = (Shapes.ONE, Shapes.TWO, Shapes.THREE)
    redZero = (Shapes.ZERO, Shapes.OFF, Shapes.OFF)
    yellowZero = (Shapes.ZERO, Shapes.ZERO, 0)
    violetZero = (Shapes.ZERO, 0, Shapes.ZERO)
    whiteZero = (Shapes.ZERO, Shapes.ZERO, Shapes.ZERO)
    greenZero = (0, Shapes.ZERO, 0)
    blueZero = (0, 0, 126)
    cyanZero = (0, Shapes.ZERO, Shapes.ZERO)
    cyanZero = (0, Shapes.ZERO, Shapes.ZERO)
    redH = (Shapes.H, Shapes.OFF, Shapes.OFF)
    redEight = (Shapes.EIGHT, Shapes.OFF, Shapes.OFF)
    whiteEight = (Shapes.EIGHT, Shapes.EIGHT, Shapes.EIGHT)
    yellowEight = (Shapes.EIGHT, Shapes.EIGHT, Shapes.OFF)
    redDash = (Shapes.DASH, Shapes.OFF, Shapes.OFF)
    violetDash = (Shapes.DASH, Shapes.OFF, Shapes.DASH)
    greenDash = (Shapes.OFF, Shapes.DASH, Shapes.OFF)
    yellowDash = (Shapes.DASH, Shapes.DASH, Shapes.OFF)
    blueDash = (Shapes.OFF, Shapes.OFF, Shapes.DASH)
    cyanDash = (Shapes.OFF, Shapes.DASH, Shapes.DASH)
    redX = (Shapes.H, 0, 0)
    yellowEightPlus = (Shapes.EIGHT, Shapes.EIGHT, Shapes.H)

    # more shapes
    pipes = Shapes.SEG_B + Shapes.SEG_C + Shapes.SEG_E + Shapes.SEG_F # pipes is ||
    dashX3 = Shapes.SEG_A + Shapes.SEG_D + Shapes.SEG_G # three horizontal dashes

    # weaker wavefront farther from explosion
    cyanPipes = (0, pipes, pipes)
    violetPipes = (pipes, 0, pipes)
    weakWaves = (cyanDash, cyanPipes, violetPipes, violetDash)

    # weaker wavefront farther from explosion
    zig = Shapes.SEG_B + Shapes.SEG_G + Shapes.SEG_E
    zag = Shapes.SEG_C + Shapes.SEG_G + Shapes.SEG_F
    cyanZag = (0, zag, zag)
    cyanZig = (0, zig, zig)
    violetZag = (zag, 0, zag)
    violetZig = (zig, 0, zig)
    weakWaves = (cyanDash, cyanZig, violetZag, violetDash) # pretty good
    yellowZig = (zig, zig, 0)
    yellowZag = (zag, zag, 0)
    weakWaves2 = (yellowDash, yellowZig, yellowZag, yellowDash)
    weakWaves2 = (yellowDash, yellowDash, yellowDash, yellowDash)

    # strong wavefronts
    waves = (whiteZero, redZero, yellowZero)
    waves = (greenDash, greenZero, blueZero, blueDash)
    waves = (cyanDash, cyanZero, violetZero, violetDash) # pretty good

    yellowDashX3 = (dashX3, dashX3, 0)
    waves2 = (yellowDash, yellowZero, yellowZero, yellowDash)
    waves2 = (yellowDash, yellowDashX3, yellowDashX3, yellowDash) # pretty good

    #wiggleWaves = (cyanZag, cyanZig, violetZag, violetZig) # looks much like weakWaves
    cyanFive = (0, Shapes.FIVE, Shapes.FIVE)
    cyanTwo = (0, Shapes.TWO, Shapes.TWO)
    violetFive = (Shapes.FIVE, 0, Shapes.FIVE)
    violetTwo = (Shapes.TWO, 0, Shapes.TWO)
    wiggleWaves = (cyanFive, cyanTwo, violetFive, violetTwo) # more flash than weakWaves

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

    # spinning red circle segments
    throb0 = (Shapes.SEG_A+Shapes.SEG_B+Shapes.SEG_C+Shapes.SEG_D, Shapes.OFF, Shapes.OFF)
    throb1 = (Shapes.SEG_B+Shapes.SEG_C+Shapes.SEG_D+Shapes.SEG_E, Shapes.OFF, Shapes.OFF)
    throb2 = (Shapes.SEG_C+Shapes.SEG_D+Shapes.SEG_E+Shapes.SEG_F, Shapes.OFF, Shapes.OFF)
    throb3 = (Shapes.SEG_D+Shapes.SEG_E+Shapes.SEG_F+Shapes.SEG_A, Shapes.OFF, Shapes.OFF)
    throb4 = (Shapes.SEG_E+Shapes.SEG_F+Shapes.SEG_A+Shapes.SEG_B, Shapes.OFF, Shapes.OFF)
    throb5 = (Shapes.SEG_F+Shapes.SEG_A+Shapes.SEG_B+Shapes.SEG_C, Shapes.OFF, Shapes.OFF)
    bombThrobs = [throb0,throb1,throb2,throb3,throb4,throb5]

    # spinning red circle with one segment missing
    throb0 = (Shapes.SEG_A+Shapes.SEG_B+Shapes.SEG_C+Shapes.SEG_D+Shapes.SEG_E, Shapes.OFF, Shapes.OFF)
    throb1 = (Shapes.SEG_C+Shapes.SEG_D+Shapes.SEG_E+Shapes.SEG_F+Shapes.SEG_A, Shapes.OFF, Shapes.OFF)
    throb2 = (Shapes.SEG_E+Shapes.SEG_F+Shapes.SEG_A+Shapes.SEG_B+Shapes.SEG_C, Shapes.OFF, Shapes.OFF)
    bombThrobs = [throb0,throb1,throb2]

    # alternating red H and 0
    bombThrobs = [redZero, redH] # not bad, have been using a while
    bombThrobs = [redZero, redDash] # maybe better, more throbby

    throbPhase = 0 # mines throb together after exploding - class vble for generators to use

    version = 0;

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
        self.unblasted = list()
        for row in range(self.rows):
            for col in range(self.cols):
                rowCol = (row, col)
                self.allCells.append(rowCol)
                self.unblasted.append(rowCol)
                self.edit(row,col, self.blank) # TODO - init to last display
        #self.phase = 0  # phase of wavefronts
        self.explosionStarts = {} # track when each mine starts explosion
        self.explosionStarts[mine] = self.frameNum
        self.unblasted.remove(mine) # remove known mine from undisturbed list
        self.wavefrontPassed = set() # track tiles passed by wavefront

        LSExplosion.version = (LSExplosion.version + 1) % 3
        #LSExplosion.version = 1
        print("Animation version " + repr(LSExplosion.version))


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

            # wavefront triggers mine explosions
            if LSExplosion.version == 1:
                return self.newflamefront()

            # use generators for explosions and wavefronts
            elif LSExplosion.version == 2:
                return self.genflamefront()

            # original explosion animation
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
            #print("Computing frame " + repr(self.frameNum))
            self.phasePerWave = len(self.waves)
            wavePhase = self.frameNum % self.phasePerWave
            LSExplosion.throbPhase = self.frameNum % len(self.bombThrobs) # all throb together

            # run explosion animation
            for tile in self.explosionStarts.keys():
                animIdx = self.frameNum - self.explosionStarts[tile]
                # mine cells blow up
                if animIdx < len(self.explosion):
                    mask = self.explosion[animIdx]
                    #print(repr(tile) + " is exploding")
                # then throb forever
                else:
                    mask = self.bombThrobs[LSExplosion.throbPhase]
                    #print(repr(tile) + " is throbbing")
                self.edit(tile[0],tile[1],mask)

            # animation for wavefront passing tile
            for tile in self.wavefrontPassed:
                dist = self.inWavefront(tile)[0] # dist is first val in tuple

                # if wavefront has passed tile, it should be blank
                if dist == -1:
                    mask = self.blank
                # strong wavefront
                elif dist <= 2: # 2 rings of strong wavefront
                    mask = self.waves[wavePhase]
                    #print(repr(tile) + " is in strong wavefront")
                # weaker wavefront farther away
                else:
                    mask = self.weakWaves[wavePhase]
                    #print(repr(tile) + " is in weak wavefront")
                self.edit(tile[0],tile[1],mask)

            # process cells that have not been blasted
            for tile in self.unblasted[:]: # use slice so remove during iterate works
                if wavePhase == 0: # wavefront moves into tile in first phase
                    continue; # no need to check for changes
                # animation for wavefront passing tile
                dist = self.inWavefront(tile)[0] # dist is first val in tuple
                if dist > 0:
                    self.unblasted.remove(tile) # remove blasted tile
                    # mine explodes when wavefront reaches it
                    if tile in self.allMines:
                        self.explosionStarts[tile] = self.frameNum
                        mask = self.explosion[0]
                        #print(repr(tile) + " just exploded!")
                    # strong wavefront
                    elif dist <= 2: # 2 rings of strong wavefront
                        mask = self.waves[wavePhase]
                        self.wavefrontPassed.add(tile) # can always add to set
                        #print(repr(tile) + " is in strong wavefront")
                    # weaker wavefront farther away
                    else:
                        mask = self.weakWaves[wavePhase]
                        self.wavefrontPassed.add(tile) # can always add to set
                        #print(repr(tile) + " is in weak wavefront")
                    self.edit(tile[0],tile[1],mask)

            self.frameNum = self.frameNum + 1

    def genflamefront(self):
    # use generators for explosions and wavefronts
        #print("Gen frame " + repr(self.frameNum))
        if self.frameNum == 0:
            self.explosionGens = {} # store explosion generators
            self.explosionGens[self.firstMine] = explodeThenThrob()
            self.wavefrontGens = {} # store wavefront generators
        self.phasePerWave = len(self.waves)
        wavePhase = self.frameNum % self.phasePerWave
        LSExplosion.throbPhase = self.frameNum % len(self.bombThrobs) # all throb together

        # run explosion animation generator on exploded mines
        # exploded mines stay in explosionGens forever
        for tile in self.explosionGens.keys():
            mask = next(self.explosionGens[tile])
            self.edit(tile[0],tile[1],mask)

        # run wavefront passing tile animation generator
        # mines in wavefront stay in wavefrontGens forever
        for tile in self.wavefrontGens.keys():
            # wavefront moves into tile in first phase
            # no need to check for changes in other phases
            if wavePhase == 0:
                waveTuple = self.inWavefront(tile)
                dist = waveTuple[0] # dist is first val in tuple
                waveMine = waveTuple[1] # active mine is second val in tuple
                if dist > 0:
                    #print(repr(tile) + " is back in wavefront")
                    # mine explodes when wavefront reaches it
                    # SHOULD NOT HAPPEN HERE - remove when satisfied
                    if tile in self.allMines:
                        self.explosionStarts[tile] = self.frameNum # used by inWavefront()
                        self.explosionGens[tile] = explodeThenThrob()
                        mask = next(self.explosionGens[tile]) # first explosion animation
                        print(repr(tile) + " exploded, but was already in wavefrontGens!")
                    else:
                        # tile in wavefront again, set new generator
                        self.wavefrontGens[tile] = animateWavefront(dist, waveMine)

            # generate wavefront animation each phase
            mask = next(self.wavefrontGens[tile])
            self.edit(tile[0],tile[1],mask)

        # test undisturbed tiles to see if in wavefront
        # wavefront moves into tile in first phase
        # no need to check for changes in other phases
        # tiles do not change until hit by a wavefront
        if wavePhase == 0:
            for tile in self.unblasted[:]: # use slice so remove during iterate works
                waveTuple = self.inWavefront(tile)
                dist = waveTuple[0] # dist is first val in tuple
                waveMine = waveTuple[1] # active mine is second val in tuple
                if dist > 0:
                    self.unblasted.remove(tile) # remove disturbed tile
                    # mine explodes when wavefront reaches it
                    if tile in self.allMines:
                        self.explosionStarts[tile] = self.frameNum # used by inWavefront()
                        self.explosionGens[tile] = explodeThenThrob()
                        mask = next(self.explosionGens[tile]) # first explosion animation
                        #print(repr(tile) + " just exploded!")
                    # tile is in wavefront
                    else:
                        self.wavefrontGens[tile] = animateWavefront(dist, waveMine)
                        mask = next(self.wavefrontGens[tile]) # first wavefront animation
                        #print(repr(tile) + " is in wavefront")
                    self.edit(tile[0],tile[1],mask)

        # genflamefront is done with this frame
        self.frameNum = self.frameNum + 1

    # returns distance from mine if in wavefront or -1 if not
    # client indicates the minimum distance it cares about,
    #   typically the max distance for closest-in wavefront
    # returns tuple (distance, active mine)
    def inWavefront(self, tile, distThresh=2):
        waves = 0
        closeDist = 999
        closeMine = None
        for mine in self.explosionStarts.keys():
            dist = self.distToMine(tile,mine)
            if dist == ((self.frameNum - self.explosionStarts[mine]) // self.phasePerWave):
                #print(repr(tile) + " is in wavefront of " + repr(mine))
                waves = waves + 1
                if closeDist > dist:
                    closeDist = dist
                    closeMine = mine
                # stop looking if explosion is as close as we care about
                if dist <= distThresh:
                    break
        # return the closest wavefront we found
        if waves > 0:
            #if waves > 1: print(repr(tile) + " is in " + repr(waves) + " wavefronts")
            return (closeDist, closeMine)
        return (-1, closeMine)

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

    d = lsdisplay.LSDisplay(realFloor = True, simulatedFloor = True, initScreen=False)
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
    #frame.edit(mine[0],mine[1]-1, LSExplosion.yellowEight)
    #frame.edit(mine[0],mine[1]-2, LSExplosion.yellowEight)
    #frame.edit(mine[0]-1,mine[1], LSExplosion.yellowEight)
    #frame.edit(mine[0]-2,mine[1], LSExplosion.yellowEight)
    for row in range(rows):
        for col in range(cols):
            frame.edit(row,col, LSExplosion.greenZero)

    starttime = time.time()

    #for frameNum in range(0,50):
    for frameNum in range(0,40):
        frame.flamefront()
        ourAnimation.addFrame(frame.get())

    endtime = time.time()
    gentime = endtime - starttime
    # newflamefront, with no printing, 6x8 38 frames <= .09 sec
    print("frame calcs took {:f} seconds".format(gentime))

    #ourAnimation.deleteFrame(7) # Because I'm too lazy to do it right
    #ourAnimation.deleteFrame(7) # Yes, we need both of these

    ourAnimation.play(d)


if __name__ == '__main__':
    main()

