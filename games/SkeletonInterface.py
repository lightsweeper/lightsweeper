#!/usr/bin/python3

from lightsweeper.lsapi import *

class HelloWorld(LSGame):
    def init(game):
        pass

    def heartbeat(game, activeSensors):
        pass

    def stepOn(game, row, col):
        pass

    def stepOff(game, row, col):
        pass

def main():
    gameEngine = LSGameEngine(HelloWorld) # Be sure to change this to reference your game
    gameEngine.beginLoop()

if __name__ == "__main__":
    main()
