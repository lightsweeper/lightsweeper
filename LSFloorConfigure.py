#!/usr/bin/env python


import os
import serial
import json
from LSRealTile import lsOpen
from LSRealTile import LSRealTile

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
        
    fileName = input("\nIf you have an existing configuration to edit, enter the name here: ")
    if "" == fileName:
        print("\nStarting a new configuration from scratch.")
        rows = int(input("\nHow many rows do you want?: "))
        while pickgeom(totaltiles, rows) is False:
            rows = int(input("\nHow many rows do you want?: "))
        cols = int(totaltiles/rows)
            
        

        print("OK, you have a floor with " + repr(rows) + " by " + repr(cols)  + " columns")

        config = []
        
        print("Blanking all tiles.")
        for port in tilepile.lsMatrix:
            myTile = LSRealTile(tilepile.lsSerial(port))
            myTile.assignAddress(0)
        #   myTile.blank()     # Not implemented in LSRealTile
            myTile.setColor(0)  # A TEMPORARY hack
            
        for port in tilepile.lsMatrix:
            for addr in tilepile.lsMatrix[port]:
                print("Port is: " + repr(port) + " Address is: " + repr(addr))
                myTile = LSRealTile(tilepile.lsSerial(port))
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
 
 # Old code:               
#        for row in range(rows):
#            for col in range(cols):
#                print("\nRow=" + repr(row) + " column=" + repr(col))
#                port = input("Enter the port name (just enter to use " + defaultPort + "): ")
#                if port == "":
#                    port = defaultPort
#                    #print("Using port " + port)
#                address = input("Enter the tile address: ")
#                address = int(address)
#                thisTile = (row, col, port, address)
#                print("Added this tile: " + str(thisTile))
#                config.append(thisTile)

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

        print("\nThis is the configuration saved in " + fileName + ":\n")
        with open(fileName) as configFile:    
            config = json.load(configFile)
        printConfig(config)


        print("\nBut the editing code is not here yet. Sorry.")

    input("\nDone - Press the Enter key to exit") # keeps double-click window open


if __name__ == '__main__':

    main()


