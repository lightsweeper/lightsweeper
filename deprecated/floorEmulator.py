#!/usr/bin/env python

from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog,
        QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
        QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QVBoxLayout)

# Lightsweeper additions
from PyQt5.QtWidgets import (QSpinBox, QPlainTextEdit)
from PyQt5.QtCore import (QTimer)
from LSEmulateFloor import LSEmulateFloor

class Dialog(QDialog):
    NumRows =  6
    NumCols = 8

    def __init__(self):
        super(Dialog, self).__init__()

        mainLayout = QHBoxLayout()
        self.createMenu()
        mainLayout.setMenuBar(self.menuBar)

        # make the API controls
        self.makeTestGroupBox()
        mainLayout.addWidget(self.testGroupBox)

        # make the Lightsweeper floor
        self.floor = LSEmulateFloor(self.NumRows, self.NumCols)
        mainLayout.addWidget(self.floor)

        #self.setContentsMargins(0,0,0,0) # chops title
        #mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(mainLayout)
        self.setWindowTitle("Lightsweeper API Demonstrator")
        self.flushQueue()

        # start sensor polling
        self.lastSensors = None
        QTimer.singleShot(3000, self.pollSensors)

    # TODO - move this into API
    def pollSensors(self):
        actives = self.floor.getSensors()
        if actives != self.lastSensors:
            self.lastSensors = actives
            wholeStr = "Active sensors:"
            for sensor in actives:
                str = " ({0},{1}) ".format(sensor[0]+1, sensor[1]+1)
                wholeStr = wholeStr + str
            self.myTextOut.appendPlainText(wholeStr)
        QTimer.singleShot(500, self.pollSensors) # schedule next poll
      
    def createMenu(self):
        self.menuBar = QMenuBar()
        self.fileMenu = QMenu("&File", self)
        self.exitAction = self.fileMenu.addAction("E&xit")
        self.menuBar.addMenu(self.fileMenu)
        self.exitAction.triggered.connect(self.accept)

    def makeTestGroupBox(self):
        self.testGroupBox= QGroupBox("test controls")
        layout = QGridLayout()
        self.makeTileSelect()
        layout.addWidget(self.tileSelectBox, 0, 1)
        self.makeColorBox()
        layout.addWidget(self.colorBox, 1, 0)
        self.makeDigitBox()
        layout.addWidget(self.digitBox, 1, 1)
        self.makeFlushBox()
        layout.addWidget(self.flushBox, 2, 0)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        layout.addWidget(buttonBox, 2, 1)

        self.myTextOut = QPlainTextEdit() 
        #QPlainTextEdit read only but with text selectable by cursor
        self.myTextOut.setReadOnly(True)
        #self.myTextOut.setTextInteractionFlags(self.myTextOut.textInteractionFlags() | QtCore.Qt.TextSelectableByKeyboard)
        layout.addWidget(self.myTextOut, 3, 0, 1, 2) # span all columns
    
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
        #self.myTextOut.appendPlainText("setColor") 

    def queueColor(self):
        row = self.rowSelect.value()
        column = self.colSelect.value()
        color = self.colorSelect.currentText()
        self.floor.setColor(row, column, color, False)
        #self.myTextOut.appendPlainText("queueColor") 

    def makeDigitBox(self):
        self.digitBox = QGroupBox("Digit Selection")
        layout = QVBoxLayout()
        self.digitSelect = QSpinBox()
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
        # TESTING
        #self.newTile.setDigit(digit, True)

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

    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("Form layout")
        layout = QFormLayout()
        layout.addRow(QLabel("Line 1:"), QLineEdit())
        layout.addRow(QLabel("Line 2, long text:"), QComboBox())
        layout.addRow(QLabel("Line 3:"), QSpinBox())
        self.formGroupBox.setLayout(layout)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    dialog = Dialog()
    sys.exit(dialog.exec_())
