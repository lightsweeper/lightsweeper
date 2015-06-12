#!/usr/bin/python3
import random
from lightsweeper.lsapi import *

instrument_1 = 19
instrument_2 = 20

class MidiSoundboard():
    def __init__(self, display, audio, rows, cols):
        self.display = display
        self.audio = audio
        self.rows = rows
        self.cols = cols
        self.ended = False
        self.handlesEvents = True
        self.audio.setSongVolume(0)
        self.handlesEvents = True
        #self.audio.midiSoundOn()
        self.board = None
        for i in range(0, rows):
            for j in range(0, cols):
                self.display.setShape(i,j,Shapes.digitToLetter(j))
                self.display.setColor(i, j, i + 1)
                print("{:d},{:d} set to 0x{:b}".format(i,j,Shapes.digitToLetter(j)))

    def heartbeat(self, sensorsChanged):
        for (row, col) in sensorsChanged:
            print("Tile:{:d},{:d} at {:d}".format(row, col))
            #self.playTileSound(move.row, move.col)
            #self.display.setColor(move.row, move.col, Colors.RANDOM())

    def stepOn(self, row, col):
        self.playTileSound(row, col)
        self.display.setColor(row, col, Colors.RANDOM())

    def playTileSound(self, row, col):
        if row is 0:
            if col is 0:
                self.audio.midiSoundOn(instrument=19, note=70)
                print("playing 0,0")
            if col is 1:
                self.audio.midiSoundOn(instrument=19, note=71)
            if col is 2:
                self.audio.midiSoundOn(instrument=19, note=72)
            if col is 3:
                self.audio.midiSoundOn(instrument=19, note=73)
            if col is 4:
                self.audio.midiSoundOn(instrument=19, note=74)
            if col is 5:
                self.audio.midiSoundOn(instrument=19, note=75)
            if col is 6:
                self.audio.midiSoundOn(instrument=19, note=76)
        elif row is 1:
            if col is 0:
                self.audio.midiSoundOn(instrument=instrument_2, note=70)
            if col is 1:
                self.audio.midiSoundOn(instrument=instrument_2, note=71)
            if col is 2:
                self.audio.midiSoundOn(instrument=instrument_2, note=72)
            if col is 3:
                self.audio.midiSoundOn(instrument=instrument_2, note=73)
            if col is 4:
                self.audio.midiSoundOn(instrument=instrument_2, note=74)
            if col is 5:
                self.audio.midiSoundOn(instrument=instrument_2, note=75)
            if col is 6:
                self.audio.midiSoundOn(instrument=instrument_2, note=76)
            if col is 7:
                self.audio.midiSoundOn(instrument=instrument_2, note=77)
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
    gameEngine = LSGameEngine(MidiSoundboard)
    gameEngine.beginLoop()

if __name__ == '__main__':
    main()
