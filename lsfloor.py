""" Contains descriptions of and methods for interfacing with LightSweeper floors """

from LSRealTile import LSRealTile
from LSRealTile import LSOpen
from lstile import LSTile
from lsconfig import LSFloorConfig
from lsconfig import userSelect

import Colors
import Shapes

from collections import defaultdict
from queue import Queue

import atexit
import copy
import inspect
import os
import random
import sys
import threading
import time

wait=time.sleep

class LSFloor():
    """
        This class describes an abstract lightsweeper floor. It is inherited by both LSRealFloor as well as Lightsweeper
        emulators via LSEmulateFloor.

        Attributes:
            conf (LSFloorConfig):   An LSFloorConfig object containing the floor's configuration
            rows (int):             The number of rows
            cols (int):             The number of columns
            tileList (list):        A single array of LSTile objects
            tiles (list):           A double array of LSTile objects, e.g.: tiles[row][column]
            views (list):           A list of emulators and displays bound to this floor
    """
    def __init__(self, conf, eventCallback=None):

        self.conf = conf
        self.rows = conf.rows
        self.cols = conf.cols

        if eventCallback is None:
            print("lsfloor: eventCallback not defined")

        self.tiles = []
        self.tileList = []
        self.views = []
        self.sensors = defaultdict(lambda: defaultdict(int))
        self._virtualTileList = []

        # Initialize calibration map
        self.calibrationMap = conf.calibrationMap

        # Setup tiles specified in conf, then populate self.tiles and self.tileList
        self._addTilesFromConf()

        # Make a copy of this skeleton
        self._nakedView = copy.deepcopy(self)

        # Become a dispatcher, this root instance of LSFloor will now become the public-facing
        # interface that relays commands to the LSFloor subclasses in self.views and maps their
        # outputs into its own datastructures
        self._patchFrom(self)

        # Start a thread to handle tile-stepping events
        # self._events is a thread-safe queue of events that look like (row, col, touch-sensor-percent)
        # LSFloor instances put event tuples into the queue
        self._events = Queue()
        eventHandler = self._handleEvents(0, "{:s}-io-root", self._events, self.tiles, eventCallback)
        eventHandler.start()

        # Register an LSRealFloor instance if there are real tiles in the configuration
        if self.conf.containsReal() is True:
            self.register(LSRealFloor)

    def _addTilesFromConf(self):
        
        self._addressToRowColumn = {}
        self.tileList = []
        
        for (row, col, port, address, calibration) in self.conf.config:
            tile = self._returnTile(row, col, port)
            self._addressToRowColumn[(address,port)] = (row, col)
            tile.assignAddress(address)
            tile.port = port
            wait(.05)
            self.tileList.append(tile)
            if port == "virtual":
                self._virtualTileList.append(tile)

        # Build the nested tile index
        self.tiles = defaultdict(lambda: defaultdict(int))
        for tile in self.tileList:
            self.tiles[tile.row][tile.col] = tile

        # Clear the board
        self.clearAll()

    def _returnTile(self, row, col, port):
        # Returns an abstract tile object
        return(LSTile(row, col))

    def _patchFrom(self, target):
        # This method remaps the public methods of LSFloor to fork their outputs to each
        # LSFloor subclass instance in self.views

        def makeFunc (method):
            def funcProxy(*args, **kwargs):
                for floor in self.views:
                    try:
                        func = getattr(floor, method.__name__)
                        func(*args, **kwargs)
                    except AttributeError as e:
                        print("Warning: {:s}()-> Method not supported by {:s}".format(method.__name__, repr(floor)))
                        print(e) # Debugging
            return funcProxy

        for name, method in inspect.getmembers(target, callable):
            if name is not "register" and name.startswith("_") is False:
                setattr(self, name, makeFunc(method))

    class _IOLoop(threading.Thread):
        # The _IOLoop class runs as a thread for each registered LSFloor instance
        # which continously calls the instance's pollEvents() generator and adds
        # corresponding events to the root LSFloor instance's _event Queue.
        # An event is a tuple of the form (row, col, tile-sensor-percent)

        def __init__(self, ID, name, view):
            threading.Thread.__init__(self)
            self.ID = ID
            self.name = name
            self.view = view

        def run(self):
            wait(3)   
            print("Starting " + self.name)
            pollEvents = getattr(self.view, "pollEvents")
            pollingLoop = pollEvents()
            staleSensor = 0
            while True:
                event = next(pollingLoop)
                r,c = event[0], event[1]
                sensorPcnt = event[2]
                try:
                    staleSensor = self.view.tiles[r][c].sensor
                except AttributeError:
                    staleSensor = 0
                if staleSensor != sensorPcnt:
                    tile = self.view.tiles[r][c]
                    tile.sensor = sensorPcnt
                    self.view._root._events.put(event)

    class _handleEvents(threading.Thread):
            # The _handleEvents class runs as a single thread from the root LSFloor
            # dispatching instance and monitors the _event Queue. When new events
            # arrive to be processed it sets the corresponding tile's sensor attribute
            # to the value specified by the event and pushes the event to the floor's
            # event handler if one is specified.
            # Events are tuples that look like (row, col, sensor-percent)
        def __init__(self, ID, name, eventQueue, tiles, eventCallback):
            threading.Thread.__init__(self)
            self.ID = ID
            self.name = name
            self.queue = eventQueue
            self.tiles = tiles
            
            if eventCallback is None:
                self.pushEvent = lambda event: None
            else:
                self.pushEvent = lambda e: eventCallback(e[0],e[1],e[2])

        def run(self):
            wait(2)
            stale = 0
            while(True):
                event = self.queue.get()
                row,col,sensorPcnt = event
                tile = self.tiles[row][col]
                try:
                    stale = tile.sensor
                except AttributeError:
                    print("INFO: The tile at ({:d},{:d}) has been touched for the very first time.".format(row,col))
                    stale = 0
                if stale is 0:
                    print("Stepped on ({:d},{:d})".format(row,col)) # Debugging
                if sensorPcnt is 0:
                    print("Stepped off ({:d},{:d})".format(row,col)) # Debugging
                tile.sensor = sensorPcnt
                self.pushEvent(event)

    def register(self, Emulator):
        """
            Allows you to register additional emulators to this floor.

            Example:
                >>> import lsfloor, lsconfig, lsemulate

                >>> conf = lsconfig.LSFloorConfig(rows=5, cols=5)
                >>> conf.makeVirtual()
                Creating virtual configuration with 5 rows and 5 columns.

                >>> floor = lsfloor.LSFloor(conf)
                lsfloor: eventCallback not defined

                >>> floor.register(lsemulate.LSPygameFloor)
                Registering: LSPygameFloor
                Making the screen (500x500)
                Starting LSPygameFloor-io
        """
        print("Registering: " + Emulator.__name__)
        baseFloor = MetaFloor(copy.deepcopy(self._nakedView)) # Make a new floor instance with a copy of the naked floor
        newFloor = object.__new__(Emulator)  # An instantiation of Emulator without calling __init__
        baseFloor.__class__ = newFloor.__class__ # Take the class from Emulator's floor
        baseFloor._root = self
        baseFloor.init()
        self.views.append(baseFloor)
        viewIndex = len(self.views)

        # Start a polling loop for this floor in a new thread
        baseFloor.io = self._IOLoop(viewIndex, "{:s}-io".format(Emulator.__name__), self.views[viewIndex-1])
        baseFloor.io.start()
                
    def saveAndExit(self, exitCode):
        """
            Allows you to gracefully exit while saving any changes to calibration state.
        """

        try:
            self._root.views[0]._saveState()
        except AttributeError:
            print("Calibration state not updated.")
        print("Goodbye")
        os._exit(exitCode)

    def setColor(self, row, col, color):
        """
            Sets the color of the selected tile.
        """
        tile = self.tiles[row][col]
        tile.setColor(color)

    def setShape(self, row, col, shape):
        """
            Sets the shape of the selected tile.
        """
        tile = self.tiles[row][col]
        tile.setShape(shape)

    def setAllColor(self, color):
        """
            Sets all tiles to color (they will retain their current shape)
        """
        for tile in self.tileList:
            self.setColor(tile.row, tile.col, color)

    def setAllShape(self, shape):
        """
            Sets all tiles to shape (they will retain their current color)
        """
        for tile in self.tileList:
            self.setShape(tile.row, tile.col, shape)

