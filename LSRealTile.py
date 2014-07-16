#!/usr/bin/env python

# the API is the base class
from LSTileAPI import *

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
LS_DEBUG = LS_LATCH+7 # control tile debug output

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
        self.Debug = True
        if sharedSerial is None:
            print("Shared serial is None")
    def destroy(self):
        return

    # set immediately or queue this color in addressed tiles
    def setColor(self, color):
        cmd = SET_COLOR
        self.__tileWrite([cmd, color])

    def setShape(self, shape):
        cmd = SET_SHAPE
        self.__tileWrite([cmd, shape])
        self.shape = shape

    def getShape(self):
        return self.shape

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

    def setDigit(self, digit):
        if ((digit < 0) | (digit > 9)):
            return  # some kind of error - see Noah example
        digitMaps=[0x7E,0x30,0x6D,0x79,0x33,0x5B,0x7D,0x70,0x7F,0x7B]
        self.shape = digitMaps[digit]
        cmd = SET_SHAPE
        self.__tileWrite([cmd, self.shape])

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
        self.__tileWrite([cmd], True)  # do not eat output
        # return response
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
        self.__tileWrite([cmd, eeAddr], True)  # do not eat output
        # return response
        val = self.__tileRead()
        return val

    # read any saved errors
    def errorRead(self):
        # send read command
        cmd = RETURN_ERRORS
        self.__tileWrite([cmd], True)  # do not eat output
        # return response
        val = self.__tileRead()
        return val

    def blank(self):
        raise NotImplementedError()
        self.setColor('white')
        return

    # send mode command that displays stuff
    def locate(self):
        cmd = 7 # the SHOW_ADDRESS command
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
        self.__tileWrite([versionCmd], True)  # do not eat output
        # return response in case tile spits stuff at reset
        time.sleep(1.0)
        val = self.__tileRead()

    def setDebug(self, debugFlag):
        cmd = LS_DEBUG
        self.Debug = debugFlag
        self.__tileWrite([cmd, debugFlag])

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
    def __tileWrite(self, args, expectResponse=False):
        if self.mySerial == None:
            return
        # insert address byte plus optional arg count
        addr = self.address + len(args) - 1  # command is not counted
        args.insert(0, addr)
        count = self.mySerial.write(args)
        if self.Debug:
            writeStr = (' '.join(format(x, '#02x') for x in args))
            print("0x%x command wrote %d bytes: %s " % (args[1], count, writeStr))

        # if no response is expected, read anyway to flush tile debug output
        if(not(expectResponse)):
            thisRead = self.mySerial.read(8)
            if len(thisRead) > 0:
                #if self.Debug:
                # debug or not, if tile sends something, we want to see it
                if True or self.Debug:
                    print ("Debug response: " + ' '.join(format(x, '#02x') for x in thisRead))

    # read from the tile
    def __tileRead(self):
        if self.mySerial == None:
            return
        thisRead = self.mySerial.read(8)
        if len(thisRead) > 0:
            #print("Received " + thisRead.ToHex())
            print ("Received: " + ' '.join(format(x, '#02x') for x in thisRead))
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

# simple delay between test statements with default delay
def testSleep(secs=0.3):
    time.sleep(secs)

# send sync sequence
def serialSync(mySerial):
    #print("sync")  # probably should not print since it slows down timing
    mySerial.write([0, 0, 0, 0])
    
