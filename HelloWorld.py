#!/usr/bin/python3

import random

from lsgame import *

class HelloWorld(LSGame):
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
        print("Hello tile at: ({:d},{:d})".format(row,col))
        self.playTileSound(row, col)
        self.display.setColor(row, col, Colors.RANDOM())

    def stepOff(self, row, col):
        print("Goodbye tile at: ({:d},{:d})".format(row,col))
        self.gameOver() # Cause game to end

    def playTileSound(self, row, col):
        self.audio.playSound("Blop.wav")

def main():
    gameEngine = LSGameEngine(HelloWorld)
    gameEngine.beginLoop()

if __name__ == "__main__":
    main()
