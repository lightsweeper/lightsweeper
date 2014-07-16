#include "LedControl.h"
#include "SoftwareSerialMod.h" // local modified SoftwareSerial library
#include <EEPROM.h>
#include "ls_wireAPI.h"
#include <avr/wdt.h> // watchdog timer - just for reset
//#include <avr/io.h> //header file for AVR Microcontroller
//#include <avr/boot.h>

// BOF preprocessor bug prevent - insert me on top of your arduino-code
// From: http://www.a-control.de/arduino-fehler/?lang=en
#if 1
__asm volatile ("nop");
#endif

// TODO - move this section to HW specific header file
// possible versions:
//      original dev board
//      dev board with comm swap
//      three PCB with comm swap
//      three PCB with no swap


#if false // version for dev board with comm swap

// pin 0 AKA DIP pin 5 is pulled too low by TinyISP, so program ATTiny out of its socket
// this is the swapped comm and MAX pin definition
#define LS_TX_PIN 2
#define LS_RX_PIN 0

// defines for LED driver
#define SEGCLK 4    // unswap was 0 // Clock line to the MAX72xx
#define SEGDIN 1    // Data-IN on the MAX72xx
#define SEGLOAD 3   // unswap was 2 // LOAD-pin to MAX72xx

// Define how the RGB virtual displays are mapped to the MAX72xx digits
#define RED 0
#define GREEN 1
#define BLUE 2
#endif


#if true // version for triple PCB with no swap

// this is the unswapped comm and MAX pin definition
#define LS_TX_PIN 3 // ?  // swap is 2
#define LS_RX_PIN 4 // ?  // swap is 0

#define SEGCLK 0    // Clock line to the MAX72xx
#define SEGDIN 1    // Data-IN on the MAX72xx
#define SEGLOAD 2   // LOAD-pin to MAX72xx

// Define how the RGB virtual displays are mapped to the MAX72xx digits
// this accounts for both wiring and LED pinout changes
#define BLUE 0
#define RED 1
#define GREEN 2
#endif

// end of move this section

// returned by TILE_VERSION query - keep old version history here 
const unsigned char tileVersion[2] = {0,3}; // sensor pullup and sensorReadings support, flicker fix
//const unsigned char tileVersion[2] = {0,2}; // tiles can share serial bus
//const unsigned char tileVersion[2] = {0,1}; // support reset

/* Attiny pin map:
  PHYS    INP
   1      (5)     RESET (ADC0 analog/ PBD5 digital input with fuse)
   2       3      (ADC3 analog/PBD3 digital)
   3       4      (ADC2 analog/PBD4 digital)
   4              GND
   5       0      (PD0 digital)
   6       1      (PD1 digital)
   7       2      (analog/PD2 digital)
   8              VCC
   */


SoftwareSerial mySerial(LS_RX_PIN, LS_TX_PIN); // RX, TX

#define TRIGGER 4 // Velostat pressure sensor
LedControl lc=LedControl(SEGDIN,SEGCLK,SEGLOAD,1);


// TODO - seems to compile without this define
#define LED_CONTROL

#define WAIT 150


// colors are represented by an RGB triplet array
#if false
const int red[3] = {255, 0, 0};
const int yellow[3] = {255, 255, 0};
const int green[3] = {0, 255, 0};
const int cyan[3] = {0, 255, 255};
const int blue[3] = {0, 0, 255};
const int magenta[3] = {255, 0, 255};
const int white[3] = {255, 255, 255};
const int black[3] = {0, 0, 0};
#endif
const unsigned char red1[3] = {255, 0, 0};
const unsigned char yellow1[3] = {255, 255, 0};
const unsigned char green1[3] = {0, 255, 0};
const unsigned char cyan1[3] = {0, 255, 255};
const unsigned char blue1[3] = {0, 0, 255};
const unsigned char magenta1[3] = {255, 0, 255};
const unsigned char white1[3] = {255, 255, 255};
const unsigned char black1[3] = {0, 0, 0};

// LEDs in segments represented by char triplets
unsigned char triggerSegs[3];// this display loads with a sensor activation
unsigned char queuedSegs[3]; // this display loads with a LS_LATCH command
unsigned char activeSegs[3]; // the currently displayed segments


bool needInit = true;
#define NEED_INIT   1
#define UPDATE_SEGS 2
unsigned char busAddress;
unsigned char tileStatus;
unsigned char debugFlag;

// high level mode - volatile since used in ISR
volatile unsigned char mode; // init in setup // was = 0;
volatile bool modeChanged = true;

// these seem to be defined in boot.h
//#define GET_LOW_FUSE_BITS (0×0000)
//#define GET_HIGH_FUSE_BITS (0×0003)
//#define GET_LOCK_BITS (0×0001)
//#define GET_EXTENDED_FUSE_BITS (0×0002)

#define _SPM_GET_LOW_FUSEBITS()  __AddrToZByteToSPMCR_LPM((char*)0x0000U, 0x09U)
#define _SPM_GET_HIGH_FUSEBITS()  __AddrToZByteToSPMCR_LPM((void __flash*)0x0003U, 0x09U)
#define _SPM_GET_EXTENDED_FUSEBITS()  __AddrToZByteToSPMCR_LPM((void __flash*)0x0002U, 0x09U)


