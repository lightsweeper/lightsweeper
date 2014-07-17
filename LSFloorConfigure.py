#!/usr/bin/env python


import os
import serial
import pickle

def serial_ports():
    """
    Returns a generator for all available serial ports
    """
    if os.name == 'nt':
        # windows
        for i in range(256):
            try:
                s = serial.Serial(i)
                s.close()
                yield 'COM' + str(i + 1)
            except serial.SerialException:
                pass
    else:
        # unix
        for port in list_ports.comports():
            yield port[0]

# prints the list of 4-tuples
def printConfig(config):
    print("The configuration has " + repr(len(config)) + " entries:")
    for cell in config:
        print(repr(cell))

def main():
    print("\nLightsweeper Configuration utility")

    # serial ports are COM<N> on windows, /dev/xyzzy on Unixlike systems
    availPorts = list(serial_ports())
    print("Available serial ports:" + str(availPorts))
    defaultPort = "COM8"
    if len(availPorts) > 0:  # default to the first port in the list
        defaultPort = availPorts[0]
        
    pickleName = input("\nIf you have an existing configuration to edit, enter the name here: ")
    if "" == pickleName:
        print("\nStarting a new configuration from scratch.")
        rows = input("\nEnter the number of rows in your floor:")
        rows = int(rows) # we need a number
        cols = input("Enter the number of columns in your floor:")
        cols = int(cols) # we need a number

        print("OK, you have a floor with " + repr(rows) + " by " + repr(cols)  + " columns")

        config = []

        for row in range(rows):
            for col in range(cols):
                print("\nRow=" + repr(row) + " column=" + repr(col))
                port = input("Enter the port name (just enter to use " + defaultPort + "): ")
                if port == "":
                    port = defaultPort
                    #print("Using port " + port)
                address = input("Enter the tile address: ")
                address = int(address)
                thisTile = (row, col, port, address)
                print("Added this tile: " + str(thisTile))
                config.append(thisTile)

        print("\nThis is the configuration: ")
        #print(repr(config))
        printConfig(config)
        
        pickleName = input("\nPlease enter a filename for this pickled configuration (or blank to not save): ")
        if pickleName == "":
            print("OK, not saving this configuration")
        else:
            configFile = open(pickleName, 'wb')
            pickle.dump(config, configFile)
            configFile.close()
            print("\nYour configuration was saved in " + pickleName)
                

    else:
        configFile = open(pickleName, 'rb')
        config = pickle.load(configFile)
        configFile.close()

        print("\nThis is the configuration saved in " + pickleName + ":\n")
        #print(repr(config))
        printConfig(config)


        print("\nBut the editing code is not here yet. Sorry.")

    input("\nDone - Press the Enter key to exit") # keeps double-click window open


if __name__ == '__main__':

    main()


