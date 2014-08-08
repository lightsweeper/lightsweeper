#!/usr/bin/env python

# the API is the base class
from LSTileAPI import *

import serial
from serial.tools import list_ports
#from struct import *

# imports for testing
import os
import time

# TODO - perhaps better to use hexlify and unhexlify
#from HexByteConversion import *

# these constants copied from LSTileAPI.h

# one byte commands for special test modes
# some of these can be used to visually locate the addressed tile
NOP_MODE        = 0     # this command changes nothing
SENSOR_TEST     = 1     # single digit ADC voltage, color changes at threshold
SENSOR_STATS    = 2 
SEGMENT_TEST    = 3     # walks through all colors of all digits
FASTEST_TEST    = 4     # walks through all colors of all digits fast, looks white
ROLLING_FADE_TEST = 5   # fades in and out from inside to out
ROLLING_FADE_TEST2 = 6  # fades in and out from inside to out
SHOW_ADDRESS    = 7     # display serial address for floor setup
STOP_MODE       = 0xF   # tile stops updating display

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
# EEPROM write is two byte command, one address byte, one data byte, and checksum
EEPROM_WRITE =   (EEPROM_READ+1)
EEPROM_WRITE2 =  (0x53)

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

# Segment display commands from 0x80 to 0xBF
SEGMENT_CMD =   0x80
SEGMENT_CMD_END = (SEGMENT_CMD+0x3F)
# Depending on the command, up to 4 byte fields will follow (R,G,B and transition)
# Three bits in command declare that R, G, and/or B segment fields will follow
# Two bits define the update condition
# One bit declares that the transition field will follow
#
# One segment byte field will be provided for each of the RGB color bits declared
# Three segment fields allow for arbitrary colors for each segment
# Segment fields are defined in the -abcdefg order, to match LedControl library
SEGMENT_FIELD_MASK  = 0x38
SEGMENT_FIELD_RED   = 0x20
SEGMENT_FIELD_GREEN = 0x10
SEGMENT_FIELD_BLUE  = 0x08
# Segment fields that are not given clear the associated target color segments
# unless the LSB is set in one of the provided segment fields
SEGMENT_KEEP_MASK  = 0x80 # if MSB set, do not clear any segment data

# The update condition bits define when these segments are applied to the display
# There are three update events: immediate, LATCH commands or a sensor detection
# Only four combinations make sense since immediate trumps the other two
# 00 - segment information is immediately applied to the active display
# 01 - segment information is applied after an LATCH command
# 10 - segment information is applied when the sensor detects weight
# 11 - segment information is applied when the sensor detects weight or LATCH
CONDX_MASK       = 0x06
CONDX_IMMED      = 0x00
CONDX_LATCH      = 0x02
CONDX_TRIG       = 0x04
CONDX_LATCH_TRIG = 0x06
#
# The transition bit means a final byte will be used as the transition effect
# These transitions are TBD.
TRANSITION_FIELD_MASK = 0x01
#
# These examples do not include the tile addressing byte -
#
# Set the segments to transition to a blue 4 on the next LATCH:
# B Segments at LATCH  B=bcfg
# 10 001 01 0          00110011
# 0x8A                 0x33
#
# Set the segments to a red white and blue 8 at a sensor trigger:
# RGB Segments at trigger  R=acdfg   G=adg     B=abdeg
# 10 111 10 0              01011011  01001001  01101101
# 0xBC                     0x5B      0x49      0x6D
#
# Immediately set a yellow 6 with transition effect #7:
# Immediate RGB Segments   R=abcdeg  G=abcdeg Transition #7
# 10 110 00 1              01111101  01111101 00000111 (TBD)
# 0xB1                     0x7D      0x7D     0x07 (TBD)
#
# Clear the active display immediately - alternative way to using LS_CLEAR:
# Immediately clear RGB by giving no segment field data
# 10 000 00 0
# 0x80



