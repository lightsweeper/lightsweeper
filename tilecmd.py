#!/usr/bin/python3
'''
tilecmd.py - a command line interface to LSRealTile.py

Usage:
    tilecmd.py [options] [blank|locate|demo|flip|reset]
    tilecmd.py [options] set digit <digit>
    tilecmd.py [options] set color <color>
    tilecmd.py [options] set address <address>
    tilecmd.py -h | --help

Options:
    -p <port>           Set the communications port to <port>
    -a <address>        Communicate with tile at address <address>
    -h --help           Display this documentation
    -i --interactive    Enter interactive mode

Tile commands:
    blank       Blanks the tile's display
    locate      Causes the tile to display its address
    demo        Causes the tile to enter demo mode
    flip        Flips the tile's display
    reset       Causes the tile to reset
'''
from docopt import docopt
from LSRealTile import *

if __name__ == '__main__':
    args = docopt(__doc__)
    
    if not any(args.values()):  # Program was called with no arguments
        print(__doc__)          #   display help
        exit()
    
# Enumerate tile commands, probably a better way to do this
    tile_command = None
    
    if args['set']:
        tile_command = 'set'
        if args['digit']:
            set_command = ('digit', int(args['<digit>']))
        if args['color']:
            set_command = ('color', int(args['<color>']))
        if args['address']:
            set_command = ('address', int(args['<address>']))
    
    if args['blank']:
        tile_command = 'blank'
    elif args['locate']:
        tile_command = 'locate'
    elif args['demo']:
        tile_command = 'demo'
    elif args['flip']:
        tile_command = 'flip'
    elif args['reset']:
        tile_command = 'reset'


  # Select com port
    com = LSRealTile.selectport()
        
  # Select address
    address = LSRealTile.selectaddr()

  # Create serial object
    theSerial=LSRealTile.lsOpen(com)

  # Bind tile object to serial object
    myTile = LSRealTile(theSerial)

  # Set the current tile's address
    myTile.assignAddress(address)

    if theSerial != None:
        if tile_command == None:
            print("No tile command provided, entering interactive mode...")
            raise NotImplementedError() # No interactive mode
        if tile_command == 'blank':
            print("Blanking tile at address " + str(address))
         #   myTile.blank()     # Not implemented in LSRealTile
            myTile.setColor(0)  # A TEMPORARY hack
        elif tile_command == 'locate':
            print("Setting locate mode on for the tile at address " + str(address))
            myTile.locate()
        elif tile_command == 'demo':
            print("Setting demo mode on for the tile at address " + str(address))
            myTile.demo(1)  # Argument (1) is used off-label...
        elif tile_command == 'flip':
            if myTile.getAddress() == 0:
                print("Please specify an address other than 0.")
                exit()
            print("Flipping tile at address " + str(address))
            # myTile.flip() # Also myTile.unflip() -- not implemented nicely
            # Perm flip:
            tile_config = myTile.eepromRead(EE_CONFIG)
            flip_config = ord(tile_config) ^ STATUS_FLIP_MASK
            myTile.eepromWrite(EE_CONFIG,flip_config)
            myTile.reset()
        elif tile_command == 'reset':
            print("Resetting tile at address " + str(address))
            myTile.reset()
        elif tile_command == 'set':
            if set_command[0] == 'digit':
                myTile.setDigit(set_command[1])
            if set_command[0] == 'color':
                myTile.setColor(set_command[1])
            if set_command[0] == 'address':
                newaddr = set_command[1]
                if (newaddr < 0 or newaddr > 254):
                    print("Supplied address (" + str(newaddr) + ") is out of bounds!")
                    exit()
                if (newaddr == 0):
                    print("Setting tile address to random value")
                    myTile.setRandomAddress()
                else:
                    print("Setting new tile address: " + str(newaddr))
                    myTile.eepromWrite(EE_ADDR, newaddr)
                    myTile.reset()
        else:
            raise NotImplementedError()
