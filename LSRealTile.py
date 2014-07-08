#!/usr/bin/env python

# the API is the base class
from LSTileAPI import *

#from serial import *
import serial
#from struct import *

# imports for testing
import os
import time

# TODO - perhaps better to use hexlify and unhexlify
#from HexByteConversion import *

# these constants copied from LSTileAPI.h

LS_LATCH = 0x10       # refresh display from queue - usually address 0
LS_CLEAR = LS_LATCH+1 # blanks the tile
LS_RESET = LS_LATCH+2 # reboot

LS_RESET_ADC = (LS_LATCH+3)    # reset ADC statistics
LS_CALIBRATE_ON = (LS_LATCH+4) # reset ADC statistics and starts calibration
LS_CALIBRATE_OFF =(LS_LATCH+5) # ends calibration, writes ADC stats to EEPROM

# one byte commands defining whether tile is rightside up or not
# the installation may be configured upside down at EEPROM address EE_CONFIG
FLIP_ON  =    (LS_LATCH+8)   # temporary command to flip display upside down
FLIP_OFF =    (LS_LATCH+9)   # restore display rightside up

# seven segment display commands with one data byte
SET_COLOR      = 0x20          # set the tile color - format TBD
SET_SHAPE      = (SET_COLOR+1) # set which segments are "on" - abcdefg-
SET_TRANSITION = (SET_COLOR+2) # set transition at the next refresh - format TBD
# seven segment display commands with three data bytes
SET_TILE       = (SET_COLOR+3) #/ set the color, segments, and transition

# one byte query commands returning one byte
ADC_NOW    = 0x40          # unsigned 8 bits representing current ADC
ADC_MIN    = (ADC_NOW + 1) # unsigned 8 bits representing minimum ADC
ADC_MAX    = (ADC_NOW + 2) # unsigned 8 bits representing maximum ADC
ADC_THRESH = (ADC_NOW + 3) # unsigned 8 bits representing sensor threshold
SENSOR_NOW = (ADC_NOW + 4) # unsigned 8 bits representing sensor tripped with history

TILE_STATUS = (ADC_NOW + 8) # returns bit mapped status
# defined bit masks
STATUS_FLIP_MASK =   0x80 # set if segments flipped
STATUS_ERR_MASK  =   0x40 # set if error, and read by RETURN_ERRORS
STATUS_CAL_MASK  =   0x20 # set if currently calibrating

TILE_VERSION = (ADC_NOW + 9) # format TBD - prefer one byte
# The Hardware version may be read and set at the EE_HW address in EEPROM

# EEPROM read is command and one byte of address
EEPROM_READ  =   0x60
# EEPROM write is command, one address byte, and one data byte
EEPROM_WRITE =   (EEPROM_READ+1)
# Defined EEPROM addresses:
EE_ADDR   =  0 # 0 - tile address in top five bytes
EE_CONFIG =  1 # 1 - tile configuration
#       0x80 - AKA STATUS_FLIP_MASK - installed upside-down
#       TBD - color mapping
EE_HW      = 2  # 2 - tile hardware version
#       0 - dev board
#       1 - 3 proto boards
#       2 - 48 tile boards
EE_ADC_MAX  = 3 # High ADC value from calibration - 8 bits of 10 - not sensitive enough?
EE_ADC_MIN  = 4 # Low ADC value from calibration - 8 bits of 10 - not sensitive enough?
EE_PUP_MODE = 5 # Powerup/Reset mode - command from 0 to 0X0F
#          commands that do not work result in the NOP_MODE

# one byte error system commands
MAX_ERRORS    =  4    # number of command errors remembered in error queue
ERROR_CMD     =  0x78 # error test command
RETURN_ERRORS =  (ERROR_CMD+1) # returns the last MAX_ERRORS errors in queue
        # Most recent errors are returned first
        # Clears error queue and STATUS_ERR_MASK
CLEAR_ERRORS  = (ERROR_CMD+2)  # not really needed, but nearly free



