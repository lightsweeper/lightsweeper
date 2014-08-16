import time
from minesweeper import Minesweeper
from LSDisplay import Display
from LSAudio import Audio

#enforces the framerate, pushes sensor data to games, and selects games
class GameEngine():
    FRAME_GAP = 1 / 30
    REAL_FLOOR = False
    EMULATOR_FLOOR = False
    CONSOLE = True

    def __init__(self):
        self.display = Display(3, 3, self.REAL_FLOOR, self.EMULATOR_FLOOR, self.CONSOLE)
        self.audio = Audio()
        self.game = Minesweeper(self.display, self.audio, 3, 3)

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
        else:
            print("~New game~")
            self.game = Minesweeper(self.display, self.audio, 3, 3)

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
    if not gameEngine.EMULATOR_FLOOR:
        gameEngine.beginLoop()
    else:
        gameEngine.beginEmulatorLoop()

if __name__ == '__main__':
    main()