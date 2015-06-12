#!/usr/bin/env python3
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
from lsapi.LSRealTile import LSOpen
from lsapi.LSRealTile import LSRealTile
from lsapi.LSRealTile import EE_ADDR

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

    lsls = LSOpen()

    if lsls.numPorts is 0:
        print("Please attach some physical Lightsweeper tiles!")
        exit(1)

    if args['-p']:
        if args['-p'] not in lsls.availPorts():
            print(args['-p'] + " does not exist!")
            exit()
        if args['-p'] not in lsls.lsMatrix.keys():
            print(args['-p'] + " does not appear to have any lightsweepers attached to it.")
            exit()
        com = args['-p']
    else:
        if args['-a']:
            pass
        else:
            com = lsls.selectPort()
        
# Select address
    if args['-a']:
        address = int(args['-a'])
        if address is 0:    # 0 is the global address
            comList = list(lsls.validPorts())
        else:
            comList = list()
        for key, val in lsls.lsMatrix.items():
            if address in val:
                comList.append(key)
        if len(comList) is 0:
            print("There is no tile with address " + repr(address) + ".")
            exit()
        if len(comList) is 1:
            com = comList[0]
        if len(comList) > 1:
            if args['-p']:
                com = args['-p']
            else:
                com = lsls.selectPort(comList)
        print("Connecting to tile at address: " + str(address) + "...")
    else:
        if args['-p']:
            print("No address specified, using address 0 (all tiles).")
            address = 0
            print("To target a tile at a specific address use the -a option...")
        else:
            print("Available addresses: " + repr(lsls.lsMatrix.get(com)))
            address = 0
            inaddr = input("What tile address would you like to control [0]: ")
            if inaddr:
                address = int(inaddr)
            
    print("Using communications port: " + repr(com) + "...")
            
    theSerial=lsls.lsSerial(com)

    myTile = LSRealTile(lsls.sharedSerials[com])    
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
            myTile.flip()
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
