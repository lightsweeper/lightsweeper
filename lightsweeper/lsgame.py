""" Contains methods responsible for running and interacting with LightSweeper games """

import copy
import json
import os
import random
import threading
import time

from collections import defaultdict

from lightsweeper.lsdisplay import LSDisplay
from lightsweeper.lsaudio import LSAudio
from lightsweeper.lsconfig import LSFloorConfig
from lightsweeper.lsconfig import userSelect


from lightsweeper import Colors
from lightsweeper import Shapes

FPS = 30

class LSGame():
    def __init__(game, display, audio, rows, cols):

        # Standard game setup
        game.display = display
        game.audio = audio
        game.rows = rows
        game.cols = cols
        game.ended = False
        game.duration = 0
        game.frameRate = FPS
        game.display.clearAll()

    def over (game, score=None):
        # TODO: Pass the score to a the scoreboard class
        print("[Game Over]")
        game.ended = True
        
class LSScreenSaver(LSGame):
    def __init__(game, *args, **kwargs):
        super().__init__(*args, **kwargs)
        game.duration = 5
        game.frameRate = 15

from lightsweeper.lsscreensavers import screensaverList

SAVERS = screensaverList


#enforces the framerate, pushes sensor data to games, and selects games
class LSGameEngine():
    initLock = threading.Event()
    SIMULATED_FLOOR = True
    CONSOLE = False
    numPlays = 0
    _warnings = []

    def __init__(self, GAME, floorConfig=None, loop=True):
        self.loop = loop
        self.wait = time.sleep
        if floorConfig is None:
            conf = LSFloorConfig()
            conf.selectConfig()
        else:
            conf = LSFloorConfig(floorConfig)
        if conf.containsVirtual() is True:
            self.REAL_FLOOR = False
        else:
            self.REAL_FLOOR = True

        self.ROWS = conf.rows
        self.COLUMNS = conf.cols
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Board size is {:d}x{:d}".format(self.ROWS, self.COLUMNS))
            
        self.GAME = GAME
        self.audio = LSAudio(initSound=True)
        self.display = LSDisplay(conf=conf, eventCallback = self.handleTileStepEvent, initScreen=True)
        self.moves = []
        self.sensorMatrix = defaultdict(lambda: defaultdict(int))
        self.newGame(self.GAME)

        #these are for bookkeeping
        self.frames = 0
        self.frameRenderTime = 0
        
        # This lock prevents handleTileStepEvent() from being run by polling loops before init is complete
        self.initLock.set()

    def newGame(self, Game):
        try: # Game is a list of game classes, pick one at random
            GAME = random.choice(Game)
        except: # Game was specified
            GAME = Game
        self.currentGame = GAME.__name__

        print("LSGameEngine: Starting {:s}...".format(self.currentGame))
        self.game = GAME(self.display, self.audio, self.ROWS, self.COLUMNS)
        self.startGame = time.time()
     #   game = self.game
     #   self.game.frameRate = FPS
        self.game.sensors = self.sensorMatrix
        self.numPlays += 1   # TODO: Check if type is screensaver
        try:
            self.game.init()
        except AttributeError:
            self._warnOnce("{:s} has no init() method.".format(self.currentGame))


    def beginLoop(self, plays = 0):
        while True:
            if plays is not 0 and self.numPlays <= plays:
                self.enterFrame()
            elif plays is 0:
                self.enterFrame()
            else:
                self.insertCoin()

    def insertCoin(self):
        self.gameOver()
        # TODO: Instead of quitting, go to game/demo screen and wait for someone to reset

    def gameOver(self):
        print(" G A M E  O V E R ")
        self.display.clearAll()
        self.display.setMessage(int(self.display.rows/2)-1,"GAME OVER")
        self.display.heartbeat()
        input("--Press any key to exit--\n")
        self.display.floor.saveAndExit(0)

    def handleTileStepEvent(self, row, col, sensorPcnt):
        self.initLock.wait()
        if int(sensorPcnt) is 0:
            try:
                self.game.stepOff(row, col)
            except AttributeError as e:   # Game has no stepOff() method
                if "object has no attribute 'stepOff'" in str(e):
                    self._warnOnce("{:s} has no stepOff() method.".format(self.currentGame))
                else:
                    raise(e)
         #   print("stepOff: ({:d},{:d})".format(row, col)) # Debugging
            self.moves = [x for x in self.moves if x[0] is not row and x[1] is not col]
        else:
            if self.sensorMatrix[row][col] is 0:
         #       if sensorPcnt > 20:                 # Only trigger > 20%, hack to guard against phantom sensors
         #                                           # TODO: This but better
                if sensorPcnt > 0:
                    try:
                        self.game.stepOn(row, col)
                    except AttributeError as e:   # Game has no stepOn() method
                        if "object has no attribute 'stepOn'" in str(e):
                            self._warnOnce("{:s} has no stepOn() method.".format(self.currentGame))
                        else:
                            raise(e)
                 #   print("stepOn: ({:d},{:d})".format(row, col)) # Debugging
                    m = (row, col)
                    self.moves.append(m)
        self.sensorMatrix[row][col] = int(sensorPcnt)

    def pauseGame (self):
        print("Game is paused.")
        while self.game.frameRate < 1:
            pass
        print("Game resuming...")

    def enterFrame(self):
        if self.game.duration is not 0:
            playTime = (time.time() - self.startGame)
            if playTime > self.game.duration:
            #    self.game.ended = True
                self.newGame(self.GAME)
        startEnterFrame = time.time()
        if not self.game.ended:
            self.game.heartbeat(self.moves)
            self.display.heartbeat()
            self.audio.heartbeat()
        else:
            self.newGame(SAVERS)    # Super hacky, should be in gameOver
         #   self.newGame(self.GAME)
        frameRenderTime = (time.time() - startEnterFrame)
        self.wait(self.padFrame(frameRenderTime))

    def padFrame(self, renderTime):
        if self.game.frameRate is 0:
            self.pauseGame()
        spaces = " " * 15
        fps = 1.0/renderTime
        if fps < self.game.frameRate or self.game.frameRate < 0:
            print("{1:s}{0:.4f} FPS".format(1.0/renderTime, spaces), end="\r")
            return(0)
        else:
            print("{1:s}{0:.4f} FPS".format(self.game.frameRate, spaces), end="\r")
            return((1.0/self.game.frameRate)-renderTime)
        print(spaces * 2, end="\r")

    def _warnOnce(self, warning):
        if warning not in self._warnings:
            print("WARNING: {:s}".format(warning))
            self._warnings.append(warning)


