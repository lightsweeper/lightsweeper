from LSDisplay import Display
from LSAudio import Audio
from LSFloorConfigure import LSFloorConfig
from LSFloorConfigure import userSelect

import time
import os
import random
#from minesweeper import Minesweeper
#from EightbitSoundboard import Soundboard
#from AnimTestbed import AnimTestbed


#GAMES = [Soundboard, AnimTestbed, Minesweeper]
#PLAYTHISGAME = random.choice(GAMES)

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
    FPS = 30
    SIMULATED_FLOOR = True
    CONSOLE = False

    def __init__(self, GAME, floorConfig=None):
        self.wait = time.sleep
        if floorConfig is None:
            conf = LSFloorConfig()
            conf.selectConfig()
        else:
            conf = LSFloorConfig(floorConfig)
        if conf.isVirtual() is True:
            self.REAL_FLOOR = False
        else:
            self.REAL_FLOOR = True


        self.ROWS = conf.rows
        self.COLUMNS = conf.cols
        print("Board size is {:d}x{:d}".format(self.ROWS, self.COLUMNS))
            
        self.GAME = GAME
        self.audio = Audio(initSound=True)
        self.display = Display(self.ROWS, self.COLUMNS, self.REAL_FLOOR, self.SIMULATED_FLOOR, self.CONSOLE,
                               eventCallback = self.handleTileStepEvent, initScreen=True, conf=conf)
        self.newGame()

        #these are for bookkeeping
        self.frames = 0
        self.frameRenderTime = 0

    def newGame(self):
        self.game = self.GAME(self.display, self.audio, self.ROWS, self.COLUMNS)
        #self.game = Minesweeper(self.display, self.audio, self.ROWS, self.COLUMNS)
        #self.game = Soundboard(self.display, self.audio, self.ROWS, self.COLUMNS)
        #self.game = AnimTestbed(self.display, self.audio, self.ROWS, self.COLUMNS)

    def beginLoop(self):
        while True:
            self.enterFrame()

    def handleTileStepEvent(self, row, col, val):
        if self.game.handlesEvents is not False:
            self.game.handleTileStepEvent(row, col, val)

    def beginEmulatorLoop(self):
        pass

    def enterFrame(self):
        self.frames += 1
        startEnterFrame = time.time()
        if not self.game.ended:
            sensorsChanged = self.pollSensors()
            self.game.heartbeat(sensorsChanged)
            self.display.heartbeat()
            self.audio.heartbeat()
        else:
            self.newGame()
        # print("enterFrame() took" + str(time.time() - startEnterFrame) + " s\n\tpollSensors():" +
        #       str(endSensorsChanged - startSensorsChanged) + " s")
        self.frameRenderTime += (time.time() - startEnterFrame)
        if self.frames % self.FPS == 0:
            print("[{:f} FPS]".format(1.0 / (self.frameRenderTime / self.FPS)), end="\r")
            self.frameRenderTime = 0

    def pollSensors(self):
        sensorsChanged = self.display.pollSensors()
        return sensorsChanged

def main():
    pass
  #  ourGame = PLAYTHISGAME
   # print("Playing {:s}".format(ourGame.__name__))
  #  gameEngine = LSGameEngine(PLAYTHISGAME)
   # gameEngine.beginLoop()

if __name__ == '__main__':
    main()