# full suite of command tests
def fullSuite(myTile):
        print("\nTesting setDebug - off")
        myTile.setDebug(0)
        testSleep()

        print("\nTesting setDebug - on")
        myTile.setDebug(1)
        testSleep()

        print("\nTesting setColor - white")
        myTile.setColor(7)
        testSleep()

        print("\nTesting setShape - 4")
        myTile.setShape(51) # 0x33 AKA "4"
        testSleep()


        print("\nTesting setColor - red")
        myTile.setColor(1)
        testSleep()

        print("\nTesting setShape - 7")
        myTile.setShape(112) # 0x70 AKA "7"
        testSleep()

        print("\nTesting setDigit - all of them")
        for i in range(10):
            myTile.setDigit(i)
            testSleep()

        print("\nTesting setColor - all of them")
        for i in range(0,8):
            myTile.setColor(i)
            testSleep()

        print("\nTesting setShape - faster, with Debug off")
        fastDelay = 0.001
        fastTime = 5.0
        tmpDebug = myTile.Debug
        start = time.time()
        myTile.setDebug(0)
        for someLoops in range(0,100):  # loop a bunch to let this last long enough
            for i in range(0,256):
                myTile.setShape(i%256)
                testSleep(fastDelay)  # may cause another OS swap of 15.6 ms
            if (time.time() - start) > fastTime:
                break;
        print("Restoring prior Debug")
        myTile.setDebug(tmpDebug)

        print("\nTesting errorRead")
        testSleep()
        myTile.errorRead()
        testSleep()

        print("\nSetting same color and digit many times to test flicker")
        fastDelay = 0.01
        fastTime = 10.0
        tmpDebug = myTile.Debug
        myTile.setDebug(0)
        start = time.time()
        for someLoops in range(0,10000):  # loop a bunch to let this last long enough
            for color in range(1,8):
                myTile.setColor(color)
                for i in range(0,20):
                    myTile.setDigit(8)
                    testSleep(fastDelay)  # may cause another OS swap of 15.6 ms
            if (time.time() - start) > fastTime:
                break;
        print("Restoring prior Debug")
        myTile.setDebug(tmpDebug)

        print("\nTesting errorRead")
        myTile.errorRead()
        testSleep()

        print("\nSetting up to test flip")
        myTile.setDigit(7)
        myTile.setColor(7)
        testSleep(1)
        print("\nTesting flip")
        myTile.flip()
        testSleep(1)

        print("\nTesting unflip")
        myTile.unflip()
        testSleep(1)

        print("\nTesting reset")
        myTile.reset()
        testSleep(4)

        print("\nTesting latch")
        myTile.latch()
        testSleep()

        print("\nTesting locate")
        myTile.locate()
        testSleep(6)
        
        print("\nTesting eepromRead - first few addresses")
        for i in range(0,8):
            myTile.eepromRead(i)
            testSleep()

        print("\nVersion command should return something:")
        val = myTile.version()
        if len(val) > 0:
            #print("Version command returned 0x%2X " % (val))
            pass

# lots of output - looking for loss of sync, overrun, etc
def commTest(myTile, mySerial):
        print("\nTesting setShape in many loops to look for timing bug")
        myTile.setColor(7)
        for yuck in range(100):
            print("\nTesting setShape - faster, with Debug off")
            fastDelay = 0.01
            fastTime = 3.0
            tmpDebug = myTile.Debug
            start = time.time()
            myTile.setDebug(0)
            for someLoops in range(0,100):  # loop a bunch to let this last long enough
                for i in range(0,256):
                    if i%64 == 50:
                        serialSync(mySerial)
                    myTile.setShape(i%256)
                    testSleep(fastDelay)  # may cause another OS swap of 15.6 ms
                if (time.time() - start) > fastTime:
                    break;

            print("Restoring prior Debug")
            myTile.setDebug(tmpDebug)


# simple testing function for LSRealTile
def main():
    print("\nTesting LSRealTile")

    # serial ports are COM<N> on windows, /dev/xyzzy on Unixlike systems
    availPorts = list(serial_ports())
    print("Available serial ports:" + str(availPorts))
    comPort = "COM8"
    if len(availPorts) > 0:  # try the first port in the list
        comPort = availPorts[0]
    print("Attempting to open port " + comPort)
    theSerial = None
    try:
        theSerial = serial.Serial(comPort, 19200, timeout=0.001)
        print(comPort + " opened")

    except serial.SerialException:
        print(comPort + " is not available")
        
    if theSerial != None:
        print("\nStarting tests...")

        myTile = LSRealTile(theSerial,1,2)

        address = input("What is the tile address? (0 is global): ")
        address = int(address)
        #address = 96 #80
        
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
        testSleep()

        print("\nTesting reset")
        myTile.reset()
        testSleep(6)

        print("Test choices:")
        print("    0 - full test suite")
        print("    1 - communications test")
        testChoice = int(input("What test do you want to run? "))
        if testChoice == 0:
            fullSuite(myTile)
        elif testChoice == 1:
            commTest(myTile, theSerial)
        else:
            print("You did not enter a valid test choice")
        
        
        print("\nFinal reset")
        myTile.reset()        
        theSerial.close()
       
    input("\nDone - Press the Enter key to exit") # keeps double-click window open

if __name__ == '__main__':

    main()


