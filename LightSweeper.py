#!/usr/bin/env python3

import imp
import os
import random

from lightsweeper.lsgame import LSGameEngine
from lightsweeper.lsconfig import userSelect
from lightsweeper import lsconfig

conf = lsconfig.readConfiguration()
try:
    GAMESDIRS = [conf["GAMESDIR"]]
except KeyError:
    print("WARNING: 'GAMESDIR' is not set.")
    GAMESDIRS = [os.path.abspath(os.getcwd())]

NUMPLAYS = 0 # The number of games the player can play (0 is infinite/free play)

availableGames = dict()

for searchDir in GAMESDIRS:
    gameFiles = [os.path.join(os.getcwd(),f) for f in os.listdir(searchDir) if f.endswith(".py")]
    
    for gamePath in gameFiles:
        gameName = os.path.splitext(os.path.basename(gamePath))[0]
        fp, pathname, description = imp.find_module(gameName, GAMESDIRS)
        try:
            gameModule = imp.load_module(gameName, fp, pathname, description)
        finally:
            fp.close()
        try:
            exec("from {:s} import {:s} as thisGame".format(gameName, gameName))
        except ImportError as e:
            print("Warning: Unable to import {:s} ({:s})".format(gameName, e))
        availableGames[gameName] = thisGame



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
