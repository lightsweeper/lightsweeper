#!/usr/bin/env python

# Diagnose hardware LightSweeper tiles


from lightsweeper.lstile import LSTile
from lightsweeper.lstile import LSRealTile
from lightsweeper.lstile import LSOpen


# imports for testing
import time

# Test code:

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

#        print("\nTesting unflip")      # No more unflip
#        myTile.unflip()
#        testSleep(1)

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
            #if len(thisRead) > 0:  # WTF - this works in addressWalk?
            if True:
                print ("EEPROM address " + repr(addr) + " = "  + ' '.join(format(x, '#02x') for x in thisRead))
            else:
                print("No response for EEPROM read at address " + repr(addr))

def eepromTasks(myTile, loop=False):
        # read first EEPROM addresses
        myTile.setDebug(0)
        loopCount = 1
        if loop:
            print("Looping on EEPROM tests - Ctrl-C to exit")
            loopCount = 1000
        for loop in range(loopCount):
            eepromRead(myTile, 0, 8)
            for action in range(8):
                addr = ""
                addr = input("Enter address of EEPROM to write or <Enter> for none: ")
                if addr == "":
                    #print ("OK - done for now")
                    break #return
                    pass
                else:
                    addr = int(addr)
                    writeStr = input("Enter value to write: ")
                    writeVal = int(writeStr)
                    print("OK - write " + repr(writeVal) + " to address " + repr(addr))
                    # TODO - choose which eepromWrite based on version
                    myTile.eepromWrite(addr, writeVal)
                    #myTile.eepromWriteObsolete(addr, writeVal) # use for Critical-era EEPROM
                    print("Re-reading EEPROM after write:")
                    eepromRead(myTile, 0, 8)
                    print("Check errorRead:")
                    myTile.errorRead()


def addressWalk(myTile, mySerial):
    liveAddresses = []
    keepAddr = myTile.getAddress() # restore original address at end
    for address in range(1,32):
        tileAddr = address * 8
        myTile.assignAddress(tileAddr)
        result = myTile.getAddress()
        myTile.setDebug(0)  # minimize visual clutter
        strAddr = ""
        #strRes = ''.join( [ "0x%02X " %  x for x in result ] ).strip()
        strAddr = repr(result)
        print("Reading EEPROM 0 at tile address = " + strAddr)
        addr = 0
        thisRead = myTile.eepromRead(addr)
        if len(thisRead) > 0:
            liveAddresses.append(tileAddr)
            print ("Address " + repr(addr) + " = "  + ' '.join(format(x, '#02x') for x in thisRead))
        else:
            #print("No response for EEPROM read at tile address " + strAddr)
            pass
    print("\nTile addresses that responded = " + repr(liveAddresses))
    myTile.assignAddress(keepAddr)
    return liveAddresses