### Implementation of the Lightsweeper low level API to a ATTiny tile
class LSRealTile(LSTileAPI):
    def __init__(self, sharedSerial, row=0, col=0):
        super().__init__(row, col)
        self.row = row
        self.col = col
        self.mySerial = sharedSerial
        # cmdNargs is address + command + N optional bytes
        self.Debug = False
        if sharedSerial is None:
            print("Shared serial is None")
    def destroy(self):
        return

    def getRowCol(self):
        return (self.row, self.col)
        
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
        self.__tileWrite([cmd, self.shape])

    # rgb is a three element list of numbers from 0 (no segments of this color) to 127 (all 7 segments lit)
    # If any element is None, the colors of unspecified fields is preserved
    # Segment fields are defined in the -abcdefg order, to match LedControl library
    def setSegments(self, rgb, conditionLatch = False, conditionTrig = False ):
        cmd = SEGMENT_CMD
        args = []
        clear = True # default to clearing ungiven colors
        # determine if clear non stated colors or keeps them
        if rgb[0] == None:
            clear = False
        elif rgb[1] == None:
            clear = False
        elif rgb[2] == None:
            clear = False

        # One segment byte field will be provided for each of the RGB color bits declared
        # Three segment fields allow for arbitrary colors for each segment
        if rgb[0] != None and rgb[0] >= 1:
            field = rgb[0]
            if not(clear):
                field |= SEGMENT_KEEP_MASK
            cmd += SEGMENT_FIELD_RED
            args.append(field)
        if rgb[1] != None and rgb[1] >= 1:
            field = rgb[1]
            if not(clear):
                field |= SEGMENT_KEEP_MASK
            cmd += SEGMENT_FIELD_GREEN
            args.append(field)
        if rgb[2] != None and rgb[2] >= 1:
            field = rgb[2]
            if not(clear):
                field |= SEGMENT_KEEP_MASK
            cmd += SEGMENT_FIELD_BLUE
            args.append(field)

        # TODO - not tested in tile, probably broken
        if conditionLatch:
            cmd += CONDX_LATCH
        if conditionTrig:
            cmd += CONDX_TRIG

        # TODO - effects transitions

        args.insert(0, cmd) # couldn't insert cmd until all fields are added
        self.__tileWrite(args)


    def set(self,color=0, shape=0, transition=0):
        raise NotImplementedError()
        if (color != 0):
            self.setColor(color)
        if (shape != 0 ):
            self.setShape(shape)
        if(transition != 0):
            self.setTransition(transition)
        return

    # expecting a 7-tuple of Color constants
    def setSegmentsCustom(self, segments, setItNow = True):

        pass

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
        # EEPROM write is two byte command, one address byte, one data byte, and checksum
        sum = EEPROM_WRITE + EEPROM_WRITE2 + eeAddr + datum
        chk = (65536 - sum) % 256;
        #chk = chk + 1 # TEST REMOVEME - this breaks checksum
        print("eepromWrite computed sum = %d, checksum = %d" % (sum, chk))
        self.__tileWrite([EEPROM_WRITE, EEPROM_WRITE2, eeAddr, datum, chk])

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
        self.setColor(0)
        return

    # send mode command that displays stuff
    def locate(self):
        cmd = SHOW_ADDRESS
        self.__tileWrite([cmd])

    def sensorTest(self):
        cmd = 1
        self.__tileWrite([cmd])

    def demo (self, seconds):
        cmd = SEGMENT_TEST
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
        
    def sensorStatus(self):
        #self.__tileWrite([SENSOR_NOW], True)  # do not eat output
        #self.__tileWrite([EEPROM_READ, 0], True)  # do not eat output
        self.__tileWrite([ADC_NOW], True)  # do not eat output
        # return response
        thisRead = self.__tileRead()
        #print ("Sensor status = " + ' '.join(format(x, '#02x') for x in thisRead))
        #if thisRead != None:
        if thisRead:
            for x in thisRead:
                intVal = int(x)
                return intVal #x # val
        # yikes - no return on read from tile?
        return 234
        
    def reset(self):
        versionCmd = LS_RESET
        self.__tileWrite([versionCmd], True)  # do not eat output
        # return response in case tile spits stuff at reset
        time.sleep(1.0)
        val = self.__tileRead()

    # resynchronize communications
    # this uses the global address, so it needs to be done only once per interface port
    def syncComm(self):
        # TODO - __tileWrite could handle global address, simpler to just copy code
        if self.mySerial == None:
            return

        # sync command is two adjacent NOP_MODE commands
        args = [0, NOP_MODE]  # use global address
        count = self.mySerial.write(args)
        count = self.mySerial.write(args)
        if self.Debug:
            print("sync command wrote two NOP_MODE commands")

        # read to flush tile debug output
        thisRead = self.mySerial.read(8)
        if len(thisRead) > 0:
            # Debug or not, if tile sends something, we want to see it
            print ("Debug response: " + ' '.join(format(x, '#02x') for x in thisRead))

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

        # flush stale read data if response is expected
        if (expectResponse):
            thisRead = self.mySerial.read(8)
            if len(thisRead) > 0:
                # debug or not, if tile sends something, we want to see it
                if True or self.Debug:
                    print ("Stale response: " + ' '.join(format(x, '#02x') for x in thisRead))

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
            if self.Debug:
                print ("Received: " + ' '.join(format(x, '#02x') for x in thisRead))
            #thisHex = ByteToHex(thisRead)
            #print("Received " + thisHex)
        #else:
        #    print("Received nothing")
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
        yield '/dev/ttyUSB1'
 #       for port in list_ports.comports():
 #           yield port[0]

