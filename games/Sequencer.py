# the layout of the 8 x n sequencer floor:
# 0    0    0    0    0    0    0    0 (first 8 note set)
# 0    0    0    0    0    0    0    0 (second 8 note set)
# sound type selection

import time

from lsapi import *

PREFIX = 'drums/'
class Sequencer():
    def __init__(self, display, audio, rows, cols):
        self.display = display
        self.display.setAll(Shapes.ZERO, Colors.BLUE)
        self.audio = audio
        self.rows = rows
        self.cols = cols
        self.ended = False
        self.handlesEvents = True
        self.audio.setSongVolume(0.1)
        self.board = None
        #which sounds will play on what tile / beat. Each beat is represented as a set
        #containing the index to the file for every sound that should be played
        self.beats = [[set(),set(),set(),set(),set(),set(),set(),set()],
                      [set(),set(),set(),set(),set(),set(),set(),set()]]
        self.files = ['hat_2.wav',  'kick.wav', 'perc_1.wav', 'ride_bell.wav', 'rimshot.wav', 'tom.wav', '02.wav', '04.wav']
        #which type of sound the player has currently selected
        self.selector = 0
        self.display.set(2, 0, Shapes.ZERO, Colors.RED)
        #where the current beat is
        self.beatRow = 0
        self.beatCol = 0
        self.clock = -1
        self.msPerBeat = 80

        for col in range(len(self.beats[0])):
            self.display.set(2, col, Shapes.DASH, Colors.GREEN)

    def heartbeat(self, sensorsChanged):
        #print('heartbeat', self.clock, time.time())
        if self.clock == -1:
            self.clock = time.time()
        if time.time() - self.clock > self.msPerBeat / 1000:

            self.incrementCurrentTile()

            if self.beats[self.beatRow][self.beatCol]:
                print(str(self.beatRow), str(self.beatCol), "playing", self.beats[self.beatRow][self.beatCol], "took", str(self.clock))
                for sound in self.beats[self.beatRow][self.beatCol]:
                    self.audio.playSound(PREFIX + self.files[sound])
                    if sound != self.selector:
                        self.display.set(2, sound, Shapes.DASH, Colors.MAGENTA)
            self.clock = time.time()

    def stepOn(self, row, col):
        if row < 2:
            if self.selector in self.beats[row][col]:
                self.beats[row][col].discard(self.selector)
            else:
                #add sound to this beat
                self.beats[row][col].add(self.selector)
                self.display.set(row, col, Shapes.ZERO, Colors.YELLOW)
        else:
            #select a new sound
            self.display.set(row, self.selector, Shapes.DASH, Colors.GREEN)
            self.selector = col
            self.display.set(row, col, Shapes.DASH, Colors.RED)
            #show all beats where this sound will be played
            for r in range(len(self.beats)):
                for c in range(len(self.beats[0])):
                    if self.selector in self.beats[r][c]:
                        self.display.set(r, c, Shapes.ZERO, Colors.YELLOW)
                    else:
                        self.display.set(r, c, Shapes.ZERO, Colors.BLUE)

    def incrementCurrentTile(self):
        if self.selector in self.beats[self.beatRow][self.beatCol]:
            self.display.setColor(self.beatRow, self.beatCol, Colors.YELLOW)
        else:
            self.display.setColor(self.beatRow, self.beatCol, Colors.BLUE)
        self.beatCol += 1
        if self.beatCol > 7:
            self.beatCol = 0
            self.beatRow += 1
        if self.beatRow > 1:
            self.beatRow = 0
        self.display.setColor(self.beatRow, self.beatCol, Colors.WHITE)
        #reset colors of the sound selection row
        for c in range(len(self.beats[0])):
            if c != self.selector:
                self.display.set(2, c, Shapes.DASH, Colors.GREEN)
            else:
                self.display.set(2, c, Shapes.DASH, Colors.RED)

def main():
    gameEngine = LSGameEngine(Sequencer)
    gameEngine.beginLoop()

if __name__ == '__main__':
    main()
