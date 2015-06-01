#!/usr/bin/python3
import Colors
import Shapes
import random
from lsgame import LSGameEngine
from lsgame import Move

class HelloWorld():
    def __init__(self, display, audio, rows, cols):
        self.display = display
        self.audio = audio
        self.rows = rows
        self.cols = cols
        self.ended = False
        self.handlesEvents = True
        print("Hello world __init__()")
        for i in range(0, rows):
            for j in range(0, cols):
                self.display.set(i, j, Shapes.ZERO, Colors.RANDOM())

    def heartbeat(self, sensorsChanged):
        print("Hello world heartbeat()")
        pass

    def stepOn(self, row, col):
        print("Hello tile at: ({:s},{:s})".format(row,col))
        self.playTileSound(row, col)
        self.display.setColor(row, col, Colors.RANDOM())

    def stepOff(self, row, col):
        print("Goodbye tile at: ({:s}.{:s})".format(row,col))

    def playTileSound(self, row, col):
        self.audio.playSound("Blop.wav")

    def ended(self):
        return self.ended

def main():
    import lsgame
    gameEngine = lsgame.LSGameEngine(HelloWorld)
    gameEngine.beginLoop()

if __name__ == "__main__":
    main()