def setRandomTileAddress(mySerial,myTile):
    print("\nThis function will attempt to set random addresses for all tiles at the current address")
    print("All tiles currently at address " + repr(myTile.getAddress()) + " will be randomized")
    print("<Ctrl-C> at any time to quit")
    print("These are the steps:")
    print("    do an address survey")
    print("    run the random address command to set temporary addresses")
    print("    loop that allows you to set a permanent address in an individual tile")
    reply = input("Next step is to do address survey, <Enter> to continue, <Ctrl-C> at any time to quit: ")
    addressWalk(myTile, mySerial)

    reply = input("Next step is to set random addresses, <Enter> to continue: ")
    myTile.setRandomAddress()

    for loop in range(3):
        print("\nCurrent address survey:")
        addressWalk(myTile, mySerial)

        print("Next step is to set an(other) address in EEPROM.")
        reply = input("Enter a tile address from survey above (<Enter if finished): ")
        if reply == "":
            return
        newAddr = int(reply)
        myTile.assignAddress(newAddr)
        result = myTile.getAddress()
        myTile.setDebug(0)  # minimize visual clutter
        strAddr = repr(result)
        print("Reading EEPROM 0 at tile address = " + strAddr)

        eepromAddr = 0
        thisRead = myTile.eepromRead(eepromAddr)
        if len(thisRead) > 0:
            print ("Address " + repr(eepromAddr) + " = "  + ' '.join(format(x, '#02x') for x in thisRead))
        else:
            print("Oops - no response for EEPROM read at tile address " + strAddr)
            pass

        reply = input("Enter value to write for new tile address in EEPROM (<Enter> to skip this tile): ")
        if reply == "":
            continue
        writeVal = int(reply)
        print("OK - write " + repr(writeVal) + " for tile address in EEPROM")
        myTile.eepromWrite(eepromAddr, writeVal)
        print("Re-reading EEPROM after write:")
        thisRead = myTile.eepromRead(eepromAddr)
        if len(thisRead) > 0:
            print ("Address " + repr(eepromAddr) + " = "  + ' '.join(format(x, '#02x') for x in thisRead))
        else:
            print("Oops - no response for EEPROM read at tile address " + strAddr)

        reply = input("Next step is to reset this tile to start using its new address, <Enter> to continue: ")
        print("Resetting this tile...")
        myTile.reset()
        testSleep(2)
        myTile.assignAddress(writeVal)  # sync up to tile address change


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
        for loop in range(1):
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
                #if i%64 == 50:
                #if i%8 == 4:
                myTile.syncComm()
                thisRead = myTile.errorRead()
                print ("errorRead response = "  + ' '.join(format(x, '#02x') for x in thisRead))
                thisRead = myTile.eepromRead(0)
                print ("EEPROM Tile Address = "  + ' '.join(format(x, '#02x') for x in thisRead))

            for i in range(6):  # six segment chase
                red = seg # 2 to 64 for segment f to a
                green = red * 2 # green is one segment CCW from red
                if green == 128:
                    green = 2
                blue = green * 2 # blue is one segment CCW from green
                if blue == 128:
                    blue = 2
                if blue == 32:
                    red += 32
                    green += 32
                rgb = [red, green, blue]
                myTile.setSegments(rgb, conditionLatch = True)
                myTile.latch()
                seg = seg * 2
                testSleep(0.08) # chase blurs when faster than this
   
def sensorTest(myTile):
       print("\nSetting sensor test mode")
       myTile.sensorTest()

 
def sensorStatusTest(myTile):
    print("looping while reading sensorStatus")
    myTile.setDebug(0)
    for i in range(200):
        val = myTile.sensorStatus()
        print("sensorStatus for " + repr(myTile.getAddress()) + " returned " + repr(val))
        testSleep(1)
    print("")

def writeAndPoll(myTile):
    print("Setting segments and polling sensor")
    blue = 1
    count = 1000
    changes = 0
    myTile.setDebug(0)
    errors = myTile.errorRead()
    print ("errorRead response = "  + ' '.join(format(x, '#02x') for x in errors))
    val = myTile.sensorStatus()
    print("initial sensor status for tile " + repr(myTile.getAddress()) + " is " + repr(val))
    startSecs = time.time()
    for i in range(count):
        # set the segments
        red = blue
        blue = blue * 2
        if blue > 128:
            blue = 1
        rgb = [red, 0, blue] # queue red segment
        myTile.setSegments(rgb, conditionLatch = False)

        # read the sensor
        newVal = myTile.sensorStatus()
        if newVal != val:
            val = newVal
            changes = changes + 1
            print("sensor status for tile " + repr(myTile.getAddress()) + " is now " + repr(val))
        #testSleep(0.1) # REMOVEME for any real speed testing

    if changes > 0:
        print("final sensor status for tile " + repr(myTile.getAddress()) + " is " + repr(val))
        print("sensor status changed " + repr(changes) + " times")
    endSecs = time.time()
    deltaSecs = endSecs - startSecs
    perSecs = deltaSecs / count
    print("writes and polls took " + repr(deltaSecs) + " s, for " + repr(perSecs) + " s per loop")
    # the timing was just longer than 3 read timeouts per loop
    # with changes to sensorStatus the timing is now over 1 read timeout per loop
    myTile.setDebug(0)
    errors = myTile.errorRead()
    print ("errorRead response = "  + ' '.join(format(x, '#02x') for x in errors))