### Implementation of the Lightsweeper low level API to a ATTiny tile
class LSRealTile(LSTileAPI):
    def __init__(self, sharedSerial, row=0, col=0):
        super().__init__(row, col)
        self.mySerial = sharedSerial
        # cmdNargs is address + command + N optional bytes

    def destroy(self):
        return

    # set immediately or queue this color in addressed tiles
    def setColor(self, color):
        cmd = SET_COLOR
        self.__tileWrite([cmd, color])

    def setShape(self, shape):
        cmd = SET_SHAPE
        self.__tileWrite([cmd, shape])

    def setTransition(self, transition):
        cmd = SET_TRANSITION
        self.__tileWrite([cmd, shape])

    def set(self,color=0, shape=0, transition=0):
        raise NotImplementedError()
        if (color != 0):
            self.setColor(color)
        if (shape != 0 ):
            self.setShape(shape)
        if(transition != 0):
            self.setTransition(transition)
        return

    def update(self,type):
        raise NotImplementedError()
        if (type == 'NOW'):
            return
        elif (type == 'CLOCK'):
            return
        elif (type == 'TRIGGER'):
            return
        else:
            return

    def version(self):
        # send version command
        cmd = TILE_VERSION
        self.__tileWrite([cmd])
        # return response
        thisRead = self.mySerial.read(8)
        val = self.__tileRead()
        return val
    
    # eeAddr and datum from 0 to 255
    def eepromWrite(self,eeAddr,datum):
        cmd = EEPROM_WRITE
        self.__tileWrite([cmd, eeAddr, datum])

    # eeAddr from 0 to 255
    def eepromRead(self,eeAddr):
        # send read command
        cmd = EEPROM_READ
        self.__tileWrite([cmd, eeAddr])
        # return response
        thisRead = self.mySerial.read(8)
        val = self.__tileRead()
        return val

    # read any saved errors
    def errorRead(self):
        # send read command
        cmd = RETURN_ERRORS
        self.__tileWrite([cmd])
        # return response
        thisRead = self.mySerial.read(8) # expect MAX_ERRORS but be safe
        val = self.__tileRead()
        return val

    def blank(self):
        raise NotImplementedError()
        self.setColor('white')
        return

    # send mode command that displays stuff
    def locate(self):
        cmd = 6
        self.__tileWrite([cmd])

    def demo (self, seconds):
        cmd = 3
        self.__tileWrite([cmd])

    def setAnimation(self):
        raise NotImplementedError()

    def flip(self):
        cmd = FLIP_ON  # wire API also has FLIP_OFF
        self.__tileWrite([cmd])

    def unflip(self):
        cmd = FLIP_OFF
        self.__tileWrite([cmd])

    def status(self):
        raise NotImplementedError()
        return

    def reset(self):
        versionCmd = LS_RESET
        self.__tileWrite([versionCmd])
        # return response in case tile spits stuff at reset
        thisRead = self.mySerial.read(8)
        val = self.__tileRead()


    # write any queued colors or segments to the display
    def latch(self):
        latchCmd = LS_LATCH
        self.__tileWrite([latchCmd])

    def unregister(self):
        raise NotImplementedError()
        return

    # assignAddress and getAddress are in LSTileAPI base class

    def calibrate(self):
        raise NotImplementedError()
        return

    def read(self):
        raise NotImplementedError()
        return self._getButtonState()

    def flushQueue(self):
        raise NotImplementedError()

    # write a command to the tile
    # minimum args is command by itself
    def __tileWrite(self, args):
        cmdLen = len(args)
        # insert address byte plus optional arg count
        #addr = ord(self.address)  # in case input was a char
        addr = self.address
        addr = addr + cmdLen - 1  # command is not counted
        args.insert(0, addr)
        count = self.mySerial.write(args)
        writeStr = (' '.join(format(x, '#02x') for x in args))
        print("0x%x command wrote %d bytes: %s " % (args[1], count, writeStr))
        #print(' '.join(format(x, '#02x') for x in args))


    # read from the tile
    def __tileRead(self):
        thisRead = self.mySerial.read(8)
        if len(thisRead) > 0:
            #print("Received " + thisRead.ToHex())
            print ("Received: " + ''.join(format(x, '02x') for x in thisRead))

            new_str = "Received: " 
            #for i in thisRead:
                #new_str += "0x%s " % (i.encode('hex'))
                #new_str += "0x%s " % (i.encode('hex'))
            #print(new_str)
        
            #thisHex = ByteToHex(thisRead)
            #print("Received " + thisHex)
        else:
            print("Received nothing")
        return thisRead


    ############################################
    # REMOVEME - old stuff for reference only

    # return a list of two-tuples
    # row or column = 0 returns the whole column or row, respectively
    # single tile returns list of itself
    def getTileList (self, row, column):
        raise NotImplementedError()

    # return a list of active pressure sensors
    def getSensors (self):
        raise NotImplementedError()

    # TODO - not yet used perhaps useful if target slot can be passed in
    def pollSensors(self):
        raise NotImplementedError()


    ############################################
    # test code

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

def main():
    print("Testing LSRealTile")

    # serial ports are COM<N> on windows, /dev/xyzzy on Unixlike systems
    print("Available serial ports:")
    print(list(serial_ports()))
        
    comPort = "COM8"
    theSerial = None
    try:
        theSerial = serial.Serial(comPort, 19200, timeout=0.001)
        #theSerial.open()
        print(comPort + " opened")

    except serial.SerialException:
        print(comPort + " is not available")
        
    if theSerial != None:
        print("\nStarting tests...")

        myTile = LSRealTile(theSerial,1,2)

        #address = input("What is the tile address?")
        address = 80
        
        myTile.assignAddress(address)
        #myTile.assignAddress(b'\x50')
        result = myTile.getAddress()
        #print("Tile address = " + result)
        strRes = ""
        #strRes = ''.join( [ "0x%02X " %  x for x in result ] ).strip()
        strRes = repr(result)
        #for i in result:
        #    strRes  += "0x%s " % (i.encode('hex'))
        print("Tile address = " + strRes)
        time.sleep(2)

        print("Testing setColor")
        myTile.setColor(7)
        time.sleep(2)

        print("Testing setShape")
        myTile.setShape(51) # 0x33 AKA "4"
        time.sleep(2)

        print("Testing setColor")
        myTile.setColor(1)
        time.sleep(4)

        print("Testing setShape")
        myTile.setShape(112) # 0x70 AKA "7"
        time.sleep(2)

        print("Testing flip")
        myTile.flip()
        time.sleep(4)

        print("Testing latch")
        myTile.latch()
        time.sleep(2)

        print("Testing reset")
        myTile.reset()
        time.sleep(2)

        print("Testing locate")
        myTile.locate()
        time.sleep(4)

        print("Testing eepromRead")
        myTile.eepromRead(0)
        time.sleep(2)

        print("\nVersion command should return something:")
        val = myTile.version()
        if len(val) > 0:
            #print("Version command returned 0x%2X " % (val))
            pass
        
        theSerial.close()
       
    input("\nDone - Press the Enter key to exit") # keeps double-click window open

    #time.sleep(10)

if __name__ == '__main__':

    main()


