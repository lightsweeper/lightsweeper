#!/usr/bin/python3
import os
import json
import numbers
from collections import defaultdict
from LSRealTile import LSOpen
from LSRealTile import LSRealTile

class FileDoesNotExistError(IOError):
    """ Custom exception returned when the config file is non-existant. """
    pass

class FileExistsError(IOError):
    """
        Custom exception returned by writeConfig() when the config file is already present
        and overwrite=False
    """
    pass

class CannotParseError(IOError):
    """ Custom exception returned when the config file is present but cannot be parsed. """
    pass

class InvalidConfigError(Exception):
    """ Custom exception returned when the configuration is not valid. """
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

    fileName = None
    cells = 0
    rows = 0
    cols = 0
    config = list()
    board = defaultdict(lambda: defaultdict(int))

    def __init__(self, configFile=None, rows=None, cols=None):

        if configFile is not None:
            self.fileName = self._formatFileName(configFile)
            try:
                self.loadConfig(self.fileName)
            except FileDoesNotExistError as e:
                if rows is not None and cols is not None:
                    self.config = self._createVirtualConfig(rows, cols)
                else:
                    print(e)
                    raise
            finally:
                self.makeFloor()
        else:
            self.rows = rows
            self.cols = cols
    
    def makeFloor(self):
        """
            This function attempts to parse the data in config and populate the rest of the object
        """
        self.cells = self.rows*self.cols
        self._parseConfig(self.config)
    
    def makeVirtual(self):
        """
            This function turns the current lsFloorConfig object into a virtual floor
        """
        self.cells = self.rows * self.cols
        self.config = self._createVirtualConfig(self.rows, self.cols)

    def loadConfig(self, fileName):
        """
            This function attempts to load the floor configuration at fileName

            Returns:
                True                    if the load was succesful

            Raises:
                IOError                 if fileName is a directory
                FileDoesNotExistError   if fileName is non-existent
                CannotParseError        if the file can not be parsed
        """
        if os.path.exists(fileName) is True:
            if os.path.isfile(fileName) is not True:
                raise IOError(fileName + " is not a valid floor config file!")
        else:
            raise FileDoesNotExistError(fileName + " does not exist!")
        try:
            with open(fileName) as configFile:
                self.config = json.load(configFile)
        except Exception as e:
            print(e)
            raise CannotParseError("Could not parse " + fileName + "!")
        finally:
            print("Board mapping loaded from " + fileName)
            self._parseConfig(self.config)
            return True


    # prints the list of 4-tuples
    def printConfig(self):
        """
            This function prints the current configuration
        """
      #  self._validate()
        print("The configuration has {:d} entries:".format(len(self.config)))
      #  print(self.cells, self.rows, self.cols) # Debugging
        for cell in self.config:
            print(repr(cell))


    def writeConfig(self, fileName = None, overwrite=False):
        """
            This function attempts to write the current configuration to disk

            Raises:
                IOError                 if fileName is not set
                FileExistsError         if fileName already exists and overwrite is False
        """
        if fileName is not None:
            self.fileName = self._formatFileName(fileName)
        elif self.fileName is None:
            raise IOError("fileName must be set. Try writeConfig(fileName).")
        if os.path.exists(self.fileName) is True:
            if overwrite is not True:
                raise FileExistsError("Cannot overwrite {:s} (try setting overwrite=True).".format(fileName))
        with open(self.fileName, 'w') as configFile:
            json.dump(self.config, configFile, sort_keys = True, indent = 4,)
        if overwrite is True:
            print("\nOverwriting {:s}...".format(fileName))
        else:
            print("\nYour configuration was saved in {:s}".format(self.fileName))


    def selectConfig(self):
        """
            This function looks in the current directory for .floor files and prompts the user to
            select one, then loads it into self. 
            
            Raises:
                IOError                 if no .floor files are found
        """
        try:
            floorFiles = list(filter(lambda ls: ls.endswith(".floor"), os.listdir("./")))
        except:
            raise IOError("No floor configuration found. Try running LSFloorConfigure.py")
        if len(floorFiles) is 1:
            fileName = floorFiles[0]
        else:
            print("\nFound multiple configurations: \n")
            fileName = userSelect(floorFiles, "\nWhich floor configuration would you like to use? ")
        self.loadConfig(fileName)

    def _formatFileName(self, fileName):
        if fileName.endswith(".floor") is False:
            fileName += ".floor"
        return fileName
        
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
        self.cells = 0
        self.rows = 0
        self.cols = 0
        for (row, col, port, addr) in config:
            self.cells += 1
            if row >= self.rows:
                self.rows = row + 1
            if col >= self.cols:
                self.cols = col + 1
            self.board[row][col] = (port, addr)
        self._validate()

    def _validate(self):
        if self.rows * self.cols is not self.cells:
            raise InvalidConfigError("Configuration is not valid.")

