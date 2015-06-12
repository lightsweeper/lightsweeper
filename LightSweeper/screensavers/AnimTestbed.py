#!/usr/bin/env python3

from lsgame import *

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
  #      for r in range(0,self.rows):
  #          for c in range(0,self.cols):
  #              self.display.setCustom(r,c, self.currentColors + [Colors.BLACK])
        color = self.currentColors.pop()
        self.currentColors.insert(0, color)
        
def main():
    gameEngine = LSGameEngine(AnimTestbed)
    gameEngine.beginLoop()

if __name__ == '__main__':
    main()
