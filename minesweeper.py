#!/usr/bin/python3

import random

from board import Board
import Colors
import Shapes
from Frame import Frame
import time

class Minesweeper():
    def __init__(self, display, audio, rows, cols):
        board = Board()
        mines = random.randint(int(cols*rows*.1), int(cols*rows*.3))
        print("{:d} mines...".format(mines))
        board.create_board(rows, cols, mines)
        self.board = board
        self.audio = audio
        self.display = display
        self.rows = rows
        self.cols = cols
        self.ended = False
        self.animatingEnd = False
        self.audio.loadSong('BetweenGames1.wav', 'between1')
        self.audio.loadSong('BetweenGames2.wav', 'between2')
        self.audio.loadSong('BetweenGames3.wav', 'between3')
        self.audio.loadSong('BetweenGames4.wav', 'between4')
        self.audio.shuffleSongs()
        #handles events is required to be defined
        self.handlesEvents = False
        self.audio.setSongVolume(0)
        self.songsQuiet = False
        self.firstStep = True
        self.updateBoard(self.board)

        # Confirmed that both sounsd play simultaneously
        # self.audio.playSound('StartUp.wav')
        # self.audio.playSound('Explosion.wav')

    def heartbeat(self, sensorsChanged):
        if self.board.is_playing:
            playSound = True
            for move in sensorsChanged:
                if self.songsQuiet:
                    self.songsQuiet = True
                if self.board.board[move.row][move.col].is_visible:
                    playSound = False
                if self.firstStep and self.board.board[move.row][move.col].is_mine:
                    self.board.board[move.row][move.col].is_mine = False
                    print("Saved from the mine!")
                self.firstStep = False
                self.board.show(move.row, move.col)
                if self.board.board[move.row][move.col].is_mine:
                    self.audio.playSound("Explosion.wav")
                elif playSound:
                    self.audio.playSound("Blop.wav")
            self.updateBoard(self.board)
        elif not self.board.is_playing and not self.animatingEnd:
            if self.board.is_solved():
                print("Well done! You solved the board!")
                self.endAnim = EndAnimation(True, self.rows, self.cols)
                self.animatingEnd = True
                self.audio.playSound("Success.wav")
            else:
                #self.audio.playSound("Explosion.wav")
                self.board.show_all()
                self.endAnim = EndAnimation(False, self.rows, self.cols)
                self.animatingEnd = True
        elif self.animatingEnd:
            frame = self.endAnim.getFrame()
            if frame:
                #update display of each tile
                self.display.setFrame(frame)
            if self.endAnim.ended:
                print("ended")
                self.ended = True
        #push changed tiles to display

    # currently this is just iterating across all the cells in the internal game state and pushing
    # the corresponding shape/color to the display for the given tile's position. a slightly better design would
    # be to only need to push info for the tiles that have actually changed
    def updateBoard(self, board):
        for row in range(0, self.rows):
            for col in range(0, self.cols):
                if board != None:
                    cell = board.getCellState(row, col)
                    if cell == "D":
                        self.display.set(row, col, Shapes.DASH, Colors.VIOLET)
                    elif cell == '.':
                        self.display.set(row, col, Shapes.ZERO, Colors.GREEN)
                    elif cell == ' ' or cell == '':
                        self.display.set(row, col, Shapes.DASH, Colors.BLACK)
                    elif cell == 'M':
                        self.display.set(row, col, Shapes.ZERO, Colors.RED)
                    elif cell == 'F':
                        break
                    else:
                        self.display.set(row, col, Shapes.digitToHex(int(cell)), Colors.YELLOW)
        return

    def ended(self):
        return self.ended

    if __name__ == "__main__":
        print("Test code goes here")

class EndAnimation:
    def __init__(self, win, rows, cols):
        self.rows = rows
        self.cols = cols
        self.ended = False
        self.currentFrame = None
        self.frames = []
        if win:
            frame = Frame(self.rows, self.cols)
            frame.setAllColor(Colors.CYAN)
            self.frames.append(frame)
            frame = Frame(self.rows, self.cols)
            frame.setAllColor(Colors.BLUE)
            self.frames.append(frame)
            frame = Frame(self.rows, self.cols)
            frame.setAllColor(Colors.GREEN)
            self.frames.append(frame)

            frame = Frame(self.rows, self.cols)
            frame.setAllColor(Colors.CYAN)
            self.frames.append(frame)
            frame = Frame(self.rows, self.cols)
            frame.setAllColor(Colors.BLUE)
            self.frames.append(frame)
            frame = Frame(self.rows, self.cols)
            frame.setAllColor(Colors.GREEN)
            self.frames.append(frame)
        else:
            frame = Frame(self.rows, self.cols)
            frame.setAllColor(Colors.RED)
            frame.setAllShape(Shapes.EIGHT)
            frame.heartbeats = 1
            self.frames.append(frame)

            frame = Frame(self.rows, self.cols)
            frame.setAllColor(Colors.BLACK)
            frame.setAllShape(Shapes.EIGHT)
            frame.heartbeats = 1
            self.frames.append(frame)

            frame = Frame(self.rows, self.cols)
            frame.setAllColor(Colors.RED)
            frame.setAllShape(Shapes.EIGHT)
            frame.heartbeats = 1
            self.frames.append(frame)

    def getFrame(self):
        if len(self.frames) is 0:
            self.ended = True
            return None
        if self.currentFrame and self.currentFrame.heartbeats > 0:
            self.currentFrame.heartbeats -= 1
        else:
            self.currentFrame = self.frames.pop()
        return self.currentFrame

def wait(seconds):
    # self.pollSensors()
    currentTime = time.time()
    while time.time() - currentTime < seconds:
        pass

def main():
    import LSGameEngine
    gameEngine = LSGameEngine.GameEngine(Minesweeper)
    gameEngine.beginLoop()

if __name__ == '__main__':
    main()
