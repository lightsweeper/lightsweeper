""" Contains descriptions of and methods for interfacing with LightSweeper tile objects """

import Colors
import Shapes

### Definition of the Lightsweeper low level API

class LSTile():
    def __init__(self, row=0, col=0):
        self.row = row
        self.col = col
        self.color = None
        self.shape = None
        self.segments = dict.fromkeys(list(map(chr, range(97, 97+7))))
        for segKey in self.segments.keys():
            self.segments[segKey] = None
        
    def set(self, shape=None, color=None, transition=0):
        if color is not None:
            self.setColor(color)
        if shape is not None:
            self.setShape(shape)
        if(transition != 0):
            self.setTransition(transition)


    def setColor(self, color):
       self.color = color
       for segKey in self.segments.keys():
           segment = self.segments[segKey]
           if segment is not None:
               self.segments[segKey] = color
               

    def setShape(self, shape):
        self.shape = shape
        if shape & Shapes.SEG_A:
            if self.segments["a"] is None:
                self.segments["a"] = self.color
        else:
            self.segments["a"] = None
        if shape & Shapes.SEG_B:
            if self.segments["b"] is None:
                self.segments["b"] = self.color
        else:
            self.segments["b"] = None
        if shape & Shapes.SEG_C:
            if self.segments["c"] is None:
                self.segments["c"] = self.color
        else:
            self.segments["c"] = None
        if shape & Shapes.SEG_D:
            if self.segments["d"] is None:
                self.segments["d"] = self.color
        else:
            self.segments["d"] = None
        if shape & Shapes.SEG_E:
            if self.segments["e"] is None:
                self.segments["e"] = self.color
        else:
            self.segments["e"] = None
        if shape & Shapes.SEG_F:
            if self.segments["f"] is None:
                self.segments["f"] = self.color
        else:
            self.segments["f"] = None
        if shape & Shapes.SEG_G:
            if self.segments["g"] is None:
                self.segments["g"] = self.color
        else:
            self.segments["g"] = None
        
        
    def setSegments(self, rgb):
        c = Colors.rgbToSegments(rgb)
        self.segments["a"] = c[0]
        self.segments["b"] = c[1]
        self.segments["c"] = c[2]
        self.segments["d"] = c[3]
        self.segments["e"] = c[4]
        self.segments["f"] = c[5]
        self.segments["g"] = c[6]
        

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

    def destroy(self):
        raise NotImplementedError()

    def version(self):
        raise NotImplementedError()

    def blank(self):
        self.setColor(None)

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


    # set immediately or queue this digit in addressed tiles
    # this is a convenience function that calls setSegments
    def setDigit(self, row, column, digit, setItNow = True):
        raise NotImplementedError()



