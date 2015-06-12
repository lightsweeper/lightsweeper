""" Contains methods related to LightSweeper games """

import copy
import os
import random
import threading
import time

from collections import defaultdict

from lightsweeper.lsdisplay import LSDisplay
from lightsweeper.lsaudio import LSAudio
from lightsweeper.lsconfig import LSFloorConfig
from lightsweeper.lsconfig import userSelect


from lightsweeper import Colors
from lightsweeper import Shapes

FPS = 30

class LSGame():
    def __init__(game, display, audio, rows, cols):

        # Standard game setup
        game.display = display
        game.audio = audio
        game.rows = rows
        game.cols = cols
        game.ended = False
        game.duration = 0
        game.frameRate = FPS
        game.display.clearAll()

    def over (game, score=None):
        # TODO: Pass the score to a the scoreboard class
        print("[Game Over]")
        game.ended = True
        
class LSScreenSaver(LSGame):
    def __init__(game, *args, **kwargs):
        super().__init__(*args, **kwargs)
        game.duration = 10
        game.frameRate = 15

from lightsweeper.screensavers import screensavers

SAVERS = screensavers.screensaverList


#enforces the framerate, pushes sensor data to games, and selects games
class LSGameEngine():
    initLock = threading.Event()
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
        self.sensorMatrix = defaultdict(lambda: defaultdict(int))
        self.newGame(self.GAME)

        #these are for bookkeeping
        self.frames = 0
        self.frameRenderTime = 0
        
        # This lock prevents handleTileStepEvent() from being run by polling loops before init is complete
        self.initLock.set()

    def newGame(self, Game):
        try: # Game is a list of game classes, pick one at random
            GAME = random.choice(Game)
        except: # Game was specified
            GAME = Game
        self.currentGame = GAME.__name__

        print("LSGameEngine: Starting {:s}...".format(self.currentGame))
        self.game = GAME(self.display, self.audio, self.ROWS, self.COLUMNS)
        self.startGame = time.time()
     #   game = self.game
     #   self.game.frameRate = FPS
        self.game.sensors = self.sensorMatrix
        self.numPlays += 1   # TODO: Check if type is screensaver
        try:
            self.game.init()
        except AttributeError:
            self._warnOnce("{:s} has no init() method.".format(self.currentGame))


    def beginLoop(self, plays = 0):
        while True:
            if plays is not 0 and self.numPlays <= plays:
                self.enterFrame()
            elif plays is 0:
                self.enterFrame()
            else:
                self.insertCoin()

    def insertCoin(self):
        self.gameOver()
        # TODO: Instead of quitting, go to game/demo screen and wait for someone to reset

    def gameOver(self):
        print(" G A M E  O V E R ")
        self.display.clearAll()
        self.display.setMessage(int(self.display.rows/2)-1,"GAME OVER")
        self.display.heartbeat()
        input("--Press any key to exit--\n")
        self.display.floor.saveAndExit(0)

    def handleTileStepEvent(self, row, col, sensorPcnt):
        self.initLock.wait()
        if int(sensorPcnt) is 0:
            try:
                self.game.stepOff(row, col)
            except AttributeError as e:   # Game has no stepOff() method
                if "object has no attribute 'stepOff'" in str(e):
                    self._warnOnce("{:s} has no stepOff() method.".format(self.currentGame))
                else:
                    raise(e)
         #   print("stepOff: ({:d},{:d})".format(row, col)) # Debugging
            self.moves = [x for x in self.moves if x[0] is not row and x[1] is not col]
        else:
            if self.sensorMatrix[row][col] is 0:
                if sensorPcnt > 20:                 # Only trigger > 20%, hack to guard against phantom sensors
                                                    # TODO: This but better
                    try:
                        self.game.stepOn(row, col)
                    except AttributeError as e:   # Game has no stepOn() method
                        if "object has no attribute 'stepOn'" in str(e):
                            self._warnOnce("{:s} has no stepOn() method.".format(self.currentGame))
                        else:
                            raise(e)
                 #   print("stepOn: ({:d},{:d})".format(row, col)) # Debugging
                    m = (row, col)
                    self.moves.append(m)
        self.sensorMatrix[row][col] = int(sensorPcnt)

    def pauseGame (self):
        print("Game is paused.")
        while self.game.frameRate < 1:
            pass
        print("Game resuming...")

    def enterFrame(self):
        if self.game.duration is not 0:
            playTime = (time.time() - self.startGame)
            if playTime > self.game.duration:
            #    self.game.ended = True
                self.newGame(self.GAME)
        startEnterFrame = time.time()
        if not self.game.ended:
            self.game.heartbeat(self.moves)
            self.display.heartbeat()
            self.audio.heartbeat()
        else:
            self.newGame(SAVERS)    # Super hacky, should be in gameOver
         #   self.newGame(self.GAME)
        frameRenderTime = (time.time() - startEnterFrame)
        self.wait(self.padFrame(frameRenderTime))

    def padFrame(self, renderTime):
        if self.game.frameRate is 0:
            self.pauseGame()
        spaces = " " * 15
        fps = 1.0/renderTime
        if fps < self.game.frameRate or self.game.frameRate < 0:
            print("{1:s}{0:.4f} FPS".format(1.0/renderTime, spaces), end="\r")
            return(0)
        else:
            print("{1:s}{0:.4f} FPS".format(self.game.frameRate, spaces), end="\r")
            return((1.0/self.game.frameRate)-renderTime)
        print(spaces * 2, end="\r")

    def _warnOnce(self, warning):
        if warning not in self._warnings:
            print("WARNING: {:s}".format(warning))
            self._warnings.append(warning)

def main():
    print("TODO: testing lsgame")

if __name__ == '__main__':
    main()
