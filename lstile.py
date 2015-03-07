#!/usr/bin/env python

### Definition of the Lightsweeper low level API

### only very common operations are coded here

class LSTile():
    def __init__(self, row=0, col=0):
        super().__init__()

    def destroy(self):
        raise NotImplementedError()

    # set immediately or queue this color in addressed tiles
    def setColor(self, color):
        raise NotImplementedError()

    def setShape(self, shape):
        raise NotImplementedError()

    def setTransition(self, transition):
        raise NotImplementedError()

    def set(self, color=0, shape=0, transition=0):
        raise NotImplementedError()

    def update(self,type):
        raise NotImplementedError()

    def version(self):
        raise NotImplementedError()

    def blank(self):
        raise NotImplementedError()

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

    # set immediately or queue these segments in addressed tiles
    # segments is a seven-tuple interpreted as True or False
    def setSegments(self, row, column, segments, setItNow = True):
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

