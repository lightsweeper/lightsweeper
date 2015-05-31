#!/usr/bin/env python3

from lsgame import LSGameEngine
from lsgame import Frame

import Colors
import Shapes

import random
import time

wait=time.sleep

class Cell(object):
    def __init__(self, is_mine, is_visible=False, is_flagged=False):
        self.is_mine = is_mine
        self.is_visible = is_visible
        self.is_flagged = is_flagged
        self.is_defused = False

    def show(self):
        self.is_visible = True

    def flag(self):
        self.is_flagged = not self.is_flagged

    def place_mine(self):
        self.is_mine = True

    def set_defused(self):
        if self.is_mine:
            self.is_defused = True


class Board():

    def __init__(self):
        super().__init__()
        self.is_playing = True

    def create_board(self, rows, cols, mines):
        print("creating board")
        self.board = tuple([tuple([Cell(False) for col in range(cols)])
                            for row in range(rows)])
        available_pos = list(range((rows) * (cols)))
        print("creating mines")
        for i in range(mines):
            new_pos = random.choice(available_pos)
            available_pos.remove(new_pos)
            (row_id, col_id) = random.randint(0, rows-1), random.randint(0, cols-1) #(new_pos // (cols), new_pos % (rows))
            self.place_mine(row_id, col_id)
        self.is_playing = True
        return

    def getCellState(self,row_id, col_id):
        # print ("min_repr for: ",row_id,col_id)
        cell = self.board[row_id][col_id]
        if cell.is_defused:
            return "D"
        elif cell.is_visible:
            if cell.is_mine:
                return "M"
            else:
                surr = self.count_surrounding(row_id, col_id)
                return str(surr) if surr else " "
        elif cell.is_flagged:
            return "F"
        else:
            return "."  #u"\uff18"

    def set_display(self, display):
        print("setting display")
        self.display = display
    
    def show(self, row_id, col_id):
        self.showingMultiple = False
        #print("given:", row_id, col_id, "board:", len(self.board), len(self.board[0]))
        cell = self.board[row_id][col_id]
        if not cell.is_visible:
            #print("board.show", row_id, col_id)
            cell.show()
            # self.display.show(row_id, col_id)
            if (cell.is_mine and not cell.is_flagged):
                self.is_playing = False
                print("mine'd!")
            elif self.is_solved():
                self.is_playing = False
            elif self.count_surrounding(row_id, col_id) == 0:
                self.showingMultiple = True
                for (surr_row, surr_col) in self.get_neighbours(row_id, col_id):
                    if self.is_in_range(surr_row, surr_col):
                        self.show(surr_row, surr_col) 

    def show_all(self):
        for row in self.board:
            for cell in row:
                cell.show()               
        
    def flag(self, row_id, col_id):
        cell = self.board[row_id][col_id]
        if not cell.is_visible:
            cell.flag()
        else:
            print("Cannot add flag, cell already visible.")

    def place_mine(self, row_id, col_id):
        self.board[row_id][col_id].place_mine()

    def count_surrounding(self, row_id, col_id):
        return sum(1 for (surr_row, surr_col) in self.get_neighbours(row_id, col_id)
                        if (self.is_in_range(surr_row, surr_col) and
                            self.board[surr_row][surr_col].is_mine))

    def get_neighbours(self, row_id, col_id):
        SURROUNDING = ((-1, -1), (-1,  0), (-1,  1),
                       (0 , -1),           (0 ,  1),
                       (1 , -1), (1 ,  0), (1 ,  1))
        return ((row_id + surr_row, col_id + surr_col) for (surr_row, surr_col) in SURROUNDING)

    def is_in_range(self, row_id, col_id):
        return 0 <= row_id < len(self.board) and 0 <= col_id < len(self.board[0])

    def remaining_mines(self):
        remaining = 0
        for row in self.board:
            for cell in row:
                if cell.is_mine and not cell.is_visible:
                    remaining += 1
                if cell.is_flagged:
                    remaining -= 1
        return remaining
    
    def remaining_hidden(self):
        remaining = 0
        for row in self.board:
            for cell in row:
                if not cell.is_visible:
                    remaining += 1
        return remaining

    def set_all_defused(self):
        for row in self.board:
            for cell in row:
                cell.set_defused()
        self.is_playing = False

    def is_solved(self):
        #return all((cell.is_visible or cell.is_flagged) for row in self.board for cell in row)
        #print("Remaining Mines: ", self.remaining_mines(), " Remaining Hidden: ", self.remaining_hidden())
        return self.remaining_mines() == self.remaining_hidden()