HI_SCORE_CUTOFF = 5
class HighScores():
    def __init__(self, fname="scores", writeToSerial=False):
        self.writeToSerial = writeToSerial
        #load scores from the card
        if self.writeToSerial:
            import serial
        #load in scores from a file
        else:
            self.fname = fname
            with open(fname) as f:
                self.namesAndScores = json.load(f)
            self.scores = []
            for entry in self.namesAndScores:
                self.scores.append(int(entry[1]))
            if len(self.scores) < HI_SCORE_CUTOFF:
                self.highScoreThreshold = 0
            else:
                self.highScoreThreshold = self.scores[HI_SCORE_CUTOFF-1]

    def isHighScore(self, score):
        #TODO: modify somehow to enable lower scores to be better depending on the game
        return score > self.highScoreThreshold

    def saveHighScore(self, name, score):
        if not self.isHighScore(score):
            return
        if self.writeToSerial:
            pass
        else:
            if score < self.scores[len(self.scores) - 1]:
                self.scores.append(score)
                self.namesAndScores.append((name, str(score)))
                with open(self.fname, 'w') as f:
                    f.dump(self.namesAndScores)
                return
            for i in range(len(self.scores)):
                if self.scores[i] < score:
                    self.scores.insert(i, score)
                    self.namesAndScores.insert(i, (name, str(score)))
                    with open(self.fname, 'w') as f:
                        json.dump(self.namesAndScores, f)
                    return

    def getHighScores(self, limit=10, start=0):
        if self.writeToSerial:
            pass
        else:
            result = []
            i = start
            while len(result) < limit and i < len(self.namesAndScores):
                result.append((self.namesAndScores[i][0], str(self.namesAndScores[i][1])))
                i += 1
            return result