# simple delay between test statements with default delay
def testSleep(secs=0.3):
    time.sleep(secs)

# full suite of command tests
def fullSuite(myTile):
        print("\nTesting setDebug - off")
        myTile.setDebug(0)
        testSleep()

        print("\nTesting setDebug - on")
        myTile.setDebug(1)
        testSleep()

        print("\nInitial errorRead to clear errors")
        testSleep()
        myTile.errorRead()
        testSleep()

        print("\nTesting setColor - white")
        myTile.setColor(7)
        testSleep()

        print("\nTesting setShape - 4")
        myTile.setShape(51) # 0x33 AKA "4"
        testSleep()


        print("\nTesting setColor - white")
        myTile.setColor(7)
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

        print("\nFinal reset")
        myTile.reset()        

# lots of output - looking for loss of sync, overrun, etc
def commTest(myTile, mySerial):
        print("\nTesting setShape in many loops to look for timing bug")
        myTile.setColor(7)
        tmpDebug = myTile.Debug
        myTile.setDebug(0)
        for yuck in range(100):
            myTile.setColor(7)
            print("\nTesting setShape - faster, with Debug off")
            fastDelay = 0.005 # 0.01
            fastTime = 3.0
            start = time.time()
            for someLoops in range(0,100):  # loop a bunch to let this last long enough
                for i in range(0,256):
                    if i%64 == 50:
                    #if i%8 == 4:
                        #myTile.syncComm()
                        pass
                    myTile.setShape(i%256)
                    testSleep(fastDelay)  # may cause another OS swap of 15.6 ms
                if (time.time() - start) > fastTime:
                    break;

        print("Restoring prior Debug")
        myTile.setDebug(tmpDebug)

def eepromRead(myTile, firstAddr, len):
        for addr in range(firstAddr, firstAddr+len):
            thisRead = myTile.eepromRead(addr)
            #if len(thisRead) > 0:
            if True:
                print ("EEPROM address " + repr(addr) + " = "  + ' '.join(format(x, '#02x') for x in thisRead))
            else:
                print("No response for EEPROM read at address " + repr(addr))

def eepromTasks(myTile):
        # read first EEPROM addresses
        myTile.setDebug(0)
        print("Looping on EEPROM tests - Ctrl-C to exit")
        for loop in range(1000):
            eepromRead(myTile, 0, 8)
            for action in range(8):
                addr = ""
                addr = input("Enter address of EEPROM to write: ")
                if addr == "":
                    #print ("OK - done for now")
                    break #return
                    pass
                else:
                    addr = int(addr)
                    writeStr = input("Enter value to write: ")
                    writeVal = int(writeStr)
                    print("OK - write " + repr(writeVal) + " to address " + repr(addr))
                    myTile.eepromWrite(addr, writeVal)
                    print("Check errorRead:")
                    myTile.errorRead()


def addressWalk(myTile, mySerial):
    for address in range(1,32):
        myTile.assignAddress(address * 8)
        result = myTile.getAddress()
        myTile.setDebug(0)  # minimize visual clutter
        #print("Tile address = " + result)
        strRes = ""
        #strRes = ''.join( [ "0x%02X " %  x for x in result ] ).strip()
        strRes = repr(result)
        #for i in result:
        #    strRes  += "0x%s " % (i.encode('hex'))
        print("\nReading EEPROM 0 at tile address = " + strRes)
        testSleep()
        #eepromRead(myTile, 0, 1)
        addr = 0
        thisRead = myTile.eepromRead(addr)
        if len(thisRead) > 0:
            print ("Address " + repr(addr) + " = "  + ' '.join(format(x, '#02x') for x in thisRead))
        else:
            #print("No response for EEPROM read at address " + repr(addr))
            pass

