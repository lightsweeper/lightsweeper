#!/usr/bin/python3

import random

from lightsweeper.lsapi import *
from lightsweeper import lsgame


def main():
    gameEngine = LSGameEngine(lsgame.SAVERS[0], init = False)
    gameEngine.beginLoop()

if __name__ == "__main__":
    main()
