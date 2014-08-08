// ls_wireAPI.h - 13 July 2014
//

// Tiles respond to either specific address or the address of 0.
// All commands follow one byte containing the address and the number of bytes.
// Commands that don't send the expected number of bytes in a short time period will
// be terminated, and the command will be placed in the error queue.
// Unrecognized commands will be placed  in the error queue.
// Commands to other addresses will be quietly dropped.
// Address is top 5 bits - addresses are multiples of 8, for 31 addresses per bus
// Byte count is low 3 bits, not counting the address or command byte
// Examples:
//   tell all tiles to flip display upside-down - 0x0, 0x18
//   read EEPROM address 4 from tile at address 80(0x50) - 0x51, 0x60, 0x4
//   write 10 to the same EEPROM address - 0x52, 0x61, 0x4, 0xA

// Lightsweeper tile commands

// one byte commands for special test modes
// some of these can be used to visually locate the addressed tile
#define NOP_MODE 0      // this command changes nothing
#define SENSOR_TEST 1   // single digit ADC voltage, color changes at threshold
#define SENSOR_STATS 2 
#define SEGMENT_TEST 3  // walks through all colors of all digits
#define FASTEST_TEST 4  // walks through all colors of all digits fast, looks white
#define ROLLING_FADE_TEST 5  // fades in and out from inside to out
#define ROLLING_FADE_TEST2 6  // fades in and out from inside to out
#define SHOW_ADDRESS 7  // display serial address for floor setup
#define STOP_MODE   0xF // tile stops updating display

// one byte commands for major actions
#define LS_LATCH     (0x10) // refresh display from queue - usually address 0
#define LS_CLEAR     (LS_LATCH+1) // blanks the tile
#define LS_RESET     (LS_LATCH+2) // reboot

// ADC calibration commands
// various statistics may be read from EEPROM addresses EE_ADC_MAX, EE_ADC_MIN  
#define LS_RESET_ADC (LS_LATCH+3) // reset ADC statistics
#define LS_CALIBRATE_ON  (LS_LATCH+4) // reset ADC statistics and starts calibration
#define LS_CALIBRATE_OFF (LS_LATCH+5) // ends calibration, writes ADC stats to EEPROM

// enable or disable debug serial output
#define LS_DEBUG         (LS_LATCH+7) // temporary command to control debug output

// one byte commands defining whether tile is rightside up or not
// the installation may be configured upside down at EEPROM address EE_CONFIG
#define FLIP_ON      (LS_LATCH+8)   // temporary command to flip display upside down
#define FLIP_OFF     (LS_LATCH+9)   // restore display rightside up

// last ditch command to set random, but valid address, if all else fails
// for robustness - two byte command and checksum
#define LS_RANDOM_ADDRESS  (LS_LATCH+0xF)
#define LS_RANDOM_ADDRESS2 (0xD4)

// seven segment immediate display commands with one data byte
#define SET_COLOR      0x20          // set the tile color - use mask bits below
#define COLOR_RED_MASK      1
#define COLOR_GREEN_MASK    2
#define COLOR_BLUE_MASK     4
#define SET_SHAPE      (SET_COLOR+1) // set which segments are "on" - -abcdefg
#define SET_TRANSITION (SET_COLOR+2) // set transition at next refresh - format TBD
// seven segment display commands with three data bytes
#define SET_TILE       (SET_COLOR+3) // set the color, segments, and transition

// one byte query commands returning one byte
#define ADC_NOW     0x40          // unsigned 8 bits representing current ADC
#define ADC_MIN     (ADC_NOW + 1) // unsigned 8 bits representing minimum ADC
#define ADC_MAX     (ADC_NOW + 2) // unsigned 8 bits representing maximum ADC
#define ADC_THRESH  (ADC_NOW + 3) // unsigned 8 bits representing sensor threshold
#define SENSOR_NOW  (ADC_NOW + 4) // unsigned 8 bits representing sensor tripped with history

#define TILE_STATUS  (ADC_NOW + 8) // returns bit mapped status
// defined bit masks
#define STATUS_FLIP_MASK    0x80 // set if segments flipped
#define STATUS_ERR_MASK     0x40 // set if error, and read by RETURN_ERRORS
#define STATUS_CAL_MASK     0x20 // set if currently calibrating

#define TILE_VERSION (ADC_NOW + 9) // format TBD - prefer one byte
// The Hardware version may be read and set at the EE_HW address in EEPROM

