#!/usr/bin/python3

from lightsweeper.lsapi import *

class HelloWorld(LSGame):
    def init(game):
        for thisRow in range(frame.rows):
            for i in range(4):  # It takes 4 frames to move the line from the
                                # top of the figure 8 to the bottom and then
                                # reset the row
                for thisCol in range(frame.cols):
                    # We just re-use the same LSFrameGen object, making incremental
                    # changes to it and adding the modified frames to our animation
                    if i is 0:
                        frame.edit(thisRow, thisCol, topLine)
                    elif i is 1:
                        frame.edit(thisRow, thisCol, midLine)
                    elif i is 2:
                        frame.edit(thisRow, thisCol, bottomLine)
                    else:
                        frame.edit(thisRow, thisCol, pinkEight)

                # Filter out frames that are all pink:
                if not all(i in pinkEight for i in frame.get()[1:]):
                    ourAnimation.addFrame(frame.get())  # Add the constructed frame


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
