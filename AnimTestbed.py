from lsgame import LSGameEngine
from lsgame import Frame

import Colors
import Shapes

import time

class AnimTestbed():
    def __init__(self, display, audio, rows, cols):
        self.rows = rows
        self.cols = cols
        self.display = display
        self.audio = audio
        self.ended = False
        self.handlesEvents = False
        self.frame = 0
        self.currentColors = [Colors.RED, Colors.YELLOW, Colors.GREEN, Colors.CYAN, Colors.BLUE, Colors.MAGENTA]

    def heartbeat(self, sensorsChanged):

        self.display.setAllCustom(self.currentColors + [Colors.BLACK])
        color = self.currentColors.pop()
        self.currentColors.insert(0, color)

    def ended(self):
        pass
        
def main():
    gameEngine = LSGameEngine(AnimTestbed)
    gameEngine.beginLoop()

if __name__ == '__main__':
    main()
