#!/usr/bin/python3

import random

from PyQt5.QtWidgets import (QApplication, QDialog,QHBoxLayout)
from LSEmulateFloor import LSEmulateFloor
from LSRealFloor import LSRealFloor

def main():
    emulator = False
    print("starting")
    #todo: remove all references to PyQt so we can compile
    #this on a Pi without Qt
    if emulator:
        app = QApplication(sys.argv)
        dialog = QDialog()
        mainLayout = QHBoxLayout()
        dialog.setContentsMargins(0,0,0,0)
        dialog.setLayout(mainLayout)
        dialog.setWindowTitle("Lightsweeper")
        dialog.setVisible(True)
        floor = LSEmulateFloor()
        mainLayout.addWidget(floor)

        console = floor
        output = console

        # Uncomment this to start with a blank board
        # console.printboard(board)

        dialog.exec_()
        sys.exit()
    else:
        print("creating LSRealFloor")
        floor = LSRealFloor()


if __name__ == '__main__':
    import sys
    main()
