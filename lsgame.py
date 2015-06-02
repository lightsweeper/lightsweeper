""" Contains methods related to LightSweeper games """

import os
import random
import threading
import time

from collections import defaultdict

from lsdisplay import LSDisplay
from lsaudio import LSAudio
from lsconfig import LSFloorConfig
from lsconfig import userSelect

#has a list of changes to the board
class Frame():
    def __init__(self, row, col):
        self.rows = row
        self.columns = col
        self.heartbeats = 1
        self.shapes = {}
        self.colors = {}

    def hasShapeChangesFor(self, row, col):
        val = True
        try:
            self.shapes[(row, col)]
        except:
            val = False
        return val

    def hasColorChangesFor(self, row, col):
        val = True
        try:
            self.colors[(row, col)]
        except:
            val = False
        return val

    def setAllColor(self, color):
        for row in range(self.rows):
            for col in range(self.columns):
                self.colors[(row, col)] = color

    def setColor(self, row, col, color):
        self.colors[(row, col)] = color

    def setAllShape(self, shape):
        for row in range(self.rows):
            for col in range(self.columns):
                self.shapes[(row, col)] = shape

    def setShape(self, row, col, shape):
        self.shapes[(row, col)] = shape

    def getShape(self, row, col):
        return self.shapes[(row, col)]

    def getColor(self, row, col):
        return self.colors[(row, col)]

    def addShape(self, row, col, shape):
        self.shapes[(row, col)] = shape

    def addColor(self, row, col, color):
        self.colors[(row, col)] = color

class Move():
    def __init__(self, row, col, val):
        self.row = row
        self.col = col
        self.val = val


#enforces the framerate, pushes sensor data to games, and selects games
class LSGameEngine():
    initLock = threading.Event()
    FPS = 30
    SIMULATED_FLOOR = True
    CONSOLE = False
    numPlays = 0
    _warnings = []

    def __init__(self, GAME, floorConfig=None, loop=True):
        self.loop = loop
        self.wait = time.sleep
        if floorConfig is None:
            conf = LSFloorConfig()
            conf.selectConfig()
        else:
            conf = LSFloorConfig(floorConfig)
        if conf.containsVirtual() is True:
            self.REAL_FLOOR = False
        else:
            self.REAL_FLOOR = True

        self.ROWS = conf.rows
        self.COLUMNS = conf.cols
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Board size is {:d}x{:d}".format(self.ROWS, self.COLUMNS))
            
        self.GAME = GAME
        self.audio = LSAudio(initSound=True)
        self.display = LSDisplay(conf=conf, eventCallback = self.handleTileStepEvent, initScreen=True)
        self.moves = []
        self.newGame()
        self.sensorMatrix = defaultdict(lambda: defaultdict(int))

        #these are for bookkeeping
        self.frames = 0
        self.frameRenderTime = 0
        
        # This lock prevents handleTileStepEvent() from being run by polling loops before init is complete
        self.initLock.set()

    def newGame(self):
        try: # Game is a list of game classes, pick one at random
            GAME = random.choice(self.GAME)
        except: # Game was specified
            GAME = self.GAME
        self.currentGame = GAME.__name__
        self.game = GAME(self.display, self.audio, self.ROWS, self.COLUMNS)
        self.numPlays += 1
        print("\nPlaying {:s}...".format(self.currentGame))

    def beginLoop(self, plays = 0):
        while True:
            if plays is not 0 and self.numPlays <= plays:
                self.enterFrame()
            elif plays is 0:
                self.enterFrame()
            else:
                print(" G A M E  O V E R ")
                self.display.clearAll()
                self.display.setMessage(int(self.display.rows/2)-1,"GAME OVER")
                self.display.heartbeat()
                input("--Press any key to exit--\n")
                self.display.floor.saveAndExit(0)

    def handleTileStepEvent(self, row, col, sensorPcnt):
        self.initLock.wait()
        sensorPcnt = int(sensorPcnt)
        if sensorPcnt is 0:
            try:
                self.game.stepOff(row, col)
            except AttributeError:   # Game has no stepOff() method
                self._warnOnce("{:s} has no stepOff() method.".format(self.currentGame))
        #    print("stepOff: ({:d},{:d})".format(row, col)) # Debugging
            self.moves = [x for x in self.moves if x.row is not row and x.col is not col]
        else:
            if self.sensorMatrix[row][col] is 0:
                try:
                    self.game.stepOn(row, col)
                except AttributeError:  # Game has no stepOn() method
                    self._warnOnce("{:s} has no stepOn() method.".format(self.currentGame))
             #   print("stepOn: ({:d},{:d})".format(row, col)) # Debugging
                self.moves.append(Move(row, col, sensorPcnt))
        self.sensorMatrix[row][col] = sensorPcnt
#            try:
#                self.game.handleTileStepEvent(row, col, sensorPcnt)
#            except AttributeError:   # Game has no event handler
#                print("({:d},{:d}): {:d}%".format(row,col,sensorPcnt)) # debugging
#                pass

    def enterFrame(self):
        self.frames += 1
        startEnterFrame = time.time()
        if not self.game.ended:
            self.game.heartbeat(self.moves)
            self.display.heartbeat()
            self.audio.heartbeat()
        else:
            self.newGame()

        # print("enterFrame() took" + str(time.time() - startEnterFrame) + " s\n\tpollSensors():" +
        #       str(endSensorsChanged - startSensorsChanged) + " s")
        self.frameRenderTime += (time.time() - startEnterFrame)
        if self.frames % self.FPS == 0:
            print(" [{:f} FPS]".format(1.0 / (self.frameRenderTime / self.FPS)), end="\r")
            self.frameRenderTime = 0

    def _warnOnce(self, warning):
        if warning not in self._warnings:
            print("WARNING: {:s}".format(warning))
            self._warnings.append(warning)

def main():
    print("TODO: testing lsgame")

if __name__ == '__main__':
    main()