void setup()
{
    // disable watchdog - probably have only 15 ms, hope we can do this in time
    MCUSR = 0;
    wdt_disable();

// http://embeddedgurus.com/stack-overflow/2009/05/checking-the-fuse-bits-in-an-atmel-avr-at-run-time/
    //char fuse_low = _SPM_GET_LOW_FUSEBITS();

    //int high,low, lock,ext;
    //_delay_ms(1); //DELAY to complete operation
    //high=boot_lock_fuse_bits_get(GET_LOW_FUSE_BITS);
    //_delay_ms(1);
    //low=boot_lock_fuse_bits_get(GET_HIGH_FUSE_BITS);
    //_delay_ms(1);
    //lock=boot_lock_fuse_bits_get(GET_LOCK_BITS);
    //_delay_ms(1);
    //ext=boot_lock_fuse_bits_get(GET_EXTENDED_FUSE_BITS);
    //_delay_ms(1);
    
    // Wake up the virtual displays
    lc.shutdown(RED, false);
    lc.shutdown(GREEN, false);
    lc.shutdown(BLUE, false);
    lc.setScanLimit(0,2); // Only scan 3 digits
  
    //pinMode(A0, INPUT);
    //digitalWrite(A0, HIGH); // a little pull-up
    // WARNING - this pin is A0, but that has the wrong value for digital functions
    // use the digital pin number instead.  A0 and D5 are the same physical pin
    pinMode(5, INPUT_PULLUP);
    analogReference(INTERNAL1V1);  // use internal 1 Volt - TODO - may not be working 
    // Set brightness for all colors (intensity=1-15)
    lc.setIntensity(0, 14);

    // Open serial communications and wait for port to open:
    mySerial.begin(19200);
    
    // initial debug mode
    debugFlag = EEPROM.read(EE_PUP_DEBUG);
    if (0xFF == debugFlag) // in case EEPROM hasn't been initialized
        debugFlag = 0;

    // REMOVEME - or use dlog only
    //mySerial.write(0xEE); // REMOVEME - testing serial stuff
    mySerial.write(get_free_memory());

    busAddress = EEPROM.read(EE_ADDR);
    mySerial.write(busAddress); // greet with address
    //sendOutput(busAddress); // greet with address

    setInversion(0); // basically just reads EEPROM here

    // initial operating mode
    mode = EEPROM.read(EE_PUP_MODE);
    if (0xFF == mode) // in case EEPROM hasn't been initialized
        mode = SHOW_ADDRESS; // ROLLING_FADE_TEST;
    //mode = SENSOR_TEST; // HACK TEMP
}


/// ADC and pressure sensor variables
unsigned char sensorReadings; // MSB is current reading, lower bits recent history
int curAdc;
// TODO - get min and max out of EEPROM
int maxAdc = 0;
int minAdc = 1023;
int threshAdc = 512; // gotta start somewhere

// These vbles are used by display updating code
// such as standalone modes and transitions and effects
// These are global - only one user at a time
// They will usually be updated at the same time
unsigned long updateLedMs; 
unsigned char updateLedState;

static unsigned char commandBytes[8]; // filled by cmdRead, used by cmdParse


// Several kinds of behavior in any routine:
// If a routine is done with its major goal, it returns true
// This allows the caller to advance its own state machine
// Returning false tells the caller that the routine is not done
//
// Reasonably complex routines are expected to keep track of their internal state
// A routine may keep internal state with static variables
// They will be called many times before finishing
// They may use static unsigned longs to keep track of time using millis()
//
// If a routine has done something, and now want to do nothing for a while
// It would just return false until the waiting is over
// e.g. for timed display of a digit


void loop()
{
    // give ACDC a chance every time thru loop
    int pad;
    bool adcDone = smoothread(10, &pad);
 
    needInit = false;

    if(modeChanged)
    {
        needInit = true;

        // will not accept new change until modeChanged is clear
        modeChanged = false;
        dlog(mode); // echo new command mode
    }
    
    if ((mode >= SEGMENT_CMD) && (mode <= SEGMENT_CMD_END))
    {
        processSegmentCmd(mode);
        modeChanged = false;
    }

    // end processing this command with a display update if needed
    else
    switch (mode)
    {
        case SENSOR_TEST:
            sensorTestMode(needInit);
            break;

        case SENSOR_STATS:
            //sensorStats(needInit);
            break;

        case SEGMENT_TEST:
            segmentTestMode(needInit);
            break;

        case FASTEST_TEST:
            // TODO - does not fit?
            //colorcounter();
            fastestTestMode(needInit);
            break;

        case ROLLING_FADE_TEST:
            activeSegs[0] = 0x5B;
            activeSegs[1] = 0x49;
            activeSegs[2] = 0x6D;
            rollingEffect(needInit);
            break;
            
        case ROLLING_FADE_TEST2:
            activeSegs[0] = activeSegs[1] = activeSegs[2] = 0x6E; // different
            rollingEffect(needInit);
            break;
            
        case SHOW_ADDRESS:
            showAddress(needInit);
            break;
            
        case LS_RESET:
            //__asm volatile ("rjmp RESET");  // apparently does not reset the hardware
            //__asm volatile ("rjmp 0");  // apparently does not reset the hardware
            
            // this bootloader does not disable the watchdog, so it keeps going off
            // make sure to clear MCUSR ASAP in setup()
            wdt_enable(WDTO_15MS); while(1){}  // use the watchdog timer
            //wdt_enable(WDTO_500MS); while(1){}  // use the watchdog timer
            //wdt_enable(WDTO_2S); while(1){}  // use the watchdog timer
            
            // could use the RESET pin except using it for sensor
            //pinMode(pin, OUTPUT); digitalWrite(pin, LOW);

            break; // should never get here :)

        case LS_LATCH:
        {
            // copy the queued segment data into the active segment data and update display
            // FWIW - copy loop takes 28 bytes, code seems to unwrap
            // big arrays seem to use loop, take 34 bytes
            for (int i=0;i<3;i++)
            {
                activeSegs[i] = queuedSegs[i];
            }
            //printSegments(activeSegs);        
            printSegments();
            mode = NOP_MODE;
            break;
        }

       case LS_CLEAR:
            // clear the active segment data and update display
            // FWIW - clear loop takes 18 bytes
            for (int i=0;i<3;i++)
            {
                activeSegs[i] = 0;
            }
            //printSegments(activeSegs);        
            printSegments();
            mode = NOP_MODE;
            break;
            
        // commands that set all segments to same color
        case SET_COLOR: // set the tile color - format TBD
        case SET_SHAPE: // set which segments are "on" - -abcdefg
        case SET_TRANSITION: // set transition at the next refresh - format TBD
            singleColor(mode);
            printSegments();
            mode = NOP_MODE;
            break;

        // these commands are one-shot queries
        case SENSOR_NOW:
        case ADC_NOW:
        case ADC_THRESH:
        case ADC_MIN:
        case ADC_MAX:
            getAdcStat(mode);
            mode = NOP_MODE;
            modeChanged = true;  //set to get init
            break;

        // these commands are one-shot queries
        case TILE_STATUS:
            mySerial.write(tileStatus); // sendOutput(tileStatus);
            mode = NOP_MODE;
            break;
        case TILE_VERSION:
            mySerial.write(tileVersion, sizeof(tileVersion));
            // sendOutput(tileVersion, sizeof(tileVersion)); // TODO - does not support lengths
            mode = NOP_MODE;
            break;

        case LS_DEBUG:         
            debugFlag = commandBytes[2];
            mode = NOP_MODE;
            break;

        case FLIP_ON:
        case FLIP_OFF:
            setInversion(mode);
            printSegments();
            mode = NOP_MODE;
            break;

#if false
        case EEPROM_READ:
            eepromRead();
            mode = NOP_MODE;
            break;

        case EEPROM_WRITE:
            eepromWrite();
            mode = NOP_MODE;
            break;
#else
        case EEPROM_READ:
        case EEPROM_WRITE:
            eepromCmd(mode);
            mode = NOP_MODE;
            break;
#endif
        case NOP_MODE:
            // do nothing here
            break;

#if false
        case COLOR_RAMP:
            colorRampTestMode(needInit);
            break;
#endif
        case ERROR_CMD:
        case CLEAR_ERRORS:
        case RETURN_ERRORS:
        default:
            processErrors(mode);
            mode = NOP_MODE; // this mode does nothing, needs no init
            break;
    }


    // simple command processor - requires address in top bits and mode in bottom bits
    // accumulate full command bytes
    bool done = cmdRead();

    // parse command
    if (done) cmdParse();
}

