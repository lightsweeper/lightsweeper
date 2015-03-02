
class LSApi():
    # segments to light for digits, in 0..6 order
	#
	#  00
	# 5  1
	# 5  1
	#  66
	# 4  2
	# 4  2
	#  33
	#
    segs0 = (1, 1, 1, 1, 1, 1, 0)
    segs1 = (0, 1, 1, 0, 0, 0, 0)
    segs2 = (1, 1, 0, 1, 1, 0, 1)
    segs3 = (1, 1, 1, 1, 0, 0, 1)
    segs4 = (0, 1, 1, 0, 0, 1, 1)
    segs5 = (1, 0, 1, 1, 0, 1, 1)
    segs6 = (1, 0, 1, 1, 1, 1, 1)
    segs7 = (1, 1, 1, 0, 0, 0, 0)
    segs8 = (1, 1, 1, 1, 1, 1, 1) #x instead of 8
    segs9 = (1, 1, 1, 1, 0, 1, 1)
    dash = (0, 0, 0, 0, 0, 0, 1)
    segMasks = [segs0,segs1,segs2,segs3,segs4,segs5,segs6,segs7,segs8,segs9,dash]

    # TODO - there are no variable members in this API yet
    # perhaps no need to call constructor - super().__init__()

    # TODO - could throw exceptions here make sure derived classes implement them
    # but not worth the bother

    @staticmethod
    def getDash():
        return LSApi.segMasks[10]

    # write any queued colors or segments to the display
    def flushQueue(self):
        pass

    # return a list of two-tuples
    # row or column = 0 returns the whole column or row, respectively
    # single tile returns list of itself
    def getTileList (self, row, column):
        pass

    # set immediately or queue this color in addressed tiles
    def setColor(self, row, column, color, setItNow = True):
        pass

    # set immediately or queue these segments in addressed tiles
    # segments is a seven-tuple interpreted as True or False
    def setSegments(self, row, column, segments, setItNow = True):
        pass

    # set immediately or queue this digit in addressed tiles
    # this is a convenience function that calls setSegments
    def setDigit(self, row, column, digit, setItNow = True):
        pass

    # return a list of active pressure sensors
    def getSensors(self):
        pass

    # TODO - not yet used perhaps useful if target slot can be passed in
    def pollSensors(self):
        pass

