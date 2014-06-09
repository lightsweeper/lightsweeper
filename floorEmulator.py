#!/usr/bin/env python


#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################


from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog,
        QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
        QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit,
        QVBoxLayout)

# Lightsweeper additions
from PyQt5.QtWidgets import (QLCDNumber, QWidget, QFrame, QSpinBox, QStyle, QStyleOption, QToolButton)
from PyQt5.QtGui import (QPainter)

class Dialog(QDialog):
    NumRows = 3
    NumCols = 5

    def __init__(self):
        super(Dialog, self).__init__()

        mainLayout = QHBoxLayout()
        self.createMenu()
        mainLayout.setMenuBar(self.menuBar)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        mainLayout.addWidget(buttonBox)

        # make the API controls
        self.makeTestGroupBox()
        mainLayout.addWidget(self.testGroupBox)

        # make the Lightsweeper floor
        self.floor = LSEmulateFloor(self.NumRows, self.NumCols)
        mainLayout.addWidget(self.floor)

        #mainLayout.addWidget(bigEditor)

        self.setContentsMargins(0,0,0,0)
        self.setLayout(mainLayout)
        self.setWindowTitle("Lightsweeper API Demonstrator")

    def createMenu(self):
        self.menuBar = QMenuBar()
        self.fileMenu = QMenu("&File", self)
        self.exitAction = self.fileMenu.addAction("E&xit")
        self.menuBar.addMenu(self.fileMenu)
        self.exitAction.triggered.connect(self.accept)

    def makeTestGroupBox(self):
        self.testGroupBox= QGroupBox("test controls")
        layout = QVBoxLayout()
        self.makeTileSelect()
        layout.addWidget(self.tileSelectBox)
        self.makeColorBox()
        layout.addWidget(self.colorBox)
        self.makeDigitBox()
        layout.addWidget(self.digitBox)
        self.makeFlushBox()
        layout.addWidget(self.flushBox)
        self.testGroupBox.setLayout(layout)

    def makeTileSelect(self):
        self.tileSelectBox = QGroupBox("Tile Selection")
        layout = QVBoxLayout()
        self.rowSelect = QSpinBox()
        self.rowSelect.setPrefix("Row ")
        self.rowSelect.setRange(0, self.NumRows)
        self.rowSelect.setSpecialValueText("Whole column");
        layout.addWidget(self.rowSelect)
        #rowLbl = QLabel("Row")
        #layout.addWidget(rowLbl)
        self.colSelect = QSpinBox()
        self.colSelect.setPrefix("Column ")
        self.colSelect.setRange(0, self.NumCols)
        self.colSelect.setSpecialValueText("Whole row");
        layout.addWidget(self.colSelect)
        #colLbl = QLabel("Column")
        #layout.addWidget(colLbl)
        self.tileSelectBox.setLayout(layout)

    def makeColorBox(self):
        self.colorBox = QGroupBox("Color Selection")
        layout = QVBoxLayout()
        self.colorSelect = QComboBox()
        self.colorSelect.addItem("red", "red")
        self.colorSelect.addItem("orange", "orange")
        self.colorSelect.addItem("yellow", "yellow")
        self.colorSelect.addItem("green", "green")
        self.colorSelect.addItem("blue", "blue")
        self.colorSelect.addItem("violet", "violet")
        self.colorSelect.addItem("white", "white")
        self.colorSelect.addItem("black", "black")
        layout.addWidget(self.colorSelect)
        # button to immediately set this color
        colorButton = QPushButton("Set this color")
        colorButton.clicked.connect(self.setColor)
        layout.addWidget(colorButton)
        # button to queue this color
        queueButton = QPushButton("Queue this color")
        queueButton.clicked.connect(self.queueColor)
        layout.addWidget(queueButton)
        self.colorBox.setLayout(layout)

    def setColor(self):
        row = self.rowSelect.value()
        column = self.colSelect.value()
        color = self.colorSelect.currentText()
        self.floor.setColor(row, column, color)

    def queueColor(self):
        row = self.rowSelect.value()
        column = self.colSelect.value()
        color = self.colorSelect.currentText()
        self.floor.setColor(row, column, color, False)

    def makeDigitBox(self):
        self.digitBox = QGroupBox("Digit Selection")
        layout = QVBoxLayout()
        self.digitSelect = QSpinBox()
        #digitSelect.setPrefix("Set this digit - ")
        self.digitSelect.setRange(0, 9)
        layout.addWidget(self.digitSelect)
        # button to immediately set this digit
        digitButton = QPushButton("Set this digit")
        digitButton.clicked.connect(self.setDigit)
        layout.addWidget(digitButton)
        # button to queue this digit
        queueButton = QPushButton("Queue this digit")
        queueButton.clicked.connect(self.queueDigit)
        layout.addWidget(queueButton)
        self.digitBox.setLayout(layout)

    def setDigit(self):
        digit = self.digitSelect.value()
        row = self.rowSelect.value()
        column = self.colSelect.value()
        self.floor.setDigit(row, column, digit)

    def queueDigit(self):
        digit = self.digitSelect.value()
        row = self.rowSelect.value()
        column = self.colSelect.value()
        self.floor.setDigit(row, column, digit, False)

    def makeFlushBox(self):
        self.flushBox = QGroupBox("Common Controls")
        layout = QVBoxLayout()
        flushButton = QPushButton("Flush the queue")
        layout.addWidget(flushButton)
        self.flushBox.setLayout(layout)
        flushButton.clicked.connect(self.flushQueue)

    def flushQueue(self):
        self.floor.flushQueue()
        
    def createGridGroupBox(self):
        self.gridGroupBoxlf = QGroupBox("Grid layout")
        layout = QGridLayout()

        for i in range(Dialog.NumGridRows):
            label = QLabel("Line %d:" % (i + 1))
            lineEdit = QLineEdit()
            layout.addWidget(label, i + 1, 0)
            layout.addWidget(lineEdit, i + 1, 1)

        layout.setColumnStretch(1, 10)
        layout.setColumnStretch(2, 20)
        self.gridGroupBox.setLayout(layout)

    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("Form layout")
        layout = QFormLayout()
        layout.addRow(QLabel("Line 1:"), QLineEdit())
        layout.addRow(QLabel("Line 2, long text:"), QComboBox())
        layout.addRow(QLabel("Line 3:"), QSpinBox())
        self.formGroupBox.setLayout(layout)