// reads stuff from the serial input 
// returns true when a complete command is acquired
bool cmdRead()
{
    static unsigned char cmdTimerInit;
    bool done = false;
    char logChar = 0;

    // top 4 bits is byte count in command,  bottom 4 is next write index
    static char commandState = 0;
    // use magic sequence of characters to synchronize
    static char syncCount = 0;

    // timeout any command that has been waiting to finish for too long
    // it is most likely that some byte got lost somehow
    // best approach is to try to sync up on the next command
    if ((commandState != 0) && timerExpired(&cmdTimerInit, 100))
    {
        commandState = 0; // reset at timeout
        //logChar = 0xCF; // timeout - but not good to send in a system
        //mySerial.write(0x40); // HACK TEMP - want to see errors on scope
    }
    else // this else allows logChar to be logged in this call
    
    while (mySerial.available())
    {
        char newChar = mySerial.read();

        // resynchronize on FOUR zero bytes in a row - this is two global NOP_MODE commands
        if (0 == newChar)
        {
            syncCount++;
            if (4 == syncCount) // resynchronize !
            {
                commandState = 0;
                syncCount = 0;
                char syncOut = 0x0;
                mySerial.write(syncOut); // all tiles should send this
                break; // break out of while loop
            }
        }
        else
        {
            syncCount = 0;
        }

        // each clause needs to set commandState for next entry
        // initially it should also send a byte for debugging

        // starting a new multi-byte command
        if (commandState == 0)
        {
            commandBytes[0] = newChar;
            // numBytes is bottom 3 bits, does not include address and command
            char numBytes = (newChar & 0x07) + 2;
            commandState = (numBytes << 4) + 1; // next byte idx is 1
            //logChar = 0xC0; // log beginning of command
            timerInit(&cmdTimerInit);
        }

        // continue accumulating a multi-byte command
        else
        {
            {
                int idx = commandState & 0x0F;
                commandBytes[idx] = newChar;
                idx ++;

                // last byte in command?
                int totalBytes = (commandState & 0xF0) >> 4;
                if (idx == totalBytes)
                {
                    commandState = 0; // reset

                    // is this tile addressed - address is top 5 bits
                    char firstByte = commandBytes[0];
                    if (((firstByte & 0xf8) == busAddress) || ((firstByte & 0xf8) == 0))
                    {
                        done = true; // command parser picks up next
                        logChar = 0xCC; // complete command acquired
                    }
                    // this tile was not addressed 
                    else
                    {
                        done = false; // throw out this command
                        //logChar = 0xCE; // not good to send in a system
                        //mySerial.write(commandBytes, 3); // HACK TEMP - want to see errors on scope
                    }

                    // exit out of while loop with no more reads
                    // any additional reads would be for next command
                    break;
                }
                // need to read again
                else
                {
                    commandState = (commandState & 0xF0) + idx; // incremented next byte idx
                    //logChar = 0xC0 + idx;
                }
            }
        }
    }

    if (0 != logChar)
        dlog(logChar);

    return done;
}


// parse commandBytes in command processor 
bool cmdParse()
{
    bool done = false;
    // logChar = 0xCC; // complete command acquired

    modeChanged = true; // activates command
    done = true;
    char newChar = commandBytes[1];
    mode = newChar;  // command is whole second byte

    return done;
}

// segment update commands

