#!/usr/bin/python3

import random
from copy import copy

from lightsweeper.lsapi import *

class Calibrate(LSGame):

    def init(self):
        pass

    def heartbeat(self, activeTiles):

        for tile in activeTiles:
            row, col = tile
            self.printPcnt(row, col, self.sensors[row][col])

        
    def printPcnt (self, r, c, pcnt):
        o = int(pcnt/10)
        if o  == 0:
            color = Colors.GREEN
            print("({:d},{:d}): {:d}%    ".format(r, c, pcnt))
        elif o < 4:
            color = Colors.CYAN
        elif o < 7:
            color = Colors.YELLOW
        elif o < 9:
            color = Colors.MAGENTA
        else:
            color = Colors.RED
        shape = Shapes.digitToHex(o)
        self.display.set(r,c, shape, color)

    def stepOn(self, row, col):
      #  print("Hello tile at: ({:d},{:d})".format(row,col))
        self.printPcnt(row, col, self.sensors[row][col])
        pass

    def stepOff(self, row, col):
      #  print("Goodbye tile at: ({:d},{:d})".format(row,col))
        self.display.clear(row, col)
        pass


def main():
    gameEngine = LSGameEngine(Calibrate, init=False)
    gameEngine.beginLoop()

if __name__ == "__main__":
    main()
