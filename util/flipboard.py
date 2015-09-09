#!/usr/bin/python3

import random
from copy import copy

from lightsweeper.lsapi import *

class Flipboard(LSGame):

    def init(self):
        pass

    def heartbeat(self, activeTiles):

        for row in range(self.rows):
            for col in range(self.cols):
                self.display.set(row, col, Shapes.UNDERSCORE, Colors.WHITE)

    def stepOn(self, row, col):
        tile = self.display.floor.views[0].tiles[row][col]
        tile.flip()
        pass


def main():
    gameEngine = LSGameEngine(Flipboard, init=False)
    gameEngine.beginLoop()

if __name__ == "__main__":
    main()
