#!/usr/bin/python3

import random

from PyQt5.QtWidgets import (QApplication, QDialog,QHBoxLayout)
from LSEmulateFloor import LSEmulateFloor

def main():
    app = QApplication(sys.argv)
    dialog = QDialog()
    mainLayout = QHBoxLayout()

    # make the Lightsweeper floor
    print("making lightsweeper floor")
    floor = LSEmulateFloor()

    #todo: make these calls possible
    #floor = LSRealFloor(board)
    #board.set_display(floor)
    mainLayout.addWidget(floor)

    dialog.setContentsMargins(0,0,0,0)
    dialog.setLayout(mainLayout)
    dialog.setWindowTitle("Lightsweeper")
    dialog.setVisible(True)
    console = floor
    output = console

    # Uncomment this to start with a blank board
    # console.printboard(board)

    print("calling dialog.exec()")
    dialog.exec_()
    print("exiting")
    sys.exit()

if __name__ == '__main__':
    import sys
    main()