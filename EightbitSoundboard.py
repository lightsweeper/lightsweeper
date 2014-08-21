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
        self.updateBoard(self.board)
        #self.audio.playSound('StartUp.wav')

    def heartbeat(self, sensorsChanged):
        for move in sensorsChanged:
            self.playTileSound(move.row, move.col)

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
    # currently this is just iterating across all the cells in the internal game state and pushing
    # the corresponding shape/color to the display for the given tile's position. a slightly better design would
    # be to only need to push info for the tiles that have actually changed

    def updateBoard(self, board):
        for row in range(0,self.rows):
            for col in range(0,self.cols):
                if board != None:
                    cell = board.getCellState(row, col)
                    if cell == "D":
                        self.display.set(row, col, Shapes.DASH, Colors.VIOLET)
                    elif cell == '.':
                        self.display.set(row, col, Shapes.ZERO, Colors.GREEN)
                    elif cell == ' ' or cell == '':
                        self.display.set(row, col, Shapes.DASH, Colors.BLACK)
                    elif cell == 'M':
                        self.display.set(row, col, Shapes.DASH, Colors.RED)
                    elif cell == 'F':
                        break
                    else:
                        self.display.set(row, col, Shapes.digitToHex(int(cell)), Colors.YELLOW)
        return

    def ended(self):
        return self.ended

    if __name__ == "__main__":
        print("Test code goes here")