# TODO
    def setDigit(self, row, column, digit, color=None):
        """
            Sets the tile at row, column to the provided digit.
        """
        pass

    def set(self, row, col, shape, color):  # set is a python type, we may want to rename this
        """
            Sets the color and shape simultaneously.
        """
        tile = self.tiles[row][col]
        tile.set(shape, color)

    def setRow(self, row, shape, color):
        for tile in self.tiles[row]:
            tile.set(shape, color)

    def setColumn(self, col, shape, color):
        tiles = list(zip(*self.tiles[::-1]))
        for tile in tiles[col]:
            tile.set(shape, color)

    def setAll(self, shape, color):
        for tile in self.tileList:
            self.set(tile.row, tile.col, shape, color)

    #segments is a list of seven colors in A,...,G order of segments
    def setSegments(self, row, col, segments):
        tile = self.tiles[row][col]
        tile.setSegments(segments)

    def setAllSegments(self, segments):
        for tile in self.tileList:
            self.setSegments(tile.row, tile.col, segments)

    def blank(self, row, col):
        """
            Blanks the tile at row, col
        """
        tile = self.tiles[row][col]
        tile.blank()

    def clearAll(self):
        """
            Blanks the whole floor.
        """
        for tile in self.tileList:
            tile.blank()

    def renderFrame(self, frame):
    # TODO: LSRealTile, should optimize tile calls

        cols = frame.pop(0)
        row = 0
        col = 0
        for _ in itertools.repeat(None, int(len(frame)/3)):
            if col is cols:
                row += 1
                col = 0
            rMask = frame.pop(0)
            gMask = frame.pop(0)
            bMask = frame.pop(0)
            if rMask is not 128:
                self.tiles[row][col].setSegments((rMask,gMask,bMask))
           #     print("{:d},{:d} -> ({:d},{:d},{:d})".format(row,col,rMask,gMask,bMask)) # Debugging
            col += 1

