#!/usr/bin/python3

import random

from minesweeper.board import Board
import Colors
import Shapes
from Frame import Frame

class Minesweeper():
    def __init__(self, display, audio, rows, cols):
        board = Board()
        mines = random.randint(2, cols)
        board.create_board(rows, cols, mines)
        self.board = board
        self.audio = audio
        self.display = display
        self.rows = rows
        self.cols = cols
        self.ended = False
        self.animatingEnd = False
        self.audio.loadSong('sounds/BetweenGames1.wav', 'between1')
        self.audio.loadSong('sounds/BetweenGames2.wav', 'between2')
        self.audio.loadSong('sounds/BetweenGames3.wav', 'between3')
        self.audio.loadSong('sounds/BetweenGames4.wav', 'between4')
        self.audio.shuffleSongs()
        self.updateBoard(self.board)

    def heartbeat(self, sensorsChanged):
        if self.board.is_playing:
            for move in sensorsChanged:
                print("got move at", move.row, move.col, "value:", move.val)
                self.board.show(move.row, move.col)
            self.updateBoard(self.board)
        elif not self.board.is_playing and not self.animatingEnd:
            if self.board.is_solved():
                print("Well done! You solved the board!")
                self.endAnim = EndAnimation(True)
                self.animatingEnd = True
            else:
                print("Uh oh! You blew up!")
                self.board.show_all()
                self.endAnim = EndAnimation(False)
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

class EndAnimation:
    def __init__(self, win):
        self.ended = False
        self.currentFrame = None
        self.frames = []
        if win:
            frame = Frame(3, 3)
            frame.setAllColor(Colors.CYAN)
            self.frames.append(frame)
            frame = Frame(3, 3)
            frame.setAllColor(Colors.BLUE)
            self.frames.append(frame)
            frame = Frame(3, 3)
            frame.setAllColor(Colors.GREEN)
            self.frames.append(frame)
        else:
            frame = Frame(3, 3)
            frame.setAllColor(Colors.RED)
            frame.setAllShape(Shapes.EIGHT)
            frame.heartbeats = 30
            self.frames.append(frame)

            frame = Frame(3, 3)
            frame.setAllColor(Colors.BLACK)
            frame.setAllShape(Shapes.EIGHT)
            frame.heartbeats = 10
            self.frames.append(frame)

            frame = Frame(3, 3)
            frame.setAllColor(Colors.RED)
            frame.setAllShape(Shapes.EIGHT)
            frame.heartbeats = 10
            self.frames.append(frame)

            frame = Frame(3, 3)
            frame.setAllColor(Colors.BLACK)
            frame.setAllShape(Shapes.EIGHT)
            frame.heartbeats = 10
            self.frames.append(frame)

            frame = Frame(3, 3)
            frame.setAllColor(Colors.RED)
            frame.setAllShape(Shapes.EIGHT)
            frame.heartbeats = 10
            self.frames.append(frame)

            frame = Frame(3, 3)
            frame.setAllColor(Colors.BLACK)
            frame.setAllShape(Shapes.EIGHT)
            frame.heartbeats = 10
            self.frames.append(frame)

            frame = Frame(3, 3)
            frame.setAllColor(Colors.RED)
            frame.setAllShape(Shapes.EIGHT)
            frame.heartbeats = 10
            self.frames.append(frame)

            frame = Frame(3, 3)
            frame.setAllColor(Colors.BLACK)
            frame.setAllShape(Shapes.EIGHT)
            frame.heartbeats = 10
            self.frames.append(frame)

            frame = Frame(3, 3)
            frame.setAllColor(Colors.RED)
            frame.setAllShape(Shapes.EIGHT)
            frame.heartbeats = 10
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