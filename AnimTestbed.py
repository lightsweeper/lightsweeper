import Colors
import Shapes
from lightsweeper import Frame
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
        for i in range(self.rows):
            for j in range(self.cols):
                self.display.setCustom(i, j, self.currentColors + [Colors.BLACK])
        color = self.currentColors.pop()
        self.currentColors.insert(0, color)

    def ended(self):
        pass
        
def main():
    import lsgame
    gameEngine = lsgame.GameEngine(AnimTestbed)
    gameEngine.beginLoop()

if __name__ == '__main__':
    main()
