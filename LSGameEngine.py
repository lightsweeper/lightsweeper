import time
from minesweeper import Minesweeper
from EightbitSoundboard import Soundboard
from LSDisplay import Display
from LSAudio import Audio

#enforces the framerate, pushes sensor data to games, and selects games
class GameEngine():
    FRAME_GAP = 1 / 30
    REAL_FLOOR = True
    CONSOLE = False
    ROWS = 6
    COLUMNS = 7

    def __init__(self):
        self.display = Display(self.ROWS, self.COLUMNS, self.REAL_FLOOR, self.CONSOLE)
        self.audio = Audio()
        self.newGame()

    def newGame(self):
        #self.game = Minesweeper(self.display, self.audio, 3, 3)
        self.game = Soundboard(self.display, self.audio, self.ROWS, self.COLUMNS)

    def beginLoop(self):
        while True:
            self.wait(self.FRAME_GAP)
            self.enterFrame()

    def beginEmulatorLoop(self):
        #this is necessary because Qt is event driven, and so must drive the game loop instead of GameEngine doing it
        self.display.beginQtLoop(self.enterFrame, self.FRAME_GAP)

    def enterFrame(self):
        if not self.game.ended:
            sensorsChanged = self.pollSensors()
            self.game.heartbeat(sensorsChanged)
            self.display.heartbeat()
            self.audio.heartbeat()
        else:
            self.newGame()

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