def setSegmentsTest(myTile):
        myTile.setDebug(1)
        print("\nInitial errorRead to clear errors")
        testSleep()
        myTile.errorRead()
        testSleep()

        print("\nall segments red")
        rgb = [127,0,0]
        myTile.setSegments(rgb)
        testSleep(2)

        print("\nall segments green")
        rgb = [0,127,0]
        myTile.setSegments(rgb)
        testSleep(2)

        print("\nall segments blue")
        rgb = [0,0,127]
        myTile.setSegments(rgb)
        testSleep(2)

        for loop in range(1):
            seg = 1
            for i in range(7):
                print("\nmostly green with red " + repr(seg))
                rgb = [seg, 127-seg, 0]
                myTile.setSegments(rgb)
                seg = seg * 2
                testSleep()

            seg = 1
            for i in range(7):
                print("\nmostly blue with green " + repr(seg))
                rgb = [0, seg, 127-seg]
                myTile.setSegments(rgb)
                seg = seg * 2
                testSleep()

            seg = 1
            for i in range(7):
                print("\nmostly red with blue " + repr(seg))
                rgb = [127-seg, 0, seg]
                myTile.setSegments(rgb)
                seg = seg * 2
                testSleep()

        print("\nTesting synchronized setSegments calls with latch")
        for loop in range(1):
            seg = 1
            for i in range(7):
                rgb = [seg, seg, seg] # queue segment
                myTile.setSegments(rgb, conditionLatch = True)
                print("segments downloaded, display updates on following latch command...")
                testSleep(2)
                print("latch !")
                myTile.latch()
                seg = seg * 2
                print("")
                testSleep(2)
                
        print("\nTesting multiple setSegments calls with latch")
        for loop in range(3):
            seg = 1
            for i in range(7):
                print("\nThree writes plus latch for white seg=" + repr(seg))
                rgb = [seg, 0, 0] # queue red segment
                myTile.setSegments(rgb, conditionLatch = True)
                rgb = [None, seg, 0] # queue green segment, preserve other colors
                myTile.setSegments(rgb, conditionLatch = True)
                rgb = [0, None, seg] # queue blue segment, preserve other colors
                myTile.setSegments(rgb, conditionLatch = True)
                myTile.latch()
                seg = seg * 2
                testSleep()
                
        print("\ncolor chase - segments from a to f, no g. Debug off")
        print("Ctrl-C to exit")
        myTile.setDebug(0)
        for loop in range(1000000):
            seg = 2
            #if (loop % 1000) == 0:
            #    print("loop " + repr(loop))
            if (loop % 30) == 0:
                print("Checking errors, loop=" + repr(loop))
                myTile.errorRead()
            for i in range(6):  # six segment chase
                red = seg # 2 to 64 for segment f to a
                green = red * 2 # green is one segment CCW from red
                if green == 128:
                    green = 2
                blue = green * 2 # blue is one segment CCW from green
                if blue == 128:
                    blue = 2
                rgb = [red, green, blue]
                myTile.setSegments(rgb)
                seg = seg * 2
                testSleep(0.08) # chase blurs when faster than this
   
def sensorTest(myTile):
       print("\nSetting sensor test mode")
       myTile.sensorTest()

 
def sensorStatusTest(myTile):
    print("looping while reading sensorStatus")
    for i in range(200):
        val = myTile.sensorStatus()
        print("sensorStatus for " + repr(myTile.getAddress()) + " returned " + repr(val))
        testSleep(1)
    print("")

def singleModeTest(mySerial):
    print("Standalone modes:")
    print("1 - pressure sensor test")
    print("5 - address displaay")
    mode = input("What mode do you want? ")
    intMode = int(mode)
    mySerial.write([0, intMode])
    input("Press enter to exit")


# simple testing function for LSRealTile
def main():
    print("\nTesting LSRealTile")

    # serial ports are COM<N> on windows, /dev/xyzzy on Unixlike systems
    availPorts = list(serial_ports())
    print("Available serial ports:" + str(availPorts))
    comPort = "COM8"
    if len(availPorts) > 0:  # try the first port in the list
        comPort = availPorts[0]
    comPort = "/dev/ttyUSB3"
    #portNum = input("Enter the number to append to /dev/ttyUSB:")
    #comPort = "/dev/ttyUSB" + portNum
    comPort = input("Enter the port:")
    print("Attempting to open port " + comPort)
    theSerial = None
    try:
        theSerial = serial.Serial(comPort, 19200, timeout=0.01)
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
        testSleep(2)

        print("Test choices:")
        print("    0 - full test suite")
        print("    1 - communications test")
        print("    2 - sensor test")
        print("    3 - sensorStatus test")
        print("    4 - run single digit mode")
        print("    5 - EEPROM tasks")
        print("    6 - walk the address space")
        print("    7 - test setSegments API")
        testChoice = int(input("What test do you want to run? "))
        if testChoice == 0:
            fullSuite(myTile)
        elif testChoice == 1:
            commTest(myTile, theSerial)
        elif testChoice == 2:
            sensorTest(myTile)
            input("Enter to exit")
        elif testChoice == 3:
            sensorStatusTest(myTile)
        elif testChoice == 4:
            singleModeTest(theSerial)
        elif testChoice == 5:
            eepromTasks(myTile)
        elif testChoice == 6:
            addressWalk(myTile, theSerial)
        elif testChoice == 7:
            setSegmentsTest(myTile)
        else:
            print("You did not enter a valid test choice")
        
        
        theSerial.close()
       
    input("\nDone - Press the Enter key to exit") # keeps double-click window open

if __name__ == '__main__':

    main()