// EEPROM read is command and one byte of address
#define EEPROM_READ     0x60
// EEPROM write is two byte command, one address byte, one data byte, and checksum
#define EEPROM_WRITE    (EEPROM_READ+1)
#define EEPROM_WRITE2   (0x53)
// Defined EEPROM addresses:
#define EE_ADDR     0 // 0 - tile address in top five bytes
#define EE_CONFIG   1 // 1 - tile configuration
//       0x80 - AKA STATUS_FLIP_MASK - installed upside-down
//       TBD - color mapping
#define EE_HW       2 // 2 - tile hardware version
//       0 - dev board
//       1 - 3 proto boards
//       2 - 48 tile boards
#define EE_ADC_MAX  3 // High ADC value from calibration - 8 bits of 10 - not sensitive enough?
#define EE_ADC_MIN  4 // Low ADC value from calibration - 8 bits of 10 - not sensitive enough?
#define EE_PUP_MODE 5 // Powerup/Reset mode - command from 0 to 0X0F
//          commands that don't work result in the NOP_MODE
#define EE_PUP_DEBUG    6 // debug output state at reset - 0 disables, 1 enables

// one byte error system commands
#define MAX_ERRORS      4    // number of command errors remembered in error queue
#define ERROR_CMD       0x78 // error test command
#define RETURN_ERRORS   (ERROR_CMD+1) // returns the last MAX_ERRORS errors in queue
        // Most recent errors are returned first
        // Clears error queue and STATUS_ERR_MASK
#define CLEAR_ERRORS    (ERROR_CMD+2) // not really needed, but nearly free


// Segment display commands from 0x80 to 0xBF
#define SEGMENT_CMD     0x80
#define SEGMENT_CMD_END (SEGMENT_CMD+0x3F)
// Depending on the command, up to 4 byte fields will follow (R,G,B and transition)
// Three bits in command declare that R, G, and/or B segment fields will follow
// Two bits define the update condition
// One bit declares that the transition field will follow
//
// One segment byte field will be provided for each of the RGB color bits declared
// Three segment fields allow for arbitrary colors for each segment
// Segment fields are defined in the -abcdefg order, to match LedControl library
#define SEGMENT_FIELD_MASK  0x38
#define SEGMENT_FIELD_RED   0x20
#define SEGMENT_FIELD_GREEN 0x10
#define SEGMENT_FIELD_BLUE  0x08
// Segment fields that are not given clear the associated target color segments
// unless the LSB is set in one of the provided segment fields
#define SEGMENT_KEEP_MASK   0x80 // if MSB set, do not clear any segment data

// The update condition bits define when these segments are applied to the display
// There are three update events: immediate, LATCH commands or a sensor detection
// Only four combinations make sense since immediate trumps the other two
// 00 - segment information is immediately applied to the active display
// 01 - segment information is applied after an LATCH command
// 10 - segment information is applied when the sensor detects weight
// 11 - segment information is applied when the sensor detects weight or LATCH
#define CONDX_MASK      0x06
#define CONDX_IMMED     0x00
#define CONDX_LATCH     0x02
#define CONDX_TRIG      0x04
#define CONDX_LATCH_TRIG 0x06
//
// The transition bit means a final byte will be used as the transition effect
// These transitions are TBD.
#define TRANSITION_FIELD_MASK  0x01
//
// These examples do not include the tile addressing byte -
//
// Set the segments to transition to a blue 4 on the next LATCH:
// B Segments at LATCH  B=bcfg
// 10 001 01 0          00110011
// 0x8A                 0x33
//
// Set the segments to a red white and blue 8 at a sensor trigger:
// RGB Segments at trigger  R=acdfg   G=adg     B=abdeg
// 10 111 10 0              01011011  01001001  01101101
// 0xBC                     0x5B      0x49      0x6D
//
// Immediately set a yellow 6 with transition effect #7:
// Immediate RGB Segments   R=abcdeg  G=abcdeg Transition #7
// 10 110 00 1              01111101  01111101 00000111 (TBD)
// 0xB1                     0x7D      0x7D     0x07 (TBD)
//
// Clear the active display immediately - alternative way to using LS_CLEAR:
// Immediately clear RGB by giving no segment field data
// 10 000 00 0
// 0x80


// TODO - leave room in command space from 0xC0 to 0xFF for UPDATE commands