void processSegmentCmd(unsigned char mode)
{
    // TODO - could do some error checking on defined fields and commandBytes length
    int commandIdx = 2; // first optional field is after address and command bytes

    // first pass through fields to determine if un-given segment fields should be cleared
    bool clearOthers = true;
    commandIdx = 2;
    if ((mode & SEGMENT_FIELD_RED) && (commandBytes[commandIdx++] & SEGMENT_KEEP_MASK)) 
    {
        clearOthers = false;
    }
    else // these two else statements save 30 program bytes and a litle execution time
    if ((mode & SEGMENT_FIELD_GREEN) && (commandBytes[commandIdx++] & SEGMENT_KEEP_MASK)) 
    {
        clearOthers = false;
    }
    else
    if ((mode & SEGMENT_FIELD_BLUE) && (commandBytes[commandIdx++] & SEGMENT_KEEP_MASK)) 
    {
        clearOthers = false;
    }

    // Determine what conditions will cause colors to be loaded into active display
    // Every update condition has at least one target register set
    // One condition updates both LATCH and TRIG registers
    unsigned char condx = (mode & CONDX_MASK);
    unsigned char* target1 = 0;
    unsigned char* target2 = 0;
    switch (condx)
    {
        default: // saves a few bytes
        case CONDX_IMMED: target1 = activeSegs; break;
        case CONDX_LATCH: target1 = queuedSegs; break;
        case CONDX_TRIG: target1 = queuedSegs; break;
        case CONDX_LATCH_TRIG: target1 = queuedSegs; target2 = triggerSegs; break;
    }

    // second pass through fields to actually set target segments
    // three possibilities:
    //      segment data is provided, copy to one or two targets
    //      no segment data, clear one or two targets
    //      no segment data but keep flag is set, so no change to targets
    commandIdx = 2;

    // process red segments
    if (mode & SEGMENT_FIELD_RED) // save segments
    {
        unsigned char thisDefn = commandBytes[commandIdx++];
        target1[0] = thisDefn;
        if (target2) target2[0] = thisDefn;
    }
    else if (clearOthers) // clear segments
    {
        target1[0] = 0x0;
        if (target2) target2[0] = 0x0;
    }

    // process green segments
    if (mode & SEGMENT_FIELD_GREEN) // save segments
    {
        unsigned char thisDefn = commandBytes[commandIdx++];
        target1[1] = thisDefn;
        if (target2) target2[1] = thisDefn;
    }
    else if (clearOthers) // clear segments
    {
        target1[0] = 0x0;
        if (target2) target2[0] = 0x0;
    }

    // process blue segments
    if (mode & SEGMENT_FIELD_BLUE) // save segments
    {
        unsigned char thisDefn = commandBytes[commandIdx++];
        target1[2] = thisDefn;
        if (target2) target2[2] = thisDefn;
    }
    else if (clearOthers) // clear segments
    {
        target1[0] = 0x0;
        if (target2) target2[0] = 0x0;
    }

    // TODO - process transition field
    unsigned char transition;
    if (mode & TRANSITION_FIELD_MASK)
    {
        transition = commandBytes[commandIdx++];
    }
}


// commands that set all segments to same color

void singleColor(unsigned char mode)
{
#if TRY_TO_MERGE_WITH_OTHER_CMDS
    // Try to be smart and work from previously set multi-color setups
    // The problem is when the color is black or the segments are all off
    // This causes all the segments to be off forever :(
    unsigned char oneColorSegs = 0;
    unsigned char commonColor = 0;

    switch (mode)
    {
        // set the color of any segment lit now with the new color
        case SET_COLOR: // set the tile color - format TBD
            oneColorSegs = activeSegs[0] | activeSegs[1] | activeSegs[2];
            //dlog(oneColorSegs);

            commonColor = commandBytes[2];
            break;

        // set the color of the new segment with all the colors currently active
        case SET_SHAPE: // set which segments are "on" - -abcdefg
            if (activeSegs[0])
                commonColor |= COLOR_RED_MASK;
            if (activeSegs[1])
                commonColor |= COLOR_GREEN_MASK;
            if (activeSegs[2])
                commonColor |= COLOR_BLUE_MASK;
            //dlog(commonColor);

            oneColorSegs = commandBytes[2];
            break;

        // TODO - nothing here quite yet
        case SET_TRANSITION: // set transition at the next refresh - format TBD
        default:
            return;
    }

    // log the new color and segments
    dlog(commonColor);
    dlog(oneColorSegs);

#else

    static unsigned char oneColorSegs = 0;
    static unsigned char commonColor = 0;

    switch (mode)
    {
        // set the color of any segment lit with the new color
        case SET_COLOR: // set the color of all segments
            commonColor = commandBytes[2];
            break;

        // set the color of the new segment with the currently active colors
        case SET_SHAPE: // set which segments are "on"  -abcdefg
            oneColorSegs = commandBytes[2];
            break;

        // TODO - nothing here quite yet
        case SET_TRANSITION: // set transition at the next refresh - format TBD
        default:
            return;
    }

#endif

    // now have the segments and the colors, load the display registers
    activeSegs[0] = (commonColor & COLOR_RED_MASK) ? oneColorSegs : 0;
    activeSegs[1] = (commonColor & COLOR_GREEN_MASK) ? oneColorSegs : 0;
    activeSegs[2] = (commonColor & COLOR_BLUE_MASK) ? oneColorSegs : 0;

    //printSegments(activeSegs);
}

// demo and standalone modes

