#!/usr/bin/env python3

from lsgame import *

import lsanimate
import lsexplosion

from collections import defaultdict
import random
import time
import pygame # pygame.event

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

    def list_mines(self):
        r = 0
        c = 0
        out = []
        for row in self.board:
            for cell in row:
                if cell.is_mine is True:
                    rowCol = (r, c)
                    out.append(rowCol)
                c += 1
            r += 1
            c = 0
        return out
                    


class Minesweeper(LSGame):

    staleDisplay = defaultdict(lambda: defaultdict(str))

    def init(self):
        board = Board()
        mines = random.randint(int(self.cols*self.rows*.1), int(self.cols*self.rows*.3))
        if mines is 0:
            mines = 1
        print("{:d} mines...".format(mines))
        board.create_board(self.rows, self.cols, mines)
        self.board = board
        self.animatingEnd = False
        self.audio.loadSong('BetweenGames1.wav', 'between1')
        self.audio.loadSong('BetweenGames2.wav', 'between2')
        self.audio.loadSong('BetweenGames3.wav', 'between3')
        self.audio.loadSong('BetweenGames4.wav', 'between4')
        self.audio.shuffleSongs()
        self.audio.setSongVolume(0)
        self.firstStep = True
        self.updateBoard(self.board)
        self.display.setAll(Shapes.ZERO, Colors.GREEN)


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
        self.lastMove = (row, col)
        if self.board.board[row][col].is_mine:
            self.display.set(row, col, Shapes.ZERO, Colors.RED)
            self.audio.playSound("Explosion.wav")
        elif playSound:
            self.audio.playSound("Blop.wav")
            cell = self.board.getCellState(row, col)
            if cell != " ":
                self.display.set(row, col, Shapes.digitToHex(int(cell)), Colors.YELLOW)

    def heartbeat(self, sensorsChanged):
        if self.board.is_playing:
            self.updateBoard(self.board)
        if not self.board.is_playing and not self.animatingEnd:
            if self.board.is_solved():
                print("Well done! You solved the board!")
                self.endAnim = EndAnimation(True, self.display, self.lastMove, self.board.list_mines())
                self.animatingEnd = True
                self.audio.playSound("Success.wav")
            else:
                #self.audio.playSound("Explosion.wav")
                self.board.show_all()
                self.endAnim = EndAnimation(False, self.display, self.lastMove, self.board.list_mines())
                self.animatingEnd = True
        elif self.animatingEnd:
            frame = self.endAnim.getFrame()
            if frame:
                #update display of each tile
                self.display.setFrame(frame)
            if self.endAnim.ended:
                self.endAnim.animation.play(self.display)
                self.gameOver()


    # currently this is just iterating across all the cells in the internal game state and pushing
    # the corresponding shape/color to the display for the given tile's position. a slightly better design would
    # be to only need to push info for the tiles that have actually changed
    def updateBoard(self, board):
        for row in range(0, self.rows):
            for col in range(0, self.cols):
                if board != None:
                    cell = board.getCellState(row, col)
                    staleCell = self.staleDisplay[row][col]
                    if cell == "D":
                        if staleCell != "D":
                            self.display.set(row, col, Shapes.DASH, Colors.MAGENTA)
                    elif cell == '.':
                        if staleCell != ".":
                            self.display.set(row, col, Shapes.ZERO, Colors.GREEN)
                    elif cell == ' ' or cell == '':
                        if staleCell != " " and staleCell != "":
                            self.display.set(row, col, Shapes.DASH, Colors.BLACK)
                    elif cell == 'M':
                        if staleCell != "M":
                            self.display.set(row, col, Shapes.ZERO, Colors.RED)
                    elif cell == 'F':
                        print("A flag?!")
                        break
                    else:
                        cell = int(cell)
                        if cell is 1:
                            color = Colors.YELLOW
                        elif cell is 2:
                            color = Colors.WHITE
                        elif cell is 3:
                            color = Colors.CYAN
                        elif cell is 4:
                            color = Colors.BLUE
                        else:
                            color = Colors.MAGENTA
                        self.display.set(row, col, Shapes.digitToHex(cell), color) # Should use setDigit?
                self.staleDisplay[row][col] = cell
        return


class EndAnimation:
    def __init__(self, win, display, lastMove, mines):
        self.rows = display.rows
        self.cols = display.cols
        print(self.rows)
        print(self.cols)
        self.ended = False
        self.currentFrame = None
        self.frames = []
        frame = display
        if win:
            redDash = (1, 0, 0)
            greenDash = (0, 1, 0)
            blueDash = (0, 0, 1)
            dashes = [redDash, greenDash, blueDash]
            redMine = (Shapes.H, 0, 0)
            greenMine = (0, Shapes.H, 0)
            blueMine = (0, 0, Shapes.H)

            winningAnimation = lsanimate.LSAnimation()

            frame = lsanimate.LSFrameGen(self.rows,self.cols)
            
            for _ in range(0,15):
                for i in range(0,self.cols):
                    #frame.edit(0,i,redDash)
                    #frame.edit(1,i,greenDash)
                    #frame.edit(2,i,blueDash)
                    for row in range(0,self.rows):
                        idx = (0+row) % 3
                        frame.edit(row,i,dashes[idx])
                for mine in mines:
                    frame.edit(mine[0],mine[1],redMine)
                winningAnimation.addFrame(frame.get())

                for i in range(0,self.cols):
                    #frame.edit(1,i,redDash)
                    #frame.edit(2,i,greenDash)
                    #frame.edit(0,i,blueDash)
                    for row in range(0,self.rows):
                        idx = (1+row) % 3
                        frame.edit(row,i,dashes[idx])
                for mine in mines:
                    frame.edit(mine[0],mine[1],greenMine)
                winningAnimation.addFrame(frame.get())

                for i in range(0,self.cols):
                    #frame.edit(2,i,redDash)
                    #frame.edit(1,i,greenDash)
                    #frame.edit(0,i,blueDash)
                    for row in range(0,self.rows):
                        idx = (2+row) % 3
                        frame.edit(row,i,dashes[idx])
                for mine in mines:
                    frame.edit(mine[0],mine[1],blueMine)
                winningAnimation.addFrame(frame.get())

                self.animation = winningAnimation

        else:

            losingAnimation = lsanimate.LSAnimation()

            frame = lsexplosion.LSExplosion(self.rows, self.cols, lastMove, mines)
            
            for frameNum in range(0,50):
                frame.flamefront()
                losingAnimation.addFrame(frame.get())

            losingAnimation.deleteFrame(7) # Because I'm too lazy to do it right
            losingAnimation.deleteFrame(7) # Yes, we need both of these

            self.animation = losingAnimation

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
