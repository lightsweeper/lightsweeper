import time
from minesweeper import Minesweeper
from EightbitSoundboard import Soundboard
from LSDisplay import Display
from LSAudio import Audio

#enforces the framerate, pushes sensor data to games, and selects games
class GameEngine():
    FRAME_GAP = 1 / 30
    REAL_FLOOR = True
    SIMULATED_FLOOR = False
    CONSOLE = False
    ROWS = 3
    COLUMNS = 8

    def __init__(self):
        self.audio = Audio(initSound=True)
        self.display = Display(self.ROWS, self.COLUMNS, self.REAL_FLOOR, self.SIMULATED_FLOOR, self.CONSOLE,
                               eventCallback = self.handleTileStepEvent, initScreen=True)
        self.newGame()

    def newGame(self):
        #self.game = Minesweeper(self.display, self.audio, self.ROWS, self.COLUMNS)
        self.game = Soundboard(self.display, self.audio, self.ROWS, self.COLUMNS)

    def beginLoop(self):
        while True:
        #for i in range(0, 100):
            #self.wait(self.FRAME_GAP)

            self.enterFrame()

    def handleTileStepEvent(self, row, col, val):
        if self.game.handlesEvents is not False:
            self.game.handleTileStepEvent(row, col, val)

    def beginEmulatorLoop(self):
        pass

    def enterFrame(self):
        startEnterFrame = time.time()
        if not self.game.ended:
            #startSensorsChanged = time.time()
            sensorsChanged = self.pollSensors()
            #endSensorsChanged = time.time()
            self.game.heartbeat(sensorsChanged)
            self.display.heartbeat()
            self.audio.heartbeat()
        else:
            self.newGame()
        #print("enterFrame() took" + str(time.time() - startEnterFrame) + "ms\n\tpollSensors():" +
        #      str(endSensorsChanged - startSensorsChanged) + "ms")

    def wait(self, seconds):
        # self.pollSensors()
        currentTime = time.time()
        while time.time() - currentTime < seconds:
            pass

    def pollSensors(self):
        sensorsChanged = self.display.pollSensors()
        return sensorsChanged

def main():
    gameEngine = GameEngine()
    gameEngine.beginLoop()

if __name__ == '__main__':
    main()
