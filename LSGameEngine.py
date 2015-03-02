import time
import os
import random
from minesweeper import Minesweeper
from EightbitSoundboard import Soundboard
from AnimTestbed import AnimTestbed
from LSDisplay import Display
from LSAudio import Audio
from LSFloorConfigure import LSFloorConfig
from LSFloorConfigure import userSelect

GAMES = [Soundboard, AnimTestbed, Minesweeper]
PLAYTHISGAME = random.choice(GAMES)

#enforces the framerate, pushes sensor data to games, and selects games
class GameEngine():
    FPS = 30
    SIMULATED_FLOOR = True
    CONSOLE = False

    def __init__(self, GAME, floorConfig=None):

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
                               eventCallback = self.handleTileStepEvent, initScreen=True)
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
            print(str(1.0 / (self.frameRenderTime / self.FPS)) + " FPS")
            self.frameRenderTime = 0

    def wait(self, seconds):
        # self.pollSensors()
        currentTime = time.time()
        while time.time() - currentTime < seconds:
            pass

    def pollSensors(self):
        sensorsChanged = self.display.pollSensors()
        return sensorsChanged

def main():
    ourGame = PLAYTHISGAME
    print("Playing {:s}".format(ourGame.__name__))
    gameEngine = GameEngine(PLAYTHISGAME)
    gameEngine.beginLoop()

if __name__ == '__main__':
    main()