# Lightsweeper classes

class LSEmulateFloor(QGroupBox):

    def __init__(self, rows=3, cols=5):
        super(QGroupBox, self).__init__("Lightsweeper Floor Emulator")
        self.rows = rows
        self.cols = cols
        floorLayout = QVBoxLayout()
        self.setContentsMargins(0,0,0,0)

        # make all the rows
        self.tileRows = []
        for row in range(rows):
            thisRow = QFrame()
            thisRow.setContentsMargins(0,0,0,0)
            layout = QHBoxLayout()
            tiles = []
            # make the LSEmulateTile in each row
            for col in range(cols):
                tile = LSEmulateTile(row, col)
                tile.setContentsMargins(0,0,0,0)
                #tile.setMinimumSize(60, 80)
                tile.display(col+1)
                tile.show()
                tiles.append(tile)
                count = len(tiles)
                layout.addWidget(tile)
                if col == 0:
                    tile.setColor("red")
                elif col == 1:
                    tile.setColor("green")
                elif col == 2:
                    tile.setColor("blue")
                else:
                    tile.setColor("white")
                thisRow.setLayout(layout)

            self.tileRows.append(tiles)
            floorLayout.addWidget(thisRow)

        self.setLayout(floorLayout)
        # is that all ?

    def flushQueue(self):
        for row in self.tileRows:
            for tile in row:
                tile.flushQueue()

    def getTileList (self, row, column):
        tileList = []
        # whole floor
        if row < 1 and column < 1:
            for tileRow in self.tileRows:
                for tile in tileRow:
                    tileList.append(tile)
                    count = len(tileList)
        # whole row
        elif column < 1:
            tileRow = self.tileRows[row-1]
            for tile in tileRow:
                tileList.append(tile)
                count = len(tileList)
        # whole column
        elif row < 1:
            for tileRow in self.tileRows:
                tile = tileRow[column-1]
                tileList.append(tile)
                count = len(tileList)
        # single tile
        else:
            tileRow = self.tileRows[row-1]
            tileList = [tileRow[column-1]]
        return tileList
    
    def getCols (self):
        return self.cols

    def getRows (self):
        return self.rows

    def setColor(self, row, column, color, setItNow = True):
        tileList = self.getTileList(row, column)
        for tile in tileList:
            tile.setColor(color, setItNow)

    def setDigit(self, row, column, digit, setItNow = True):
        tileList = self.getTileList(row, column)
        for tile in tileList:
            tile.setDigit(digit, setItNow)

class LSEmulateTile(QFrame):

    def __init__(self, row=0, col=0):
        super(QFrame, self).__init__()
        self.row = row
        self.col = col
        self.segments = QLCDNumber(1) # 1 digit
        self.segments.setMinimumSize(30, 40)
        self.queueColor = "QLCDNumber {color: white }";
        self.queueDigit = 8;
        self.setContentsMargins(0,0,0,0)
        self.button = QPushButton("%d %d" % (row+1, col+1))
        #self.button = QToolButton()  # little button with no text
        self.button.setCheckable(True)
        layout = QVBoxLayout()
        layout.addWidget(self.segments)
        layout.addWidget(self.button)
        self.setLayout(layout)


    # attempt to get rid of
    # QWindowsWindow::setGeometry: Unable to set geometry 97x91+192+60
    #
    #def paintEvent(QPaintEvent pe)
    def paintEvent(self, pe):
        o = QStyleOption()
        o.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, o, p, self)

    def flushQueue(self):
            self.segments.setStyleSheet(self.queueColor)
            self.segments.display(self.queueDigit)
    
    def setColor (self, newColor, setItNow = True):
        str = "QLCDNumber {{color: {0} }}".format(newColor)
        self.queueColor = str;
        if setItNow:
            self.segments.setStyleSheet(str)
        pass
    
    def setDigit (self, newDigit, setItNow = True):
        self.queueDigit = newDigit;
        if setItNow:
            self.segments.display(newDigit)
    
    def getCol (self):
        return self.col

    def getRow (self):
        return self.row

    def display (self, val):
        self.segments.display(val)

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    dialog = Dialog()
    sys.exit(dialog.exec_())
