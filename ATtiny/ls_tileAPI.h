// defines for serial port
// pin 0 AKA DIP pin 5 is pulled mostly low by TinyISP, so usually program ATTiny out of its socket
#define LS_TX_PIN 2
#define LS_RX_PIN 0

// Tiles respond to either specific address or the address of 0.
// All commands follow one byte containing the address and the number of bytes.
// Commands that don't send the expected number of bytes in a short time period will be terminated,
//   and the command will be placed in the error queue.
// Unrecognized command will be placed  in the error queue.
// Commands to other addresses will be quietly dropped.
// Address is in top 5 bits - addresses are multiples of 8, giving 31 addresses per serial bus
// Byte count is in low 3 bits, not counting the address or command byte
// Examples:
//   tell all tiles to flip display upside-down - 0x0, 0x18
//   read EEPROM address 4 from tile at address 80(0x50) - 0x51, 0xA0, 0x4
//   write 10 to the same EEPROM address - 0x52, 0xA1, 0x4, 0xA

// Lightsweeper tile commands

// one byte commands for special test modes
// some of these can be used to visually locate the addressed tile
#define NOP_MODE 0      // does nothing
#define SENSOR_TEST 1   // shows single digit ADC voltage, color changes across threshold
#define SENSOR_STATS 2 
#define SEGMENT_TEST 3  // walks through all colors of all digits
#define FASTEST_TEST 4  // walks through all colors of all digits fast, looks white

// one byte commands for major actions
#define LS_CLEAR     0x10        // blanks the tile
#define LS_RESET     (LS_CLEAR+1) // reboot
#define LS_LATCH     (LS_CLEAR+2) // refresh display with accumulated changes - usually sent to address 0
// one byte commands defining whether tile is rightside up or not
// the installation may be relatively upside down, that is configured in EEPROM at address EE_CONFIG
// whether the installation is upside down is configured in EEPROM at address EE_CONFIG
#define FLIP_ON      (LS_CLEAR+8)   // temporary command to flip display upside down
#define FLIP_OFF     (LS_CLEAR+9)   // restore display rightside up


// ADC calibration commands
// various statistics may be read from EEPROM addresses EE_ADC_MAX, EE_ADC_MIN  
#define LS_RESET_ADC (LS_CLEAR+3) // reset ADC statistics
#define LS_CALIBRATE_ON  (LS_CLEAR+4) // reset ADC statistics and starts calibration cycle
#define LS_CALIBRATE_OFF (LS_CLEAR+5) // ends calibration cycle, writes ADC high and low to EEPROM

// seven segment display commands with one data byte
#define SET_COLOR      0x20          // set the internal color of the tile - format TBD
#define SET_SHAPE      (SET_COLOR+1) // set which internal segments are "on" - abcdefg-
#define SET_TRANSITION (SET_COLOR+2) // set the transition at the next refresh - format TBD
// seven segment display commands with three data bytes
#define SET_TILE       (SET_COLOR+3) // set the color, segments, and transition


// one byte query commands returning one byte
#define ADC_NOW     0x80          // unsigned 8 bits representing current ADC
#define ADC_MIN     (ADC_NOW + 1) // unsigned 8 bits representing minimum ADC
#define ADC_MAX     (ADC_NOW + 2) // unsigned 8 bits representing maximum ADC
#define ADC_THRESH  (ADC_NOW + 3) // unsigned 8 bits representing sensor threshold
#define SENSOR_NOW  (ADC_NOW + 4) // unsigned 8 bits representing sensor tripped with history

#define TILE_STATUS  (ADC_NOW + 8) // returns bit mapped status
// defined bit masks
#define STATUS_FLIP_MASK    0x80
#define STATUS_ERR_MASK     0x40
#define STATUS_CAL_MASK     0x20

#define TILE_VERSION (ADC_NOW + 9) // format TBD - prefer one byte
// The Hardware version may be read and set at the EE_HW address in EEPROM

// one byte command with one byte EEPROM address for read
#define EEPROM_READ     0xA0
// one byte command with one byte EEPROM address and one data byte for write
#define EEPROM_WRITE    (EEPROM_READ+1)
// Defined EEPROM addresses:
#define EE_ADDR     0 // 0 - tile address in top five bytes
#define EE_CONFIG   1 // 1 - tile configuration
//       0x80 - AKA STATUS_FLIP_MASK - installed upside-down
//       TBD - color mapping
#define EE_HW       2 // 2 - tile hardware version
//       0 - dev board
//       1 - 3 proto boards
//       2 - 48 tile boards
#define EE_ADC_MAX  3 // High ADC value from calibration - 8 bits of 10 - may not be sensitive enough
#define EE_ADC_MIN  4 // Low ADC value from calibration - 8 bits of 10 - may not be sensitive enough
#define EE_PUP_MODE 5 // Powerup/Reset mode - single bye command from 0 to 0X0F as an initial operating mode
//          commands that don't work result in the NOP_MODE


// one byte error system commands
#define MAX_ERRORS      4    // not a command, but the number of command errors remembered
#define ERROR_CMD       0xB8 // error test command
#define RETURN_ERRORS   (ERROR_CMD+1) // returns the last MAX_ERRORS errors, most recent first
#define CLEAR_ERRORS    (ERROR_CMD+2) // not really needed, but nearly free

// TODO - leave room in command space from 0xC0 to 0xFF for UPDATE commands