// mode = SENSOR_TEST
void sensorTestMode(bool init)
{
    unsigned long newMs = millis();

    if(init)
    {
        updateLedMs = newMs;
        updateLedState = 0;
        dlog(0xB0);
    }

    bool done;
    unsigned long deltaMs = newMs - updateLedMs;
    //const int *dispColor;
    int digit;

    switch (updateLedState)
    {
        // take ADC readings
        case 0:
        default: // saves a few bytes
        {
            //curAdc = (curAdc+10)%1024; // HACK TEMP - ramp
            int pad;
            done = smoothread(10, &pad);
            
            if (done)
            {
                curAdc = pad;
                updateLedState = 1; // done here
                dlog(0xB1);
            }
            break;
        }
        
        // display ADC digits
        case 1:
        {
            int curVal = curAdc;
            bool overThresh = (curVal > threshAdc);
            //dispColor = overThresh ? yellow : cyan; // color shows whether over or under threshold
            // color shows whether over or under threshold
            const unsigned char* dispColor = overThresh ? yellow1 : cyan1;
            digit = map(curVal, 0, 1023, 0, 9); // map input to single digit
            printDigit(digit, dispColor); // display first digit
            updateLedMs = newMs;
            updateLedState = 2; // done here
            break;
        }

        // display more info?
        case 2:
            if (deltaMs > 100) // display new digit
            {
                updateLedMs = newMs;
                updateLedState = 3;
                //dlog(0xB3);
            }
            break;
    }
}

// mode = SENSOR_STATS
void sensorStats(bool needInit)
{
    //static int loopState;
    unsigned long newMs = millis();

    if(needInit)
    {
        updateLedMs = newMs;
        updateLedState = 0;
    }

    bool done;
    unsigned long deltaMs = newMs - updateLedMs;
    int pad;
    
    switch (updateLedState)
    {
        // take ADC readings
        case 0:
        default: // saves a few bytes
            done = smoothread(10, &pad);

            if (done)
            {
                curAdc = pad;
                updateLedState = 1; // done here
            }
            break;

        // display ADC digits
        case 1:
        {
            int curVal = curAdc;
            bool overThresh = (curVal > threshAdc);
            //const int *dispColor;
            //dispColor = overThresh ? yellow : cyan; // color shows whether over or under threshold
            //done = displayAdcPct(curVal, dispColor);
            // color shows whether over or under threshold
            const unsigned char *dispColor = overThresh ? yellow1 : cyan1;
            done = displayAdcPct(curVal, dispColor);
            if (done)
                updateLedState = 2; // done here
            break;
        }

        // display more info?
        case 2:
            if (deltaMs > 20000) // display more information every 10 secs
            {
                updateLedMs = newMs;
                updateLedState = 3;
            }
            else
                updateLedState = 0; // done here
            
            break;

        // display ADC threshold
        case 3:
            //done = displayAdcPct(threshAdc, (int*)green); // display threshold in green
            //done = displayAdcPct(threshAdc, (unsigned char*)green1); // display threshold in green
            done = displayAdcPct(threshAdc, green1); // display threshold in green
            if (done)
                updateLedState = 4;
            break;

        // display maximum ADC
        case 4:
            //done = displayAdcPct(maxAdc, (int*)red); // display max in red
            //done = displayAdcPct(maxAdc, (unsigned char*)red1); // display max in red
            done = displayAdcPct(maxAdc, red1); // display max in red
            if (done)
                updateLedState = 5;
            break;

        // display minimum ADC
        case 5:
            //done = displayAdcPct(minAdc, blue); // display min in blue
            done = displayAdcPct(minAdc, blue1); // display min in blue
            if (done)
            {
                updateLedState = 0; // done here
            }
            break;
    }
}

// copied from LedControl
// whole table is not needed, and something blows up with whole table
const static byte lsCharTable[16] = {
    B01111110,B00110000,B01101101,B01111001,B00110011,B01011011,B01011111,B01110000,
    B01111111,B01111011,B01110111,B00011111,B00001101,B00111101,B01001111,B01000111};

// TODO - 3 board proto and probably 48 board build have mirrored segments
// Noah is using this table
const static byte lsMirrorTable[10] =
        {B01111110,B00000110,B01011011,B01001111,B00100111,
         B01101101,B01111101,B01000110,B01111111,B01101111};

// mode = SEGMENT_TEST
void segmentTestMode(bool init)
{
    unsigned long newMs = millis();

    // loop thru colors and thru digits
    static char digit = 0;

    if(init)
    {
        digit = 0;
        updateLedMs = newMs;
        updateLedState = 0; // used for color index
    }

    unsigned long deltaMs = newMs - updateLedMs;

    if(init || (deltaMs>1000))
    {
        // prepare for next state
        updateLedMs = newMs;

        // increment color
        updateLedState++;
        if (updateLedState == 7)
        {
            updateLedState = 0;
            // maybe increment digit
            digit++;
            digit = digit%10;
            dlog(32+digit);
        }

        //const int* colors[] = {white, red, yellow, green, cyan, blue, magenta};
        //int* color = (int*) colors[(int)updateLedState];
        const unsigned char* colors[] = {white1, red1, yellow1, green1, cyan1, blue1, magenta1};
        const unsigned char* color = colors[(int)updateLedState];

        printDigit(digit, color);
    }
}

// walk thru colors and digits as fast as possible - in this control model
void fastestTestMode(bool init)
{
    // loop thru colors and thru digits
    static char digit = 0;

    if(init)
    {
        updateLedState = 0; // used for color index
        digit = 0;
    }

    {
        // increment color
        updateLedState++;
        if (updateLedState == 7)
        {
            updateLedState = 0;
            // maybe increment digit
            digit++;
            digit = digit%10;
        }
    }

    //const int* colors[] = {white, red, yellow, green, cyan, blue, magenta};
    //int* color = (int*) colors[(int)updateLedState];
    const unsigned char* colors[] = {white1, red1, yellow1, green1, cyan1, blue1, magenta1};
    const unsigned char* color = colors[(int)updateLedState];

    printDigit(digit, color);
    //delay(5); // little delay
}


