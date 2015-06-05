#!/usr/bin/python3

from lsgame import *    # Start by importing the namespace from lsgame

import random           # You can also import any other python modules you need
                        # to run your game

class HelloWorld(LSGame):   # Define a new class with the name of your game
                            # have it inherit LSGame
    """
        This is a very basic skeleton designed to help you learn how to write
        your own games for LightSweeper!

        Your game should inherit from lsgame.LSGame which provides some built-in
        variables and methods:

            game.rows       The number of rows available for your game
            game.cols       The number of columns available for your game
            game.sensors    A matrix of sensor data indexed by row and column

                Rows and columns are indexed from zero.
                Sensor values are between 0 and 100 with 0 meaning no one is
                stepping on the tile.

            Examples:
                # Get the sensor value of the tile in the first row and the last column
                > sensorValueInPercent = game.sensors[0][game.cols]

                # Get the sensor value of the tile in the 3rd row and the first column
                > sensorValueInPercent = game.sensors[2][0]


        Updating the game display (game.display):
            Your game also has access to an LSDisplay object which you can use
            to update the tiles of the LightSweeper board. Look in lsdisplay.py
            for more details on what functions this object supports.

            Examples:
                # Make all of the tiles display a green four:
                > game.display.setAll(Shapes.FOUR, Colors.GREEN)

                # Change the color of the upper left-most tile to blue:
                > row = 0
                > column = 0
                > game.display.setColor(row, column, Colors.BLUE)

                # Clear the display:
                > game.display.clearAll()

                # Write the word "DEADBEEF" on the display in yellow:
                > game.display.setMessage("DEADBEEF", Colors.YELLOW)

            When interacting with the display you should use the constants defined
            in Colors and Shapes, look in Colors.py and Shapes.py to see what is
            available.

        Changing the game's framerate:
            By default LightSweeper will attempt to run your game at 30 frames
            per second. If you'd like it to run at a different framerate you can
            adjust the value of game.frameRate.

            Examples:
                # Print the current frame rate in frames per second (fps):
                > print(game.frameRate)

                # Set the frame rate to 15 fps
                > game.frameRate = 15


        Making the game play sounds and music (game.audio):
            Look in lsaudio.py for more information.


        Ending the game:
            To end the game, just call game.over(). You can also pass this function
            a score if you'd like the game engine to track scoring for your game.

            Example:
            > score = 100
            > print("Congratulations! You scored 100 points!")
            > game.over(score)

    """


    def init(game):
        """
            The init function runs once each time your game begins. Use it to
            initialize the board and set up any variables you might need to
            track your game's state.
        """

        print("Hello world init()")
        for i in range(0, game.rows):
            for j in range(0, game.cols):
                game.display.set(i, j, Shapes.ZERO, Colors.RANDOM())


    def heartbeat(game, activeTiles):
        """
            This function gets called in a loop and is where the meat of your
            game logic will likely occur. The game engine attempts to call
            heartbeat a number of times per second equal to the value of
            game.frameRate. The variable activeTiles contains a list of tiles
            that are being actively triggered.
        """

        if len(activeTiles) > 0:
            print("Tiles currently being stepped on: " + repr(activeTiles))
        pass


    def stepOn(game, row, col):
        """
            This function is called every time a previously untriggered tile gets
            stepped on. The variables row and col refer to the row and column
            of the stepped-on tile.
        """

        print("Hello tile at: ({:d},{:d})".format(row,col))
        game.audio.playSound("Blop.wav")
        game.display.setColor(row, col, Colors.RANDOM())

    def stepOff(game, row, col):
        """
            This function is called every time a previously triggered tile gets
            stepped off of. The variables row and col refer to the row and column
            of the tile being vacated.
        """
        print("Goodbye tile at: ({:d},{:d})".format(row,col))
        game.over() # Cause game to end


# The following 5 lines are the magic that allows you run your game directly.
# You should include them at the end of every game you write.
def main():
    gameEngine = LSGameEngine(HelloWorld)
    gameEngine.beginLoop()

if __name__ == "__main__":
    main()
