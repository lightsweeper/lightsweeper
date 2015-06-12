#!/usr/bin/python3

from lsapi.lsconfig import LSFloorConfig
from lsapi.lsconfig import userSelect
from lsapi.lsconfig import interactiveConfig
from lsapi.lsconfig import pickFile
from lsapi.lsconfig import FileExistsError
from lsapi.lsconfig import yesNO

def main():

    print("\nLightsweeper Configuration utility")

    config = pickFile("\nEnter the name of the configuration you would like to edit or leave blank to create a new file: ")
 #   config = None

    if config is None:                              # Start a new configuration
        config = interactiveConfig()

    elif config.cells is 0:     # Start a new configuration with a pre-existing filename
        config = interactiveConfig(config)

    else:                       # Load an existing configuration for editing
        print("\nThis is the configuration saved in " + config.fileName + ":\n")
        config.printConfig()

        print("\nBut the editing code is not here yet. Sorry.")
        exit()


    print("\nThis is the configuration: ")
    config.printConfig()

    if config.fileName is None:
        fileName = input("\nPlease enter a filename for this configuration (or blank to not save): ")
    else:
        fileName = config.fileName
    if fileName == "":
        print("OK, not saving this configuration.")
    else:
        try:
            config.writeConfig(fileName)
        except FileExistsError:
            if yesNO("{:s} already exists, would you like to overwrite it?".format(config.fileName)) is True:
                config.writeConfig(fileName, overwrite=True)
            else:
                print("OK, not saving any changes to this configuration.")
            

    input("\nDone - Press the Enter key to exit") # keeps double-click window open


if __name__ == '__main__':

    main()


