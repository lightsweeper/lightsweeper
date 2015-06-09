lightsweeper
============

Lightsweeper Firmware


### Requirements:
  - A LightSweeper board
  - An ATTiny85 programmer (we use this one: https://www.sparkfun.com/products/11801)
  - Arduino SDK (http://www.arduino.cc/en/Main/Software)
  - The ATtiny Arduino core board files from https://code.google.com/p/arduino-tiny/


### Installation:

#### Flashing the LightSweeper firmware:
  - Launch the Arduino IDE
  - Navigate to File -> Open and select the file: ls_firmware.ino
  - Make sure that Tools -> Serial Port and Tools -> Programmer are correctly configured
    (For the programmer from Sparkfun you should select USBtinyISP)
  - Under Tools -> Board select the entry "ATtiny85 @ 8 MHz (internal oscillator; BOD disabled)
  - Select Tools -> Burn Bootloader and wait for the operation to complete
  - Select File -> Upload and wait for the firmware to finish flashing

  By default the pin connected to the touch-sensor input of the LightSweeper tile is the same pin
  as is used for ATtiny85's system-reset. Thus to use the LightSweeper tile with sensor input you
  will also need to set the RSTDSBL (reset disable) flag on the chip. You can do this using a tool
  that ships with the Arduino platform called avrdude.

    **WARNING**: The system-reset behavior is required for the chip programming cycle, so once you have
    set the RSTDSBL flag you will be unable to reflash your LightSweeper firmware without using a
    high voltage serial programmer or a high voltage fuse resetter (such as the ATTiny Fuse Repair
    Programmer on this page: http://www.microcontrollerprog.com/fuseprog.html). Do not set the RSTDSBL
    flag until you are ready to install the chip in a LightSweeper board for production.

  You now have a fully-programmed brain for your LightSweeper board! Plug it in and get ready to play
  some 7-segment games!
