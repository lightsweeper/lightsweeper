from collections import defaultdict
import os
import json
import numbers



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

class LSFloorConfig:
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
            This function turns the current LSFloorConfig object into a virtual floor
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

    def containsVirtual(self):
        """
            This function returns true if the configuration contains any
            virtual tiles.
        """
        for cell in self.config:
            if "virtual" in cell[2]:
                return True
        return False

    def containsReal(self):
        """
            This function returns true if the configuration contains any
            real tiles.
        """
        for cell in self.config:
            if "virtual" not in cell[2]:
                return True
        return False

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
        floorFiles = list(filter(lambda ls: ls.endswith(".floor"), os.listdir("./")))
        
        if len(floorFiles) is 0:
            raise IOError("No floor configuration found. Try running LSFloorConfigure.py")
        elif len(floorFiles) is 1:
            fileName = floorFiles[0]
        else:
            print("\nFound multiple configurations: \n")
            fileName = userSelect(floorFiles, "\nWhich floor configuration would you like to use?")
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

def userSelect(selectionList, message="Select an option from the list:"):
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
    print("\r")
    for optNum, optName in options:
        print("  [{:d}] {:s}".format(optNum, optName))
    return pick("{:s} ".format(message))