#    def pollSensors(self):
 #       return(list())

    def heartbeat(self):
        pass

    def showBoard(self):
        pass

    def resetBoard(self):
        for tile in self.tileList:
            tile.reset()
        return

    def _flushQueue(self, row, col):
        # Calls flushQueue() on the given tile (underlying functionality not currently implemented)
        tile = self.tiles[row][col]
        tile.flushQueue()

    def RAINBOWMODE(self, updateFrequency = 0.4):
        '''
            OMG! Double rainbow!!! What does this mean?!
        '''
        self.setAllShape(Shapes.EIGHT)
        RAINBOW = [Colors.RED,
                Colors.YELLOW,
                Colors.GREEN,
                Colors.CYAN,
                Colors.BLUE,
                Colors.MAGENTA,
                Colors.WHITE]

        for COLOR in RAINBOW:
            self.setAllColor(COLOR)
            wait(updateFrequency)


#handles all communications with RealTile objects, serving as the interface to the
#actual lightsweeper floor. thus updates are pushed to it (display) and also pulled from it
#(sensor changes)
class LSRealFloor(LSFloor):
    """
        This class extends LSFloor with methods specific to interacting with real Lightsweeper hardware
    """

    def init(self):

        # Initialize the serial ports
        self.realTiles = LSOpen()
        self.sharedSerials = dict()
        self._addTilesFromConf()

        # Save changes to self.config (namely the most recent calibrationMap)
        atexit.register(self._saveState)

    def _saveState(self):
        self.conf.calibrationMap = self.calibrationMap
        self.conf.writeConfig(overwrite=True, message="Saving calibration map...")

    def _returnTile(self, row, col, port):
        # Returns an abstract tile object if the configuration calls for a virtual tile
        # otherwise returns a real tile object
        if port == "virtual":
            return(LSTile(row, col))
        else:
            return(LSRealTile(self.realTiles.sharedSerials[port], row, col))

    def setAllColor(self, color):
        for port in self.realTiles.sharedSerials.keys():
            zeroTile = LSRealTile(self.realTiles.sharedSerials[port])
            zeroTile.assignAddress(0)
            zeroTile.setColor(color)
        for tile in self.tileList:
            tile.color = color

    def setAllShape(self, shape):
        for port in self.realTiles.sharedSerials.keys():
            zeroTile = LSRealTile(self.realTiles.sharedSerials[port])
            zeroTile.assignAddress(0)
            zeroTile.setShape(shape)
        for tile in self.tileList:
            tile.shape = shape

    def setAllSegments(self, segments):
        for port in self.realTiles.sharedSerials.keys():
            zeroTile = LSRealTile(self.realTiles.sharedSerials[port])
            zeroTile.assignAddress(0)
            zeroTile.setSegments(segments)
        for tile in self.tileList:
            tile.shape = segments[0]|segments[1]|segments[2]

    def clearAll(self):
        for port in self.realTiles.sharedSerials.keys():
            zeroTile = LSRealTile(self.realTiles.sharedSerials[port])
            zeroTile.assignAddress(0)
            zeroTile.blank()
        for tile in self.tileList:
            tile.shape = 0
            tile.color = 0

    def latch(self, row, col):
        tile = self.tiles[row][col]         # TODO: Check if tile is virtual
        tile.latch()

    def latchAll(self):
        for port in self.realTiles.sharedSerials.keys():
            zeroTile = LSRealTile(self.realTiles.sharedSerials[port])
            zeroTile.assignAddress(0)
            zeroTile.latch()

    def pollEvents(self):
        tiles = self.tileList
        while True:
            for tile in tiles:
                reading = tile.sensorStatus()

                cMap = self.calibrationMap[(tile.address,tile.port)]
                # A higher reading is less weight on the pressure sensor
                lowest = cMap[0]
                highest = cMap[1]
                if reading < lowest:
                    lowest = reading
                    cMap[0] = lowest
                elif reading > highest:
                    highest = reading
                    cMap[1] = highest
                self.calibrationMap[(tile.address,tile.port)] = cMap

                if reading is highest:
                    yield((tile.row, tile.col, 0))
                elif reading is lowest and lowest < 127:
                    yield((tile.row, tile.col, 100))
                else:
                    pcntOut = (((reading-highest)*100)/(lowest-highest))
                    yield((tile.row, tile.col, pcntOut))


