#!/usr/bin/env python3

import imp
import multiprocessing
import os
import random
import time


from copy import copy

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
except lscartridge.ReaderNotSupported as e:
    print("Cartridge reader is not supported: {:s}".format(str(e)))
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
    games = sorted([ g.__name__ for g in availableGames.values() ])
    if rfidcart is False:

        games = ["Random"] + games
        games.append("Exit")
        runningGame = multiprocessing.Process(target=nullGame)
        while True:
            clearTerm()
            print(" L I G H T S W E E P E R ")

            game = userSelect(games, "\nWhich game do you want?")

            if game == "Random":
                currentGame = list(availableGames.values())
            elif game == "Exit":
                exit()
            else:
                currentGame = availableGames[game]

            runningGame = multiprocessing.Process(target=runGame, args=(currentGame, conf.fileName))
            runningGame.start()
            while runningGame.is_alive():
                pass

    else:
        while True:
            errors = False
            bannerPrinted = False
            clearTerm()
            while not rfidcart.gameRunning:
                if not bannerPrinted:
                    print("\n")
                    print(" L I G H T S W E E P E R ")
                    print("\nInsert a game cartridge.")
                    print("(Or press Ctrl-C to exit.)")
                bannerPrinted = True
            print("Game ID: 0x{:x}".format(rfidcart.gameID))
            # TODO: Faster loading by indexing gameID over load hint
            while not rfidcart.loaded:
                pass # Give the cartridge reader a moment to initialize the cart
            print("Load Hint: {:s}".format(repr(rfidcart.loadHint)))
            if rfidcart.loadHint is not False:
                try:
                    truncatedGames = dict() # Cartridges can only store 15 character game hints
                    for key, val in availableGames.items():
                        truncatedGames[key[:15]] = val
                    currentGame = truncatedGames[rfidcart.loadHint]
                except KeyError:
                    print("Cannot find any game using the hint: '{:s}'".format(rfidcart.loadHint))
                    print("Please eject cartridge.")
                    while rfidcart.gameRunning:
                        errors = True
            else:
                print("Unrecognized game cartridge!")
                if lsconfig.YESno("Would you like to configure it now?"):
                    game = userSelect(games, "\nWhich game should this cartridge activate?")
                    rfidcart.setHint(game)
                    currentGame = availableGames[game]
                else:
                    print("Please eject cartridge.")
                    while rfidcart.gameRunning:
                        errors = True

            if not errors:
                runningGame = multiprocessing.Process(target=runGame, args=(currentGame, conf.fileName, rfidcart))
                runningGame.start()
                while rfidcart.gameRunning:
                    pass
                runningGame.terminate()
                # Regain control of the serial handle
                rfidcart.serial.close()
                rfidcart.serial.open()
            else:
                bannerPrinted = False
                rfidcart.resetState()
                time.sleep(.5)

def runGame(gameObject, configurationFileName, cartReader=False):
    gameEngine = LSGameEngine(gameObject, configurationFileName, cartridgeReader = cartReader)
    try:
        gameEngine.beginLoop(plays=NUMPLAYS)
    except EOFError:
        return
    except Exception as e:
        print(e)
        return

def nullGame():
    pass


if __name__ == '__main__':
    main()
