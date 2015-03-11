import Colors
import Shapes

### Definition of the Lightsweeper low level API

### only very common operations are coded here

class LSTile():
    def __init__(self, row=0, col=0):
        self.row = row
        self.col = col
        self.color = Colors.BLACK
        self.shape = Shapes.ZERO

    def destroy(self):
        raise NotImplementedError()
        
    def set(self, shape=0, color=0, transition=0):
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

    # set immediately or queue this color in addressed tiles
    def setColor(self, color):
       self.set(color=color)

    def setShape(self, shape):
        self.set(shape=shape)
        
    # set immediately or queue these segments in addressed tiles
    # segments is a seven-tuple interpreted as True or False
    def setSegments(self, segments):
        self.segments = Colors.rgbToSegments(segments)

    def setTransition(self, transition):
        raise NotImplementedError()
        
    def getShape(self):
        return self.shape
        
    def getColor(self):
        return self.color
        
    def getCol (self):
        return self.col

    def getRow (self):
        return self.row

    def update(self,type):
        raise NotImplementedError()

    def version(self):
        raise NotImplementedError()

    def blank(self):
        self.setColor(Colors.BLACK)

    def locate(self):
        raise NotImplementedError()

    def demo (self, seconds):
        raise NotImplementedError()

    def setAnimation(self):
        raise NotImplementedError()

    def flip(self):
        raise NotImplementedError()

    def status(self):
        raise NotImplementedError()

    def reset(self):
        raise NotImplementedError()

    # write any queued colors or segments to the display
    def latch(self):
        raise NotImplementedError()

    def unregister(self):
        raise NotImplementedError()

    # addresses may be HW specific, but can support here
    def assignAddress(self, address):
        self.address = address

    def getAddress(self):
        return self.address

    def calibrate(self):
        raise NotImplementedError()

    def read(self):
        raise NotImplementedError()
        
    def update(self,type):
#        if (type == 'NOW'):
#            return
#        elif (type == 'CLOCK'):
#            return
#        elif (type == 'TRIGGER'):
#            return
#        else:
#            return
        raise NotImplementedError()

    # TODO - how is this different from latch?
    def flushQueue(self):
        raise NotImplementedError()

###################################

    # REMOVEME - old stuff for reference only

    # return a list of two-tuples
    # row or column = 0 returns the whole column or row, respectively
    # single tile returns list of itself
    def getTileList (self, row, column):
        raise NotImplementedError()

    # set immediately or queue this digit in addressed tiles
    # this is a convenience function that calls setSegments
    def setDigit(self, row, column, digit, setItNow = True):
        raise NotImplementedError()

    # return a list of active pressure sensors
    def getSensors (self):
        raise NotImplementedError()

    # TODO - not yet used perhaps useful if target slot can be passed in
    def pollSensors(self):
        raise NotImplementedError()