class MetaFloor(LSFloor):
    def __init__(self, thisFloor):
        className = thisFloor.__class__.__name__
        self.__class__ = type(className, (self.__class__, thisFloor.__class__), {})
        self.__dict__ = thisFloor.__dict__


def main():

    def getRandRow(lsDisplay):
        return random.randint(0, lsDisplay.rows-1)

    def getRandCol(lsDisplay):
        return random.randint(0, lsDisplay.cols-1)

    useRealFloor = True
    try:
        realTiles = LSOpen()
    except Exception as e:
        useRealFloor = False

    print("Importing LSDisplay")
    import lsdisplay

    d = lsdisplay.LSDisplay()

    input("Press return to begin tests")

    print("Testing set")
    d.set(getRandRow(d),getRandCol(d),Shapes.L,Colors.RED)
    d.set(getRandRow(d),getRandCol(d),Shapes.S,Colors.MAGENTA)
    d.heartbeat()
#    wait(2)
    input("Press return to continue")

    print("Testing setAll")
    d.setAll(Shapes.B,Colors.BLUE)
    d.heartbeat()
#    wait(2)
    input("Press return to continue")

    trow = getRandRow(d)
    tcol = getRandCol(d)

    print("Testing setColor")
    d.setColor(trow,tcol,Colors.GREEN)
    d.heartbeat()
#    wait(2)
    input("Press return to continue")

    print("Testing setShape")
    d.setShape(trow,tcol,Shapes.ZERO)
    d.heartbeat()
#    wait(2)
    input("Press return to continue")

    print("Testing setAllColor")
    d.setAllColor(Colors.MAGENTA)
    d.heartbeat()
#    wait(2)
    input("Press return to continue")

    print("Testing setAllShape")
    d.setAllShape(Shapes.DASH)
    d.heartbeat()
#    wait(2)
    input("Press return to continue")

    print("Testing clear")
    d.clear(getRandRow(d),getRandCol(d))
    d.heartbeat()
#    wait(2)
    input("Press return to continue")

    print("Testing clearAll")
    d.clearAll()
    d.heartbeat()
#    wait(2)
    input("Press return to continue")

    print("Testing setCustom")
    d.setCustom(0, 0, [1,3,2,6,4,5])
    d.heartbeat()
    wait(.5)
    d.setCustom(0, 0, [0,0,0,0,0,0,7])
    d.heartbeat()
    wait(.5)
    d.setCustom(0, 0, [1,3,2,6,4,5])
    d.heartbeat()
    wait(.5)
    d.setCustom(0, 0, [0,0,0,0,0,0,7])
    d.heartbeat()
    wait(.5)
    d.setCustom(0, 0, [1,3,2,6,4,5])
    d.heartbeat()
    wait(.5)
    d.setCustom(0, 0, [0,0,0,0,0,0,7])
    d.heartbeat()
    wait(.5)
    d.setCustom(0, 0, [1,3,2,6,4,5,7])
    d.heartbeat()
#    wait(2)
    input("Press return to continue")

    print("Testing setAllCustom")
    d.setAllCustom([1,3,2,6,4,5,7])
    d.heartbeat()
#    wait(2)
    input("Press return to continue")

    print("Testing setColor after setSegment")
    # TODO: Make LSRealTile remember shape    
    d.setAllColor(Colors.YELLOW)
    d.heartbeat()

    input("Press return to exit")
    d.floor.saveAndExit(0)

if __name__ == '__main__':

    main()

