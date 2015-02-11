#!/usr/bin/python3
import Colors
import Shapes

class Soundboard():
    def __init__(self, display, audio, rows, cols):
        self.display = display
        self.audio = audio
        self.rows = rows
        self.cols = cols
        self.ended = False
        self.audio.loadSong('8bit/8bit-loop.wav', 'between1')
        self.audio.shuffleSongs()
        self.audio.setSongVolume(0)
        self.board = None
        #we want the tile to change back to the untouched color after some number of heartbeats
        self.moveColorChange = []
        self.moveColorChangeTimer = []
        #self.audio.playSound('StartUp.wav')

    def heartbeat(self, sensorsChanged):
        removeItems = []
        for i in range(len(self.moveColorChangeTimer)):
            if self.moveColorChangeTimer[i] < 10:
                self.moveColorChangeTimer[i] += 1
            else:
                move = self.moveColorChange[i]
                self.display.setColor(move.row, move.col, Colors.WHITE)
                removeItems.push(i)
        for i in removeItems:
            self.moveColorChange.remove(self.moveColorChange[i])
            self.moveColorChangeTimer.remove(self.moveColorChangeTimer[i])
        for move in sensorsChanged:
            self.playTileSound(move.row, move.col)
            self.moveColorChangeTimer.append(0)
            self.moveColorChange.append(move)
            self.display.setColor(move.row, move.col, Colors.RANDOM)

    def playTileSound(self, row, col):
        if row is 0:
            print("swap looping tracks")
        if row is 1:
            print("swap assist looping tracks")
        if row is 2:
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
                self.audio.playSound("8bit/casio_C_7.wav")
            if col is 6:
                self.audio.playSound("8bit/casio_C_2.wav")
                self.audio.playSound("8bit/casio_C_3.wav")
                self.audio.playSound("8bit/casio_C_4.wav")
                self.audio.playSound("8bit/casio_C_5.wav")
                self.audio.playSound("8bit/casio_C_6.wav")
                self.audio.playSound("8bit/casio_C_7.wav")
        elif row is 3:
            if col is 0:
                self.audio.playSound("8bit/Reveal_G_2.wav")
            if col is 1:
                self.audio.playSound("8bit/Reveal_G_4.wav")
            if col is 2:
                self.audio.playSound("8bit/Reveal_G_5.wav")
            if col is 3:
                self.audio.playSound("8bit/04.wav")
            if col is 4:
                self.audio.playSound("8bit/08.wav")
            if col is 5:
                self.audio.playSound("8bit/8-bit-explosion1.wav")
            if col is 6:
                self.audio.playSound("8bit/8-bit-power-up.wav")
            if col is 7:
                self.audio.playSound("8bit/10.wav")
        elif row is 3:
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