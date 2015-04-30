#!/usr/bin/python3

from LSRealTile import LSOpen
from LSRealTile import LSRealTile

from lsconfig import LSFloorConfig
from lsconfig import userSelect

def main():
# Warning: spaghetti code ahead


    def validateRowCol(numTiles, rowsOrCols, isVirtual=True):
        try:
            rowsOrCols = int(rowsOrCols)
        except:
            print("You must enter a whole number!")
            return False
        if numTiles is 0:       # Virtual floor
            return True
        if isVirtual is False:
            if rowsOrCols > numTiles:
                print("There are only " + repr(numTiles) + " tiles!")
                return False
        return True

    def pickRowCol(cells, message, isVirtual=True):
        x = input(message)
        while validateRowCol(cells, x, isVirtual) is False:
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
                    floorConfig = LSFloorConfig()
                    floorConfig.fileName = fileName
                    return floorConfig
                else:
                    return pickFile(message)
            try:
                return LSFloorConfig(fileName)
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

        totaltiles = 0

        isLive = True
        try:
            tilepile = LSOpen()
        except IOError as e:
            print("Not using serial because: {:s}".format(str(e)))
            isLive = False

        if isLive is not False:
            # serial ports are COM<N> on windows, /dev/xyzzy on Unixlike systems
            availPorts = list(tilepile.lsMatrix)

            print("Available serial ports: " + str(availPorts))
    
            for port in tilepile.lsMatrix:
                totaltiles += len(tilepile.lsMatrix[port])

#            if len(availPorts) > 0:  # default to the first port in the list
#                defaultPort = availPorts[0]

            # It's the little details that count
            question = "Would you like this to be a virtual floor?"
            if totaltiles is 0:
                isVirtual = YESno(question)
            else:
                isVirtual = yesNO(question)
        else:
            isVirtual = True


        if isVirtual is True:
            print("\nConfiguring virtual Lightsweeper floor...")
        else:
            print("\nConfiguring real floor...")

        rows = int(pickRowCol(totaltiles, "\nHow many rows do you want?: "))
        
        if isVirtual is True or totaltiles is 0:
            cols = int(pickRowCol(totaltiles, "How many columns do you want?: ", isVirtual))
        else:
            cols = int(totaltiles/rows)

        print("OK, you have a floor with " + repr(rows) + " by " + repr(cols)  + " columns")

        if isVirtual is True:
            config = LSFloorConfig(rows=rows, cols=cols)
            config.makeVirtual()
        else:
            if totaltiles is not 0:
                config = LSFloorConfig(rows=rows, cols=cols)
                configWithKeyboard(config, tilepile)

        return config


    print("\nLightsweeper Configuration utility")

  #  config = pickFile("\nEnter the name of the configuration you would like to edit [NEW]: ")
    config = None

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
        config.writeConfig(fileName)

    input("\nDone - Press the Enter key to exit") # keeps double-click window open


if __name__ == '__main__':

    main()