def userSelect(selectionList, message="Select an option from the list: "):
    def checkInput(selection):
        options = dict(enumerate(selectionList))
        if selection in options.values():
            return selection
        try:
            selection = int(selection)
        except:
            return False
        if selection in options.keys():
            return options.get(selection)
        return False
        
    def pick(msg):
        x=str()
        while checkInput(x) is False:
            x = input(msg)
        return checkInput(x)
        
    options = enumerate(selectionList)
    for optNum, optName in options:
        print("[{:d}] {:s}".format(optNum, optName))
    return pick(message)
    


def main():
# Warning: spaghetti code ahead


    def validateRowCol(numTiles, rowsOrCols):
        try:
            rowsOrCols = int(rowsOrCols)
        except:
            print("You must enter a whole number!")
            return False
        if numTiles is 0:       # Virtual floor
            return True
        if rowsOrCols > numTiles:
            print("There are only " + repr(numTiles) + " tiles!")
            return False
        return True

    def pickRowCol(cells, message):
        x = input(message)
        while validateRowCol(cells, x) is False:
            x = input(message)
        return x

    def YESno(message, default="Y"):
        yesses = ("yes", "Yes", "YES", "y", "Y")
        nos = ("no", "No", "NO", "n", "N")
        if default in yesses:
            answer = input("{:s} [Y/n]: ".format(message))
        elif default in nos:
            answer = input("{:s} [y/N]: ".format(message))
        else:
            raise ValueError("Default must be some form of yes or no")
        if answer is "":
            answer = default
        if answer in yesses:
            return True
        elif answer in nos:
            return False
        else:
            print("Please answer Yes or No.")
            return YESno(message)

    def yesNO(message, default="N"):
        return YESno(message, default)

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
            except Exception as e:
                print(e)
                return pickFile(message)

    def configWithKeyboard(floorConfig, tilepile):
        config = list()
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
                row=int(pickRowCol(floorConfig.cells, "Which row?: "))
                row = row-1
                col=int(pickRowCol(floorConfig.cells, "Which col?: "))
                col = col-1
                thisTile = (row, col, port, addr)
                print("Added this tile: " + str(thisTile))
                config.append(thisTile)
                myTile.setColor(0)
        floorConfig.config = config
        return floorConfig



    def interactiveConfig (config = None):

        if config is None:
            print("\nStarting a new configuration from scratch.")
            config = []
        else:
            print("Configuring {:s}...".format(config.fileName))

        tilepile = LSOpen()

        # serial ports are COM<N> on windows, /dev/xyzzy on Unixlike systems
        availPorts = list(tilepile.lsMatrix)

        print("Available serial ports: " + str(availPorts))
    
        totaltiles = 0
        for port in tilepile.lsMatrix:
            totaltiles += len(tilepile.lsMatrix[port])

        if len(availPorts) > 0:  # default to the first port in the list
            defaultPort = availPorts[0]

        # It's the little details that count
        question = "Would you like this to be a virtual floor?"
        if totaltiles is 0:
            isVirtual = YESno(question)
        else:
            isVirtual = yesNO(question)

        if isVirtual is True:
            print("\nConfiguring virtual Lightsweeper floor...")
        else:
            print("\nConfiguring real floor...")


        rows = int(pickRowCol(totaltiles, "\nHow many rows do you want?: "))
        
        if isVirtual is True or totaltiles is 0:
            cols = int(pickRowCol(totaltiles, "How many columns do you want?: "))
        else:
            cols = int(totaltiles/rows)

        print("OK, you have a floor with " + repr(rows) + " by " + repr(cols)  + " columns")

        if isVirtual is True:
            config = lsFloorConfig(rows=rows, cols=cols)
            config.makeVirtual()
        else:
            if totaltiles is not 0:
                config = lsFloorConfig(rows=rows, cols=cols)
                configWithKeyboard(config, tilepile)

        return config


    print("\nLightsweeper Configuration utility")

    config = pickFile("\nEnter the name of the configuration you would like to edit [NEW]: ")

    if config is None:                              # Start a new configuration
        config = interactiveConfig()

    elif config.cells is 0:     # Start a new configuration with a pre-existing filename
        config = interactiveConfig(config)
        ourfile = config.fileName

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
        config.writeConfig(fileName)

    input("\nDone - Press the Enter key to exit") # keeps double-click window open


if __name__ == '__main__':

    main()


