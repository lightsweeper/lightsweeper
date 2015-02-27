import time
import os
from minesweeper import Minesweeper
from EightbitSoundboard import Soundboard
from AnimTestbed import AnimTestbed
from LSDisplay import Display
from LSAudio import Audio
from LSFloorConfigure import lsFloorConfig
from LSFloorConfigure import userSelect

#PLAYTHISGAME = Soundboard
#PLAYTHISGAME = AnimTestbed
PLAYTHISGAME = Minesweeper

#enforces the framerate, pushes sensor data to games, and selects games
class GameEngine():
    FPS = 30
    REAL_FLOOR = False
    SIMULATED_FLOOR = True
    CONSOLE = False

    def __init__(self, GAME, floorConfig=None):
        if floorConfig is None:
            try:
                floorFiles = list(filter(lambda ls: ls.endswith(".floor"), os.listdir("./")))
            except:
                raise IOError("No floor configuration found. Try running LSFloorConfigure.py")
            if len(floorFiles) is 1:
                fileName = floorFiles[0]
            else:
                print("\nFound multiple configurations: \n")
                fileName = userSelect(floorFiles, "\nWhich floor configuration would you like to use? ")
        else:
            fileName = configFile
            
            
        conf = lsFloorConfig(fileName)
        self.ROWS = conf.rows
        self.COLUMNS = conf.cols
            
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
    gameEngine = GameEngine(PLAYTHISGAME)
    gameEngine.beginLoop()

if __name__ == '__main__':
    main()
