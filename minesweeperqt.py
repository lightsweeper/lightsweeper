#!/usr/bin/python3

from PyQt5.QtWidgets import (QApplication, QDialog,QHBoxLayout)
from LSEmulateFloor import LSEmulateFloor

def main():
    emulator = False
    print("starting")
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


if __name__ == '__main__':
    import sys
    main()
