#!/usr/bin/env python3

import os
import random

from games.minesweeper import Minesweeper
from games.EightbitSoundboard import EightbitSoundboard
from games.MidiSoundboard import MidiSoundboard
from games.WhackAMole import WhackAMole
from games.Snake import Snake

from LightSweeper.lsgame import LSGameEngine
from LightSweeper.lsconfig import userSelect
import LightSweeper.lsconfig as lsconfig

NUMPLAYS = 0 # The number of games the player can play (0 is infinite/free play)


availableGames = dict([
                        ("Minesweeper", Minesweeper),
                 #       ("EightbitSoundboard", EightbitSoundboard),
                        ("WhackAMole", WhackAMole),
                 #       ("MidiSoundboard", MidiSoundboard),
                        ("Snake", Snake)
                      ])

def clearTerm():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clearTerm()
    conf = lsconfig.LSFloorConfig()
    conf.selectConfig()
    while True:
        clearTerm()
        print(" L I G H T S W E E P E R ")

        games = [ g.__name__ for g in availableGames.values() ]

        games.append("Random")

        game = userSelect(games, "\nWhich game do you want?")

        if game is "Random":
            currentGame = list(availableGames.values())
        else:
            currentGame = availableGames[game]

        gameEngine = LSGameEngine(currentGame, conf.fileName)
        gameEngine.beginLoop(plays=NUMPLAYS)

if __name__ == '__main__':
    main()