class EnterName():
    def __init__(self, display, rows, cols, seconds=30, highScore = None):
        print("EnterName init()")
        self.rows = rows
        self.cols = cols
        self.timer = CountdownTimer(seconds, self.timesUp, self.secondTick)
        self.display = display
        self.display.clearAll()
        self.seconds = seconds
        self.currentText = "_" * cols
        self.timestamp = time.time()
        self.enteringName = False
        self.rainbow = [Colors.RED, Colors.YELLOW, Colors.GREEN,Colors.CYAN,Colors.BLUE,Colors.MAGENTA]
        self.color = self.rainbow.pop(0)
        self.ended = False
        self.letterMap = []
        self.highScore = highScore
        alphabet = "abcdefghijklnopqrstuUyz"
        i = 0
        for r in range(rows):
            currentRow = []
            if r == 0:
                pass
            else:
                for c in range(cols):
                    currentRow.append(alphabet[i:i+1])
                    i += 1
            self.letterMap.append(currentRow)

    def heartbeat(self, sensorsChanged):
        if not self.enteringName:
            self.display.setMessage(1, "HIGH", self.color)
            self.display.setMessage(2, "SCORE", self.color)
            if self.highScore is not None:
                self.display.setMessage(3, str(self.highScore), Colors.WHITE)

            if len(self.rainbow) > 0:
                if time.time() - self.timestamp > 0.5:
                    self.color = self.rainbow.pop(0)
                    self.timestamp = time.time()
                return
            elif len(self.rainbow) == 0:
                self.enteringName = True
                #self.ended = True

        #display letters
        self.display.setMessage(0, self.currentText, color = Colors.CYAN)
        for i in range(len(self.letterMap)):
            self.display.setMessage(i, self.letterMap[i])

        #check for letter pressed
        for move in sensorsChanged:
            try:
                self.currentText = self.currentText.replace('_', self.letterMap[move.row][move.col], 1)
                print("stepped on", self.letterMap[move.row][move.col], "text", self.currentText)
            except:
                pass
            if '_' not in self.currentText:
                self.ended = True
        self.timer.heartbeat()

        #time left
        self.display.set(self.rows - 1, self.cols - 2, Shapes.digitToHex(int(self.timer.seconds / 10)), Colors.YELLOW)
        self.display.set(self.rows - 1, self.cols - 1, Shapes.digitToHex(int(self.timer.seconds % 10)), Colors.YELLOW)

    def timesUp(self):
        self.ended = True

    def secondTick(self):
        pass

class CountdownTimer():
    def __init__(self, countdownFrom, finishCallback, secondCallback=None, minuteCallback=None):
        self.countdownFrom = countdownFrom
        self.seconds = countdownFrom
        self.secondCallback = secondCallback
        self.minuteCallback = minuteCallback
        self.finishCallback = finishCallback
        self.timestamp = time.time()
        self.done = False

    def heartbeat(self):
        if self.done:
            return
        ts = time.time()
        if ts - self.timestamp > 1:
            self.timestamp = ts
            self.seconds -= 1
            if self.seconds == 0:
                self.finishCallback()
                self.done = True
                return
            elif self.secondCallback is not None:
                self.secondCallback()
            elif self.seconds % 60 == 0:
                self.minuteCallback()

def main():
    print("TODO: testing lsgame")

if __name__ == '__main__':
    main()
