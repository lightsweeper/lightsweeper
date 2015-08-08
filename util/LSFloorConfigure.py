#!/usr/bin/python3

import os

from lightsweeper.lsconfig import LSFloorConfig
from lightsweeper.lsconfig import userSelect
from lightsweeper.lsconfig import interactiveConfig
from lightsweeper.lsconfig import pickFile
from lightsweeper.lsconfig import FileExistsError
from lightsweeper.lsconfig import yesNO
from lightsweeper import lsconfig

def main():

    print("\nLightsweeper Configuration utility")

    conf = lsconfig.readConfiguration()
    try:
        floorDir = conf["FLOORSDIR"]
    except KeyError:
        floorDir = conf["CONFIGDIR"]

    floorFiles = list(filter(lambda ls: ls.endswith(".floor"), os.listdir(floorDir)))

    if len(floorFiles) is 0:
        config = None
    else:
        choices = floorFiles
        NEW = "New Floor"
        choices.insert(0, NEW)
        selection = userSelect(choices, "\nWhich floor configuration would you like to edit?")
        if selection == NEW:
            config = None
        else:
            fileName = selection
            absFloorConfig = os.path.abspath(os.path.join(floorDir, fileName))
            try:
                config = LSFloorConfig(absFloorConfig)
            except lsconfig.CannotParseError as e:
                print("\nCould not parse the configuration at {:s}: {:s}".format(absFloorConfig, e))

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