// walk thru colors and digits as fast as possible - in this control model
void colorRampTestMode(bool init)
{
    unsigned long newMs = millis();

    // loop thru colors and thru digits
    static int digit = 0;

    if(init)
    {
        digit = 0;
        updateLedMs = newMs;
        updateLedState = 0; // used for color index
    }

    unsigned long deltaMs = newMs - updateLedMs;

    if(deltaMs>100)
    {
        // prepare for next state
        updateLedMs = newMs;

        // increment color
        updateLedState++;
        if (updateLedState == 7)
        {
            updateLedState = 0;
            // maybe increment digit
            digit++;
            digit = digit%10;
        }
    }

    //int* color = (int*) colors[colorIdx];
    //int color[3];
    unsigned char color[3];
    color[0] = (updateLedState %1) * digit * 25; // 0 to 225
    color[1] = (updateLedState/2 %1) * digit * 25;
    color[2] = (updateLedState/4 %1) * digit * 25;
    color[0] = digit * 25; // 0 to 225
    color[1] = 0 * digit * 25;
    color[2] = (updateLedState/4 %1) * digit * 25;
    printDigit(digit, color);
    delay(5); // little delay
}


// display serial address for floor setup - runs forever
void showAddress(bool init)
{
    unsigned long newMs = millis();

    if(init)
    {
        updateLedMs = newMs;
        updateLedState = 0;
        dlog(0xB0);
    }

    unsigned long deltaMs = newMs - updateLedMs;

    // split address into array of digits, LSD first
    int val = busAddress;
    char digits[3];
    splitInt(val, 3, digits);
    const unsigned long dispTimeMs = 2000;

    switch (updateLedState)
    {
        // display first digit
        case 0:
            printDigit(digits[2], red1); // display first digit

            // prepare for next state
            updateLedMs = newMs;
            updateLedState = 1;
            break;

        // wait then display second digit
        case 1:
            if(deltaMs>dispTimeMs) // display digits long enough to see
            {
                printDigit(digits[1], yellow1); // display second digit

                // prepare for next state
                updateLedMs = newMs;
                updateLedState = 2;
            }
            break;

        // wait then display third digit
        case 2:
            if(deltaMs>dispTimeMs) // display digits long enough to see
            {
                printDigit(digits[0], green1); // display third digit

                // prepare for next state
                updateLedMs = newMs;
                updateLedState = 3;
            }
            break;

        // wait then display third digit
        case 3:
            if(deltaMs>dispTimeMs) // display digits long enough to see
            {
                activeSegs[0] = 0x08;
                activeSegs[1] = 0x08;
                activeSegs[2] = 0x08;
                printSegments();

                // prepare for next state
                updateLedMs = newMs;
                updateLedState = 4;
            }
            break;

        // done
        case 4:
        default:
            if(deltaMs>dispTimeMs)
            {
                // prepare for next state
                updateLedMs = newMs;
                updateLedState = 0; // done here
            }
            break;
    }
}


// ADC and pressure sensor functions

// sensor value is single char
// ADC values are 10 bits but return 8
void getAdcStat(char stat)
{
    int selVal;
    unsigned char retVal;

    if (SENSOR_NOW == stat)
    {
        retVal = sensorReadings;

        // Host should not be expected to keep track of which readings it has seen,
        // Fill all bits with most recent reading so only new changes will be in next status read
        sensorReadings = (sensorReadings >= 128) ? 0xFF : 0x0;
    }
    else
    {
        switch(stat)
        {
            default: // saves a few bytes
            case ADC_NOW:       selVal = curAdc; break;
            case ADC_THRESH:    selVal = threshAdc; break;
            case ADC_MIN:       selVal = minAdc; break;
            case ADC_MAX:       selVal = maxAdc; break;
        }
        retVal = selVal >> 2;
    }
    mySerial.write(retVal); // sendOutput(retVal);
}


bool smoothread(int smoothing, int* avgAdc)
{
    bool done = false;
    int inputPin = 0; //TRIGGER;
    static unsigned char adcTimerInit;  // static to control ADC state machine

    static int total = 0;               // the running total
    static unsigned char readState = 0; // allows smoothing to 15 with 16 skips

    if (timerExpired(&adcTimerInit, 5)) // long-ish period when logging
    {
        total = total + analogRead(inputPin);  // nominal 100 us per read
        //total = analogRead(inputPin);  // nominal 100 us per read
        timerInit(&adcTimerInit);
        readState++;
    }

    // accumulate for "smoothing" times
    if (readState >= smoothing)
    {
        int average = total / smoothing;
        //int average = total;
        const int high = 1023; // maximum ADC value
        const int low = 0;
        average = constrain(average, low, high);
        *avgAdc = average;
        curAdc = average; // global

        if (maxAdc < average) maxAdc = average;
        if (minAdc > average) minAdc = average;

        // for now, set threshold to middle of observed values
        threshAdc = (maxAdc + minAdc) / 2;

        //dlog(0xC0);
        //dlog(readState);
        //dlog(average >> 4);  // 0-1023 to 8 bits
        //int vble = map(average, 0, 1023, 0, 99);
        //dlog(vble);  // 99%
        //mySerial.write(vble);  // 99% - lots of output - mostly 0x63

        done = true;
        readState = 0;
        total = 0;

        // add the current reading to the accumulated status byte for the host
        sensorReadings = sensorReadings >> 1;   // shift out oldest reading
        if (average >= threshAdc)               // insert new reading in MSB
            sensorReadings |= 0x80;
    }

    return done;
}


