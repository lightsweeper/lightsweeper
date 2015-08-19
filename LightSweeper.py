#!/usr/bin/env python3

import imp
import multiprocessing
import os
import random
import time

from lightsweeper.lsgame import LSGameEngine
from lightsweeper.lsconfig import userSelect
from lightsweeper import lscartridge
from lightsweeper import lsconfig

conf = lsconfig.readConfiguration()
try:
    GAMESDIRS = [conf["GAMESDIR"]]
except KeyError:
    print("WARNING: 'GAMESDIR' is not set.")
    GAMESDIRS = [os.path.abspath(os.getcwd())]

NUMPLAYS = 0 # The number of games the player can play (0 is infinite/free play)

try:
    rfidcart = lscartridge.LSRFID()
except lscartridge.NoCartReader:
    print("No cartridge reader found.")
    rfidcart = False

if rfidcart != False:
    useCart = lsconfig.YESno("Would you like to use the rfid cartridge reader?")
    if not useCart:
        rfidcart = False

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
    if rfidcart is False:
        games = sorted([ g.__name__ for g in availableGames.values() ])

        games.append("Random")
        runningGame = multiprocessing.Process(target=nullGame)
        while True:
            clearTerm()
            print(" L I G H T S W E E P E R ")

            game = userSelect(games, "\nWhich game do you want?")

            if game is "Random":
                currentGame = list(availableGames.values())
            else:
                currentGame = availableGames[game]

            runningGame = multiprocessing.Process(target=runGame, args=(currentGame, conf.fileName))
            runningGame.start()
            while runningGame.is_alive():
                pass

    else:
        while True:
            bannerPrinted = False
            clearTerm()
            while not rfidcart.gameRunning:
                if not bannerPrinted:
                    print(" L I G H T S W E E P E R ")
                    print("\nInsert a game cartridge.")
                    print("(Or press Ctrl-C to exit.)")
                bannerPrinted = True
            time.sleep(0.5) # Give the cartridge reader a moment to initialize the cart
            print(rfidcart.gameID)
            if rfidcart.loadHint is not False:
                try:
                    currentGame = availableGames[rfidcart.loadHint]
                except KeyError:
                    print("Cannot find any game using the hint: '{:s}'".format(rfidcart.loadHint))
                    exit()

            runningGame = multiprocessing.Process(target=runGame, args=(currentGame, conf.fileName))
            runningGame.start()
            while rfidcart.gameRunning:
                pass
            runningGame.terminate()

def runGame(gameObject, configurationFileName):
    gameEngine = LSGameEngine(gameObject, configurationFileName)
    try:
        gameEngine.beginLoop(plays=NUMPLAYS)
    except EOFError:
        return

def nullGame():
    pass

#class runGame(multiprocessing.Process):
#    def __init__(self, gameObject, configurationFileName):
#        super().__init__(name='TEST')
#        self.gameEngine = LSGameEngine(gameObject, configurationFileName)

#    def run(self):
#        self.gameEngine.beginLoop(plays=NUMPLAYS)


if __name__ == '__main__':
    main()
