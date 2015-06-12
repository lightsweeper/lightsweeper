lightsweeper
============

Lightsweeper - a burning man project


### Requirements:
  - Python version 3.2 or later
  - PyGame (http://www.pygame.org/)

 To use Lightsweeper with a real floor you will also need:
  - pyserial (http://pyserial.sourceforge.net/)


### Installation:

  > python setup.py install


### To use:

 First run:

  > python util/LSFloorConfigure.py

 this will walk you through creating a floor configuration file. If you are not using
 a real floor just create a virtual configuration.

 Once configured, run a game by calling it directly, e.g.:

  > python games/minesweeper.py

 or by accessing it through LightSweeper:

 > python LightSweeper.py