void colorcounter() {

    int iterator = 0;
    int r = 1;
    int g = 1;
    int b = 1;
    int p = 0;

    int loops = 0;

    while (1) {
        if (iterator == 0) {

            loops++;

            if (prime(loops)) {
                r = 1;
                b = 1;
                g = 1;
                p = loops;
                for (int i=0;i<loops;i++) {
                    //printDigit(iterator,white);
                    printDigit(iterator,white1);
                    delay(1);
                }
            } else {
                //int color[3];
                unsigned char color[3];
                color[0] = r * 255;
                color[1] = g * 255;
                color[2] = b * 255;
                printDigit(iterator,color);
                delay(p);
            }


        } else {
            //int color[3];
            unsigned char color[3];
            color[0] = r * 255;
            color[1] = g * 255;
            color[2] = b * 255;
            printDigit(iterator,color);
            delay(p);
        }

        if (r == 1) {
            if (g == 1) {
                if (b == 1) {
                    g = 0;
                    b = 0;
                } else {
                    r = 0;
                }
            } else {
                if (b == 1) {
                    b = 0;
                } else {
                    g = 1;
                }
            }
        } else if (g == 1) {
            if (b == 1) {
                g = 0;
            } else {
                b = 1;
            }
        } else {
            r = 1;
        }
  
        iterator++;
  
        if (iterator > 9) {
            iterator = 0;
        }
    }
}

int prime(int n) {
    int i;
    for (i=2;i<n;i++) {
        if (n % i == 0 && i != n) return 0;
    }
    return 1;
}

// display ADC value as 2 digit percentage of maximum
// returns true when done
//bool displayAdcPct(int val, const int *rgb)
bool displayAdcPct(int val, const unsigned char *rgb)
{
    static char dispState; // separate from display state?
    static char digits[2];
    const int high = 1023; // maximum ADC value
    const int low = 0;

    static unsigned long lastMs;  // separate from display timer?
    unsigned long newMs = millis();
    unsigned long deltaMs = newMs - lastMs;

    switch (dispState)
    {
        // convert ADC val and display first digit
        case 0:
        default: // saves a few bytes
            val = constrain(val, low, high);
            val = map(val, 0, high, 0, 99); // map input to two digit percent
            splitInt (val, 2, digits); // splits into array of digits, LSD first
            printDigit(digits[1], rgb); // display first digit

            // prepare for next state
            lastMs = newMs;
            dispState = 1;
            break;

        // wait then display second digit
        case 1:
            if(deltaMs>500)
            {
                printDigit(digits[0], rgb); // display second digit

                // prepare for next state
                lastMs = newMs;
                dispState = 2;
            }
            break;

        // wait then clear display
        case 2:
            if(deltaMs>500) // wait to clear second digit
            {
                printDigit(8, black1); // clear
                // prepare for next state
                lastMs = newMs;
                dispState = 3; // done here
            }
            break;

        // done
        case 3:
            if(deltaMs>400)
            {
                // prepare for next state
                lastMs = newMs;
                dispState = 0; // done here
                return true; // really done here
            }
            break;
    }

    return false;
}

// splits integer into array of digits for display, LSD first
// caller had better allocate the array - compiler does not catch
//void splitInt (int val, int numDigits, int* digits)
void splitInt (int val, int numDigits, char* digits)
{
    int lotsMoreDigits = val;

    for (int digit=0; digit<numDigits; digit++)
    {
        digits[digit] = lotsMoreDigits%10;
        lotsMoreDigits = lotsMoreDigits/10;
    }
}

// rolling fade effect
// keeps current segments, but uses rolling mask on current segments
inline void rollingEffect(bool init)
{
    unsigned long newMs = millis();
    
    if(init)
    {
        updateLedMs = newMs;
        updateLedState = 0;
    }

    unsigned long deltaMs = newMs - updateLedMs;

    if(init || (deltaMs>200))
    {
        // prepare for next state
        updateLedMs = newMs;
        updateLedState++;
        if (updateLedState > 5)
            updateLedState = 0;
            
        unsigned char mask;
        switch (updateLedState)
        {
            default: // saves a few bytes
            case 0: mask = 0; break;
            case 1: mask = 0x01; break;  // g
            case 2: mask = 0x6E; mask = 0x37; break; //  bc ef g
            case 3: mask = 0xFE; mask = 0x7F; break; // abcdefg
            case 4: mask = 0xFC; mask = 0x7E; break; // abcdef
            case 5: mask = 0x90; mask = 0x48; break; // a  d
        }
        mapActiveToLive(mask);
        // TODO - change to liveSegs
        printSegments();        
    }
}

inline void mapActiveToLive(unsigned char mask)
{
    // TODO - change to liveSegs
    activeSegs[0] = activeSegs[0] & mask;
    activeSegs[1] = activeSegs[1] & mask;
    activeSegs[2] = activeSegs[2] & mask;
}


// seven-segment print signature with RGB byte array
void printDigit(int digit, const unsigned char *rgb)
{
    // map digit with defined color to segments array
    for (int i=0; i<3; i++)
    {
        unsigned char thisColor = 0x7f;
        //thisColor = charTable[(int)digit]; // something blows up with whole table
        thisColor = lsCharTable[(int)digit];
        if (rgb[i] < 127)
            thisColor = 0;
        activeSegs[i] = thisColor;
    }
    //mySerial.write(activeSegs, 3);  // lots of output
    printSegments();
}

#if false // TESTING
// seven-segment print signature with RGB array
void printDigit(int digit, const int *rgb)
{
    // map digit with defined color to segments array
    for (int i=0; i<3; i++)
    {
        unsigned char thisColor = 0x7f;
        //thisColor = charTable[(int)digit]; // something blows up with whole table
        thisColor = lsCharTable[(int)digit];
        if (rgb[i] < 127)
            thisColor = 0;
        activeSegs[i] = thisColor;
    }
    //mySerial.write(activeSegs, 3);  // lots of output
    printSegments();
}
#endif

