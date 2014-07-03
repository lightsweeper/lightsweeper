from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog,
        QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
        QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit,
        QVBoxLayout)

# Lightsweeper additions
from PyQt5.QtWidgets import (QLCDNumber, QWidget, QFrame, QSpinBox, QStyle, QStyleOption, QToolButton)
from PyQt5.QtGui import (QPainter)


class LSEmulateTile(QFrame):
    def __init__(self, event, row=0, col=0):
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
        # self._display(col+1)
        self.button.setCheckable(True)
        self.button.clicked.connect(event)
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

    def _flushQueue(self):
            self.segments.setStyleSheet(self.queueColor)
            self.segments.display(self.queueDigit)
    
    def _setColor (self, newColor, setItNow = True):
        str = "QLCDNumber {{color: {0} }}".format(newColor)
        self.queueColor = str;
        if setItNow:
            self.segments.setStyleSheet(str)
        pass
    
    def _setDigit (self, newDigit, setItNow = True):
        self.queueDigit = newDigit;
        if setItNow:
            self.segments.display(newDigit)
        return
    
    def _getCol (self):
        return self.col

    def _getRow (self):
        return self.row

    def _display (self, val):
        self.segments.display(val)
        return

    def _getButtonState(self):
        return self.button.isChecked()


    def _buttonPressed(self):
        print(self.button.isChecked())
        return

    ### Implementation of the Lightsweeper API
    def destroy(self):
        return

    def setColor(self, color):
        self._setColor(color)
        return

    def setShape(self, shape):
        self._setDigit(shape)

    def setTransition(self, transition):
        return

    def set(self,color=0, shape=0, transition=0):
        if (color != 0):
            self.setColor(color)
        if (shape != 0 ):
            self.setShape(shape)
        if(transition != 0):
            self.setTransition(transition)
        return

    def update(self,type):
        if (type == 'NOW'):
            return
        elif (type == 'CLOCK'):
            return
        elif (type == 'TRIGGER'):
            return
        else:
            return

    def version(self):
        return 1

    def blank(self):
        self.setColor('white')
        return

    def locate(self):
        return

    def demo (self, seconds):
        return

    def setAnimation(self):
        return

    def flip(self):
        return

    def status(self):
        return

    def reset(self):
        return

    def latch(self):
        return

    def unregister(self):
        return

    def assignAddress(self, address):
        self.address = address
        return

    def getAddress(self):
        return self.address

    def calibrate(self):
        return

    def read(self):
        return self._getButtonState()
        