def singleModeTest(mySerial):
    print("\nStandalone modes:")
    print("1 - pressure sensor test")
    print("3 - walk thru all colors of all digits")
    #FASTEST_TEST    = 4     # walks through all colors of all digits fast, looks white
    print("5 - Fourth of July display")
    print("6 - another rolling fade display")
    print("7 - address display")
    mode = input("What mode do you want? ")
    intMode = int(mode)
    # TODO - why force address 0 global?
    mySerial.safeWrite([0, intMode])

# simple testing function for LSRealTile
def main():
    print("\nTesting LSRealTile")

    tilepile = LSOpen()
    
    comPort = tilepile.selectPort()
    
    print("Attempting to open port " + comPort)
    theSerial = None
    try:
        # The serial read timeout may need to vary on different hosts.
        # On Acer netbook:
        # timeout = 0.003 misses a lot of sensor reads in writeAndPoll
        # timeout = 0.004 misses a few reads
        # timeout = 0.005 rarely misses a read
        # timeout = 0.006 never seen to miss a read
        theSerial = tilepile.lsSerial(comPort, 19200, timeout=0.006)
        print(comPort + " opened")

    except serial.SerialException:
        print(comPort + " is not available")
        
    if theSerial != None:
        print("\nStarting tests...")

        myTile = LSRealTile(tilepile.lsSerial(comPort))

        # start with tile address survey
        address = 8 # default address
        myTile.assignAddress(address)
        tiles = addressWalk(myTile, theSerial)
        testChoice = 6 # initialize for repeat

        reply = input("What is the tile address? (0 is global, <Enter> for default): ")
        if reply == "":  # try the first tile in the list
            address = tiles[0] # 64
        else:
            address = int(reply)
        
        myTile.assignAddress(address)
        result = myTile.getAddress()
        #print("Tile address = " + result)
        strRes = ""
        #strRes = ''.join( [ "0x%02X " %  x for x in result ] ).strip()
        strRes = repr(result)
        print("Tile address = " + strRes)
        testSleep()

        print("\nTesting reset")
        myTile.reset()
        testSleep(2)

        myTile.setDebug(0)
        for loop in range(1000000):
            print("\nTest choices or <Ctrl-C> to exit: ")
            print("    0 - full test suite")
            print("    1 - communications test")
            print("    2 - sensor test")
            print("    3 - sensorStatus test")
            print("    4 - run single digit mode")
            print("    5 - EEPROM tasks")
#            print("    6 - discovery walk thru the address space")
            print("    6 - test setSegments API")
            print("    7 - set segments and poll sensor")
            print("    8 - random tile address procedure")
            reply = input("\nWhat test do you want to run? <Enter> to repeat: ")
            if reply != "":
                testChoice = int(reply)
            if testChoice == 0:
                fullSuite(myTile)
            elif testChoice == 1:
                commTest(myTile, theSerial)
            elif testChoice == 2:
                sensorTest(myTile)
            elif testChoice == 3:
                sensorStatusTest(myTile)
            elif testChoice == 4:
                singleModeTest(theSerial)
            elif testChoice == 5:
                eepromTasks(myTile)
#            elif testChoice == 6:
#                addressWalk(myTile, theSerial)
            elif testChoice == 6:
                setSegmentsTest(myTile)
            elif testChoice == 7:
                writeAndPoll(myTile)
            elif testChoice == 8:
                setRandomTileAddress(theSerial, myTile)
            else:
                print("You did not enter a valid test choice")
        
        theSerial.close()
       
    input("\nDone - Press the Enter key to exit") # keeps double-click window open

if __name__ == '__main__':

    main()


