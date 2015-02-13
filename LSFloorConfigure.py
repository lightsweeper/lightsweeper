#!/usr/bin/env python

import os
import serial
import json
from collections import defaultdict
from LSRealTile import lsOpen
from LSRealTile import LSRealTile


class lsFloorConfig:
    """
        This class implements methods to read/write and otherwise
        manipulate Lightsweeper floor configurations.

        Attributes:
            fileName (str): The name of the config file on disk
            cells (int):    The number of cells in the lightsweeper matrix.
            rows (int):     The number of rows in the lightsweeper matrix.
            cols (int):     The number of columns in the lightsweeper matrix.
            board (dict):   A dictionary of dictionaries sorted by row and column, each
                            containing a tuple of the corresponding tile's port and address
            config (list):  A list of tuples of the form (row, col, port, address)
    """

    class FileDoesNotExistError(IOError):
        """ Custom exception returned when the config file is non-existant. """
        pass

    class CannotParseError(IOError):
        """ Custom exception returned when the config file is present but cannot be parsed. """
        pass


    def __init__(self, configFile=None, rows=None, cols=None):

        if configFile is not None:
            if configFile.endswith(".floor") is False:
                configFile += ".floor"
            self.fileName = configFile
            try:
                self.config = self.loadConfig(configFile)
            except self.FileDoesNotExistError as message:
                print(message)
                raise
            except IOError as message:
                print(message)
                raise
            except self.CannotParseError:
                print(message)
                raise
            self._parseConfig(self.config)



    def loadConfig(self, fileName):
        if os.path.exists(fileName) is True:
            if os.path.isfile(fileName) is not True:
                raise IOError(fileName + " is not a valid floor config file!")
        else:
            raise self.FileDoesNotExistError(fileName + " does not exist!")
        try:
            with open(fileName) as configFile:
                return json.load(configFile)
        except:
            raise self.CannotParseError("Could not parse " + fileName + "!")
        print("Board mapping loaded from " + fileName)


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


# prints the list of 4-tuples
def printConfig(config):
    print("The configuration has " + repr(len(config)) + " entries:")
    for cell in config:
        print(repr(cell))

def main():
    
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
        
    def pickgeom(numTiles, rows):
        if rows > numTiles:
            print("There are only " + repr(numTiles) + " tiles!")
            return False
        else:
            return True

    def tryforfile():
        fileName = input("\nEnter the name of the configuration you would like to edit [NEW]: ")
        if fileName == "" or fileName == "NEW":
            return None
        else:
            try:
                return lsFloorConfig(fileName)
            except:
                return tryforfile()

    try:   
        config = tryforfile()
    except:
        print("Could not read " + config.fileName)
        exit()
    if config is None:
        print("\nStarting a new configuration from scratch.")
        rows = int(input("\nHow many rows do you want?: "))
        while pickgeom(totaltiles, rows) is False:
            rows = int(input("\nHow many rows do you want?: "))
        cols = int(totaltiles/rows)

        print("OK, you have a floor with " + repr(rows) + " by " + repr(cols)  + " columns")

        config = []

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

        print("\nThis is the configuration: ")
        #print(repr(config))
        printConfig(config)
        
        fileName = input("\nPlease enter a filename for this configuration (or blank to not save): ")
        if fileName == "":
            print("OK, not saving this configuration")
        else:
            with open(fileName, 'w') as configFile:
                json.dump(config, configFile, sort_keys = True, indent = 4,)
            print("\nYour configuration was saved in " + fileName)
                

    else:

        print("\nThis is the configuration saved in " + config.fileName + ":\n")
        printConfig(config.config)


        print("\nBut the editing code is not here yet. Sorry.")

    input("\nDone - Press the Enter key to exit") # keeps double-click window open


if __name__ == '__main__':

    main()


