import Colors
import Shapes

### Definition of the Lightsweeper low level API

### only very common operations are coded here

# Segment display commands from 0x80 to 0xBF
SEGMENT_CMD =   0x80
SEGMENT_CMD_END = (SEGMENT_CMD+0x3F)
# Depending on the command, up to 4 byte fields will follow (R,G,B and transition)
# Three bits in command declare that R, G, and/or B segment fields will follow
# Two bits define the update condition
# One bit declares that the transition field will follow
#
# One segment byte field will be provided for each of the RGB color bits declared
# Three segment fields allow for arbitrary colors for each segment
# Segment fields are defined in the -abcdefg order, to match LedControl library
SEGMENT_FIELD_MASK  = 0x38
SEGMENT_FIELD_RED   = 0x20
SEGMENT_FIELD_GREEN = 0x10
SEGMENT_FIELD_BLUE  = 0x08
# Segment fields that are not given clear the associated target color segments
# unless the LSB is set in one of the provided segment fields
SEGMENT_KEEP_MASK  = 0x80 # if MSB set, do not clear any segment data

class LSTile():
    def __init__(self, row=0, col=0):
        self.row = row
        self.col = col
        self.color = None
        self.shape = None
        self.segments = dict.fromkeys(list(map(chr, range(97, 97+7))))
        for segKey in self.segments.keys():
            self.segments[segKey] = None

    def destroy(self):
        raise NotImplementedError()
        
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
       pass
        

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

