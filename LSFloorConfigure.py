#!/usr/bin/env python

import os
import json
import numbers
from collections import defaultdict
from LSRealTile import lsOpen
from LSRealTile import LSRealTile

class FileDoesNotExistError(IOError):
    """ Custom exception returned when the config file is non-existant. """
    pass

class CannotParseError(IOError):
    """ Custom exception returned when the config file is present but cannot be parsed. """
    pass


class lsFloorConfig:
    """
        This class implements methods to read/write and otherwise
        manipulate Lightsweeper floor configurations.

        Attributes:
            fileName (str): The name of the config file on disk
            cells (int):    The number of cells in the lightsweeper matrix.
            rows (int):     The number of rows in the lightsweeper matrix.
            cols (int):     The number of columns in the lightsweeper matrix.
            config (list):  A list of 4-tuples of the form (row, col, port, address)
            board (dict):   A dictionary of dictionaries sorted by row and column, each
                            containing a tuple of the corresponding tile's port and address
    """

    cells = 0
    rows = 0
    cols = 0

    def __init__(self, configFile=None, rows=None, cols=None):

        if configFile is not None:
            if configFile.endswith(".floor") is False:
                configFile += ".floor"
            self.fileName = configFile
            try:
                self.config = self.loadConfig(configFile)
            except FileDoesNotExistError as message:
                if rows is not None and cols is not None:
                    self.config = self._createVirtualConfig(rows, cols)
                else:
                    print(message)
                    raise
            except CannotParseError:
                print("Could not parse {:s}".format(configFile))
                print(message)
                raise
            except IOError as message:
                print(message)
                raise
            finally:
                self._parseConfig(self.config)



    def loadConfig(self, fileName):
        if os.path.exists(fileName) is True:
            if os.path.isfile(fileName) is not True:
                raise IOError(fileName + " is not a valid floor config file!")
        else:
            raise FileDoesNotExistError(fileName + " does not exist!")
        try:
            with open(fileName) as configFile:
                return json.load(configFile)
        except Exception as message:
            print(message)
            raise CannotParseError("Could not parse " + fileName + "!")
        print("Board mapping loaded from " + fileName)


    # prints the list of 4-tuples
    def printConfig(self):
        print("The configuration has " + repr(len(self.config)) + " entries:")
        for cell in self.config:
            print(repr(cell))


    def _createVirtualConfig(self, rows, cols):
        assert isinstance(rows, numbers.Integral), "Rows must be a whole number."
        assert isinstance(cols, numbers.Integral), "Cols must be a whole number."
        print("Creating virtual configuration with {:d} rows and {:d} columns.".format(rows,cols))
        virtualConfig = list()
        row = 0
        col = 0
        for i in range(1,rows*cols+1):
            virtualConfig.append((row, col, "virtual", i))
            if col < cols-1:
                col += 1
            else:
                row += 1
                col = 0
        return(virtualConfig)


    def _parseConfig(self, config):
        def defdict():
            return defaultdict(int)
        self.cells = 0
        self.rows = 0
        self.cols = 0
        self.board = defaultdict(defdict)
        for (row, col, port, addr) in config:
            self.cells += 1
            if row >= self.rows:
                self.rows = row + 1
            if col >= self.cols:
                self.cols = col + 1
            self.board[row][col] = (port, addr)


def main():
# Warning: spaghetti code ahead


    def validateRows(numTiles, rows):
        try:
            rows = int(rows)
        except:
            print("You must enter a whole number!")
            return False
        if rows > numTiles:
            print("There are only " + repr(numTiles) + " tiles!")
            return False
        return True

    def pickRows(message):
        rows = input(message)
        while validateRows(totaltiles, rows) is False:
            rows = input(message)
        return rows

    def YESno(message):
        answer = input("{:s} [Y/n]: ".format(message))
        if answer in ("yes", "Yes", "YES", "y", "Y"):
            return True
        elif answer in ("no", "No", "NO", "n", "N"):
            return False
        else:
            print("Please answer Yes or No.")
            return YESno(message)


    def pickFile(message):
        fileName = input(message)
        if fileName == "" or fileName == "NEW":
            return None
        else:
            if fileName.endswith(".floor") is False:
                fileName += ".floor"
            if os.path.exists(fileName) is False:
                if YESno(fileName + " does not exist, would you like to create it?") is True:
                    print("Creating {:s}.".format(fileName))
                    floorConfig = lsFloorConfig()
                    floorConfig.fileName = fileName
                    return floorConfig
                else:
                    return pickFile(message)
            try:
                return lsFloorConfig(fileName)
            except:
                return pickFile(message)

    def interactiveConfig (config = None):

        if config is None:
            print("Starting a new configuration from scratch.")
            config = []
        else:
            print("Configuring {:s}".format(config.fileName))

        rows = pickRows("\nHow many rows do you want?: ")

        cols = int(totaltiles/rows)
        print("OK, you have a floor with " + repr(rows) + " by " + repr(cols)  + " columns")

        print("Blanking all tiles.")
        for port in tilepile.lsMatrix:
            myTile = LSRealTile(tilepile.sharedSerials[port])
            myTile.assignAddress(0)
        #   myTile.blank()     # Not implemented in LSRealTile
            myTile.setColor(0)  # A TEMPORARY hack
            
        for port in tilepile.lsMatrix:
            for addr in tilepile.lsMatrix[port]:
                print("Port is: " + repr(port) + " Address is: " + repr(addr))
                myTile = LSRealTile(tilepile.sharedSerials[port])
                myTile.assignAddress(addr)
                myTile.demo(1)
                row=int(input("Which row?: "))
                row = row-1
                col=int(input("Which col?: "))
                col = col-1
                thisTile = (row, col, port, addr)
                print("Added this tile: " + str(thisTile))
                config.append(thisTile)
                myTile.setColor(0)

        return config
    
    tilepile = lsOpen()
    
    print("\nLightsweeper Configuration utility")

    # serial ports are COM<N> on windows, /dev/xyzzy on Unixlike systems
    availPorts = list(tilepile.lsMatrix)

    print("Available serial ports:" + str(availPorts))
    
    totaltiles = 0
    for port in tilepile.lsMatrix:
        totaltiles += len(tilepile.lsMatrix[port])

    if len(availPorts) > 0:  # default to the first port in the list
        defaultPort = availPorts[0]

    config = pickFile("\nEnter the name of the configuration you would like to edit [NEW]: ")

    if config is None:                              # Start a new configuration
        config = interactiveConfig()

    elif config.cells is 0:     # Start a new configuration with a pre-existing filename
        config = interactiveConfig(config)

    else:                       # Load an existing configuration for editing
        print("\nThis is the configuration saved in " + config.fileName + ":\n")
        config.printConfig()

        print("\nBut the editing code is not here yet. Sorry.")


    print("\nThis is the configuration: ")
    config.printConfig()
        

    fileName = input("\nPlease enter a filename for this configuration (or blank to not save): ")
    if fileName == "":
        print("OK, not saving this configuration")
    else:
        with open(fileName, 'w') as configFile:
            json.dump(config, configFile, sort_keys = True, indent = 4,)
        print("\nYour configuration was saved in " + fileName)

    input("\nDone - Press the Enter key to exit") # keeps double-click window open


if __name__ == '__main__':

    main()


