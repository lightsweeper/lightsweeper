#!/usr/bin/env python3

import os
import random

from minesweeper import Minesweeper
from EightbitSoundboard import EightbitSoundboard
from MidiSoundboard import MidiSoundboard
from AnimTestbed import AnimTestbed
from WhackAMole import WhackAMole

from lsgame import LSGameEngine
from LSFloorConfigure import userSelect


availableGames = dict([
                        ("AnimTestbed", AnimTestbed),
                        ("Minesweeper", Minesweeper),
                        ("EightbitSoundboard", EightbitSoundboard),
                        ("WhackAMole", WhackAMole),
                        ("MidiSoundboard", MidiSoundboard)
                      ])


def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(" L I G H T S W E E P E R ")

    games = [ g.__name__ for g in availableGames.values() ]

    games.append("Random")

    game = userSelect(games, "\nWhich game do you want?")

    if game is "Random":
        game = random.choice(list(availableGames.keys()))

    currentGame = availableGames[game]

    print("\nPlaying {:s}...".format(currentGame.__name__))
    gameEngine = LSGameEngine(currentGame)
    gameEngine.beginLoop()

if __name__ == '__main__':
    main()
