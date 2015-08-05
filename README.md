lightsweeper
============

Lightsweeper - a burning man project


### Requirements:
  - Python version 3.2 or later
  - PyGame (http://www.pygame.org/)

 To use Lightsweeper with a real floor you will also need:
  - pyserial (http://pyserial.sourceforge.net/)


### Installation:

Download and install https://github.com/lightsweeper/lightsweeper-api
Edit the file lightsweeper.conf to reflect the locations of your games and sounds directories


### Usage:

 First run:

  > python util/LSFloorConfigure.py

 this will walk you through creating a floor configuration file. If you are not using
 a real floor just create a virtual configuration.

 Once configured, run:

  > python LightSweeper.py