#if false
// seven-segment print signature with individual RGB ints
void printDigit(int digit, int red, int green, int blue)
{
    lc.clearDisplay(0);
    if (red > 127) {
        lc.setDigit(0,RED,(byte)digit,false);
    }
    if (green > 127) {
        lc.setDigit(0,GREEN,(byte)digit,false);
    }
    if (blue > 127) {
        lc.setDigit(0,BLUE,(byte)digit,false);
    }
}
#endif


// seven-segment print signature with individual segment bits
// TODO - could change from parameter to always using activeSegs
//void printSegments(unsigned char* colorSegments)
void printSegments()
{
    unsigned char* colorSegments = activeSegs;
#if false // this old code caused repeated writes to flicker
    lc.clearDisplay(0);
#else
    static unsigned char lastSegs[3];
#endif

    int row[3] = {RED, GREEN, BLUE};
    for(int i=0; i<3; i++)
    {
        unsigned char thisSeg = colorSegments[i];
#if false // this old code caused repeated writes to flicker
        if (thisSeg)  // more to do if any segment is lit
#endif
        {
            // rotate segments if tile inversion
            if (tileStatus & STATUS_FLIP_MASK)
            {
                const int abc = 0x70;
                const int def = 0x0E;
                const int g   = 0x01;
                thisSeg = ((thisSeg & abc) >> 3) | ((thisSeg & def) << 3) | (thisSeg & g);
            }
#if false // this old code caused repeated writes to flicker
            lc.setRow(0,row[i], thisSeg);
#else
            // update the display only if virtual digit changes to prevent flicker
            //if (lastSegs[i] != thisSeg) // not needed for flicker prevention
            {
                lc.setRow(0, row[i], thisSeg);
                lastSegs[i] = thisSeg;
            }
#endif
        }
    }
}

// sets MSB of tileStatus if tile is upside down 
void setInversion(unsigned char mode)
{
    char flip = EEPROM.read(EE_CONFIG);
    //dlog(flip);
    if (FLIP_ON == mode)
        flip = ~flip;
    flip &= STATUS_FLIP_MASK; // want only flip bit
    //dlog(flip);
    tileStatus = (tileStatus & ~STATUS_FLIP_MASK) | flip;
    //printSegments(activeSegs);        // maybe temporary

    dlog(tileStatus); // MSB is flip bit
}

// utility functions

#if false
void eepromRead()
{
    // TODO - use more than 256 bytes of EEPROM?
    unsigned char addr = commandBytes[2];
    unsigned char val = EEPROM.read(addr);
    mySerial.write(val); // sendOutput(val);
}

void eepromWrite()
{
    // TODO - use more than 256 bytes of EEPROM?
    unsigned char addr = commandBytes[2];
    unsigned char val = EEPROM.read(addr);
    unsigned char datum = commandBytes[3];
    if (val != datum)
        EEPROM.write(addr, datum);
}
#else
void eepromCmd(unsigned char cmd)
{
    // TODO - use more than 256 bytes of EEPROM?
    unsigned char addr = commandBytes[2];
    unsigned char val = EEPROM.read(addr);
    if (cmd == EEPROM_WRITE)
    {
        unsigned char datum = commandBytes[3];
        if (val != datum)
            EEPROM.write(addr, datum);
    }
    else
        mySerial.write(val); // sendOutput(val);
}
#endif

void processErrors(unsigned char mode)
{
    static unsigned char savedErrors[MAX_ERRORS];
   
    if ((CLEAR_ERRORS == mode) || (RETURN_ERRORS == mode))
    {
        if (RETURN_ERRORS == mode)
        {
            // sendOutput(savedErrors, sizeof(savedErrors)); // TODO - does not support lengths
            mySerial.write(savedErrors, 4);
        }
        
        for (unsigned int i=0; i<sizeof(savedErrors); i++)
        {
            savedErrors[i] = 0;  // clear after returning error
        }
        tileStatus &= ~STATUS_ERR_MASK; // clear error bit in status
    }

    // almost any other command must be an error
    else if (NOP_MODE != mode)
    {
        // shift errors to later in array to keep most recent
        for (int i=sizeof(savedErrors)-1; i>=1; i--)
        {
            savedErrors[i] = savedErrors[i-1]; // errors[N-1]=errors[N-2] ... errors[1]=errors[0]
        }
        savedErrors[0] = mode;
        tileStatus |= STATUS_ERR_MASK; // set error bit in status
        dlog(0xFF); // are we getting here?
    }
}

// timer functions

// initialize the timeout clock from the low byte in millis()
void timerInit(unsigned char * initVal)
{
    unsigned long init = millis();
    *initVal = init & 0xFF;
}

// returns true when the desired time has expired
bool timerExpired(unsigned char * initVal, unsigned char timerMs)
{
    // generate now time in single char to match timer init value
    unsigned long now = millis() & 0xFF; // extract low byte
    if (now < *initVal)
        now += 256; // now is always after init

    // TODO - allow up to 7 bits of millis() to elapse
    // TODO - might work up to 255 ms
    bool timeout = (now - *initVal) > timerMs;

    return timeout;
}

// use this write for debug output
inline void dlog (char thisChar)
{
    if(debugFlag)
        mySerial.write(thisChar);
}

// use this write for queries and other desired output
// TODO - DO NOT USE YET - something wrong with this
inline void sendOutput (char thisChar)
{
    mySerial.write(thisChar);
}

extern int __bss_end;
extern void *__brkval;

int get_free_memory()
{
  int free_memory;

  if((int)__brkval == 0)
    free_memory = ((int)&free_memory) - ((int)&__bss_end);
  else
    free_memory = ((int)&free_memory) - ((int)__brkval);

  return free_memory;
}