class Minesweeper():
    def __init__(self, display, audio, rows, cols):
        board = Board()
        mines = random.randint(int(cols*rows*.1), int(cols*rows*.3))
        if mines is 0:
            mines = 1
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
        self.audio.setSongVolume(0)
        self.firstStep = True
        self.updateBoard(self.board)

    def stepOn(self, row, col):
        playSound = True
        if self.board.board[row][col].is_visible:
            playSound = False
        if self.firstStep:
            if self.board.board[row][col].is_mine:
                self.board.board[row][col].is_mine = False  # TODO: Should replace the mine somewhere else
                print("Saved from the mine!")
            self.firstStep = False
        self.board.show(row, col)
        if self.board.board[row][col].is_mine:
            self.audio.playSound("Explosion.wav")
        elif playSound:
            self.audio.playSound("Blop.wav")
        self.lastMove = (row, col)

    def heartbeat(self, sensorsChanged):
        if self.board.is_playing:
            self.updateBoard(self.board)
        elif not self.board.is_playing and not self.animatingEnd:
            if self.board.is_solved():
                print("Well done! You solved the board!")
                self.endAnim = EndAnimation(True, self.rows, self.cols, self.lastMove)
                self.animatingEnd = True
                self.audio.playSound("Success.wav")
            else:
                #self.audio.playSound("Explosion.wav")
                self.board.show_all()
                self.endAnim = EndAnimation(False, self.rows, self.cols, self.lastMove)
                self.animatingEnd = True
        elif self.animatingEnd:
            frame = self.endAnim.getFrame()
            if frame:
                #update display of each tile
                self.display.setFrame(frame)
            if self.endAnim.ended:
                print("ended")
                self.ended = True

    # currently this is just iterating across all the cells in the internal game state and pushing
    # the corresponding shape/color to the display for the given tile's position. a slightly better design would
    # be to only need to push info for the tiles that have actually changed
    def updateBoard(self, board):
        for row in range(0, self.rows):
            for col in range(0, self.cols):
                if board != None:
                    cell = board.getCellState(row, col)
                    try:
                        staleCell = self.staleBoard.getCellState(row, col)
                    except AttributeError:
                        staleCell = "Q" # Just different
                    if cell == "D" and staleCell != "D":
                        self.display.set(row, col, Shapes.DASH, Colors.MAGENTA)
                    elif cell == '.' and staleCell != ".":
                        self.display.set(row, col, Shapes.ZERO, Colors.GREEN)
                    elif cell == ' ' or cell == '':
                        self.display.set(row, col, Shapes.DASH, Colors.BLACK)
                    elif cell == 'M' and staleCell != "M":
                        self.display.set(row, col, Shapes.ZERO, Colors.RED)
                    elif cell == 'F':
                        print("A flag?!")
                        break
                    else:
                        cell = int(cell):
                        if int(staleCell) != cell:
                            if cell is 1:
                                color = Colors.WHITE
                            elif cell is 2:
                                color = Colors.BLUE
                            elif cell is 3:
                                color = Colors.CYAN
                            elif cell is 4:
                                color = Colors.YELLOW
                            else:
                                color = Colors.PINK
                            self.display.set(row, col, Shapes.digitToHex(cell), color) # Should use setDigit?
        self.staleBoard = board
        return

    def ended(self):
        return self.ended

class EndAnimation:
    def __init__(self, win, rows, cols, lastMove):
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

def main():
    gameEngine = LSGameEngine(Minesweeper)
    gameEngine.beginLoop()

if __name__ == '__main__':
    main()
