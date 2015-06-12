#!/usr/bin/env python3

import random

from lsapi.lsgame import *

class EightbitSoundboard():
    def __init__(self, display, audio, rows, cols):
        self.display = display
        self.audio = audio
        self.rows = rows
        self.cols = cols
        self.ended = False
        self.handlesEvents = True
        #self.audio.loadSong('8bit/8bit-loop.wav', 'between1')
        #self.audio.shuffleSongs()
        self.audio.setSongVolume(0)
        self.audio.loadSound('8bit/casio_C_4.wav', 'casioC4')
        self.board = None
        for i in range(0, rows):
            for j in range(0, cols):
                self.display.setShape(i,j,Shapes.digitToLetter(j))
                self.display.setColor(i, j, i + 1)
                print("{:d},{:d} set to 0x{:b}".format(i,j,Shapes.digitToLetter(j)))

    def heartbeat(self, sensorsChanged):
        for move in sensorsChanged:
            print("Tile:{:d},{:d} at {:d}".format(move.row, move.col, move.val))
            #self.playTileSound(move.row, move.col)
            #self.display.setColor(move.row, move.col, Colors.RANDOM())

    def stepOn(self, row, col):
        self.playTileSound(row, col)
        #self.audio.playLoadedSound('casioC4')
        self.display.setColor(row, col, Colors.RANDOM())

    def playTileSound(self, row, col):
        if row is 0:
            if col is 0:
                self.audio.playSound("8bit/casio_C_2.wav")
            if col is 1:
                self.audio.playSound("8bit/casio_C_3.wav")
            if col is 2:
                self.audio.playSound("8bit/casio_C_4.wav")
            if col is 3:
                self.audio.playSound("8bit/casio_C_5.wav")
            if col is 4:
                self.audio.playSound("8bit/casio_C_6.wav")
            if col is 5:
                self.audio.playSound("8bit/casio_C_3.wav")
                self.audio.playSound("8bit/casio_C_6.wav")
            if col is 6:
                self.audio.playSound("8bit/casio_C_2.wav")
                self.audio.playSound("8bit/casio_C_3.wav")
                self.audio.playSound("8bit/casio_C_4.wav")
                self.audio.playSound("8bit/casio_C_5.wav")
                self.audio.playSound("8bit/casio_C_6.wav")
        elif row is 1:
            if col is 0:
                self.audio.playSound("8bit/Reveal_G_2.wav")
            if col is 1:
                self.audio.playSound("8bit/Reveal_G_4.wav")
            if col is 2:
                self.audio.playSound("8bit/Reveal_G_4.wav")
            if col is 3:
                self.audio.playSound("8bit/04.wav")
            if col is 4:
                self.audio.playSound("8bit/08.wav")
            if col is 5:
                self.audio.playSound("8bit/8-bit-explosion1.wav")
            if col is 6:
                self.audio.playSound("8bit/8-bit-power-up.wav")
            if col is 7:
                print("Tile 2,8 is triggering too much")
                #self.audio.playSound("8bit/10.wav")
        elif row is 2:
            if col is 0:
                self.audio.playSound("8bit/12.wav")
            if col is 1:
                self.audio.playSound("8bit/13.wav")
            if col is 2:
                self.audio.playSound("8bit/15.wav")
            if col is 3:
                self.audio.playSound("8bit/16.wav")
            if col is 4:
                self.audio.playSound("8bit/23.wav")
            if col is 5:
                self.audio.playSound("8bit/34.wav")
            if col is 6:
                self.audio.playSound("8bit/38.wav")
            if col is 7:
                self.audio.playSound("8bit/46.wav")

    def ended(self):
        return self.ended

    if __name__ == "__main__":
        print("Test code goes here")
        
def main():
    gameEngine = LSGameEngine(EightbitSoundboard)
    gameEngine.beginLoop()

if __name__ == '__main__':
    main()
