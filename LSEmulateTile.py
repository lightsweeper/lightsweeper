# Lightsweeper additions
from lstile import LSTile
import Colors
import Shapes

# this class holds a seven segment display and a button to mimic the pressure sensor
# it does no segment processing, it just passes thru to the seven segment display
class EmulateTile(LSTile):
    def __init__(self, row=0, col=0):
        self.row = row
        self.col = col
#        self.floor = floor
        self.color = Colors.BLACK
        self.shape = Shapes.ZERO
        
#        if labelTiles:
#            self.post = "_labels.png"
#        else:
#            self.post = ".png"
        self.set(self.shape, self.color)

    def flushQueue(self):
        pass

    def set(self, shape=Shapes.ZERO, color=Colors.BLACK):
        self.shape = shape
        self.color = color
        self.segments = []
        if shape & Shapes.SEG_A:
            self.segments.append(color)
        else:
            self.segments.append(Colors.BLACK)
        if shape & Shapes.SEG_B:
            self.segments.append(color)
        else:
            self.segments.append(Colors.BLACK)
        if shape & Shapes.SEG_C:
            self.segments.append(color)
        else:
            self.segments.append(Colors.BLACK)
        if shape & Shapes.SEG_D:
            self.segments.append(color)
        else:
            self.segments.append(Colors.BLACK)
        if shape & Shapes.SEG_E:
            self.segments.append(color)
        else:
            self.segments.append(Colors.BLACK)
        if shape & Shapes.SEG_F:
            self.segments.append(color)
        else:
            self.segments.append(Colors.BLACK)
        if shape & Shapes.SEG_G:
            self.segments.append(color)
        else:
            self.segments.append(Colors.BLACK)

    def setShape(self, shape):
        self.set(shape, self.color)
        
    def setColor(self, color):
       self.set(self.shape, color)
        
    def setSegments(self, rgb):
        self.segments = Colors.rgbToSegments(rgb)

    def getShape(self):
        return self.shape

    def getSensors(self):
#        if self.button.isChecked():
#            return (self.row, self.col)
#        else:
#            return None
        pass
            
    def sensorStatus(self):
#        return 255 # TODO: Return based on pygame input
        pass

    def getTileList (self, row, column):
        return (self.row, self.col)

    def getCol (self):
        return self.col

    def getRow (self):
        return self.row

   # def _display (self, val):
   #     return

  #  def _getButtonState(self):
  #      return self.button.isChecked()


  #  def _buttonPressed(self):
  #      print("Button state is", self.button.isChecked(), self.row, self.col)
  #      self.floor.handleTileSensed(self.row, self.col)

    ### Implementation of the Lightsweeper API
    def destroy(self):
        return


    def setTransition(self, transition):
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
        self.setColor(Colors.BLACK)
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

    def getAddress(self):
        return self.address

    def calibrate(self):
        return

#    def read(self):
#        return self._getButtonState()
