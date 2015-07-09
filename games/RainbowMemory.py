#!/usr/bin/python3

'''
idea by Nate Anderson:
All of the segments would start cycling random colors once or twice a second. 
One digit would briefly switch to a solid color 1 with accompanying sound effect before returning to random cycling 
The user would select it and a confirmation action would occur with a sound effect.
Step 2 would repeat and an additional digit would be added to the sequence(a 2 displayed in a different color than the first)
Rinse and repeat until a user select the incorrect digit(not sure if it should go on indefinitely or if there should be a limit)
The entire board displays a failure animation with sound effects
'''

from lightsweeper.lsapi import *
import random

DISPLAY_DIGIT_FOR = 25
DISPLAY_DIGIT_EVERY = 65
class RainbowMemory(LSGame):
    def init(self):
        self.frameRate = 15
        self.frame = 0
        self.displayingDigit = False
        self.currDigit = 1
        self.currentColors = [Colors.RED, Colors.YELLOW, Colors.GREEN, Colors.CYAN, Colors.BLUE, Colors.MAGENTA]
        self.tile = (random.randint(0,self.display.rows-1), random.randint(0,self.display.cols-1))
        self.steppedOnDigit = False
        self.audio.playSound('8bit/8bit-loop.wav')

    def heartbeat(self, sensorsChanged):
        self.frame += 1
        if not self.displayingDigit:
            self.display.setAllCustom(self.currentColors + [Colors.BLACK])
            color = self.currentColors.pop()
            self.currentColors.insert(0, color)
        if self.frame > DISPLAY_DIGIT_EVERY:
            self.display.setAll(Shapes.DASH, Colors.WHITE)
            self.frame = 0
            self.displayingDigit = True
            self.audio.stopSounds()
            self.audio.playSound('tick_tock.wav')
            self.display.setAll(Shapes.UNDERSCORE, Colors.WHITE)
            self.tile = (random.randint(0,self.display.rows-1), random.randint(0,self.display.cols-1))
            self.display.set(self.tile[0],self.tile[1],Shapes.digitToHex(self.currDigit), (self.currDigit % 6) + 1)
        elif self.displayingDigit and self.frame > DISPLAY_DIGIT_FOR:
            self.frame = 0
            self.displayingDigit = False
            self.audio.stopSounds()
            self.audio.playSound('8bit/8bit-loop.wav')
            
            if self.currDigit > 9:
                self.audio.stopSounds()
                self.ended = True
                self.audio.playSound('8bit/42.wav')
        if self.steppedOnDigit:
            self.currDigit += 1
            self.steppedOnDigit = False

    def stepOn(game, row, col):
        self.audio.stopSounds()
        if not game.displayingDigit:
            if (row,col) == game.tile:
                game.steppedOnDigit = True
                self.audio.playSound('8bit/42.wav')
                print('Yay! You stepped on it')
            else:
                self.audio.playSound('8bit/16.wav')
                print('Nope')

    def stepOff(game, row, col):
        pass

def main():
    gameEngine = LSGameEngine(RainbowMemory)
    gameEngine.beginLoop()

if __name__ == "__main__":
    main()
