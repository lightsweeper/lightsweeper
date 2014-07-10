#!/usr/bin/python3

import random

from PyQt5.QtWidgets import (QApplication, QDialog,QHBoxLayout)
from LSEmulateFloor import LSEmulateFloor
from minesweeper.board import Board, Cell

def create_board(width, height, mines):
    print("creating board")
    board = Board(tuple([tuple([Cell(False) for i in range(width)])
                         for j in range(height)]))
    available_pos = list(range((width-1) * (height-1)))
    print("creating mines")
    for i in range(mines):
        new_pos = random.choice(available_pos)
        available_pos.remove(new_pos)
        (row_id, col_id) = (new_pos % (height-1), new_pos // (height-1))
        board.place_mine(row_id, col_id)
    return board

def main():
    SIZE_W = 8
    SIZE_H = 6
    MINES = 9

    # Initialize board
    board = create_board(SIZE_W, SIZE_H, MINES)
    print("board created")

    app = QApplication(sys.argv)
    dialog = QDialog()
    mainLayout = QHBoxLayout()

    # make the Lightsweeper floor
    print("making lightsweeper floor")
    floor = LSEmulateFloor(6, 8, board)
    board.set_display(floor)
    floor.printboard(board)

    #todo: make these calls possible
    #floor = LSRealFloor(board)
    #board.set_display(floor)
    mainLayout.addWidget(floor)

    dialog.setContentsMargins(0,0,0,0)
    dialog.setLayout(mainLayout)
    dialog.setWindowTitle("Lightsweeper")
    dialog.setVisible(True)
    print("calling dialog.exec()")
    dialog.exec_()
    
    console = floor
    output = console
    output.printboard()
    
    print("exiting")
    sys.exit()

if __name__ == '__main__':
    import sys
    main()