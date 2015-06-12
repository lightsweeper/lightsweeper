#!/usr/bin/env python3

import time
import random

from lsapi import *

from lsapi.LSGameUtils import HighScores
from lsapi.LSGameUtils import CountdownTimer
from lsapi.LSGameUtils import EnterName

TIMEOUT = 5
FAST_TIMEOUT = 4
EXTREME_TIMEOUT = 4

class WhackAMole(LSGame):

    def init(self):
        self.moleTimeout = TIMEOUT
        self.startTimestamp = -1
        self.moles = []
        self.molesTimestamp = []
        self.deletables = []
        self.moleAppearanceTimes = [29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10,
                                    9, 8, 7, 6, 5, 5, 4, 4, 4, 3, 3, 3, 2, 2, 2, 2, 1, 1, 1]
        self.score = 0
        self.highScores = HighScores()
        self.winScreen = False
        self.winScreenTimestamp = -1
        self.enterName = None
        self.handlesEvents = True
        self.timer = CountdownTimer(30, self.timerFinished)
        self.showingHighScores = False

    def stepOn(self, row, col):
        if (row, col) in self.moles:
            self.score += 1
            self.audio.playSound("Blop.wav")
            self.deletables.append((row, col))
            self.display.set(row, col, Shapes.DASH, Colors.YELLOW)

    def heartbeat(self, activeSensors):
        #show appropriate win screen
        ts = time.time()
        if self.winScreen:
            if self.enterName is not None:
                self.enterName.heartbeat(activeSensors)
                if self.enterName.ended:
                    self.highScores.saveHighScore(self.enterName.currentText, self.score)
                    self.enterName = None
                    self.winScreenTimestamp = ts
            elif ts - self.winScreenTimestamp > 6:
                self.over()
            elif not self.showingHighScores:
                self.over()
          #      self.display.setAll(Shapes.ZERO, Colors.BLACK)
         #       self.display.showHighScores(self.highScores.getHighScores())
        #        self.showingHighScores = True                      # TODO: pass highscores to LSGameEngine with game.over
            return

        #update timer
        self.timer.heartbeat()

        #delete expired moles
        for i in range(len(self.moles)):
            if ts - self.molesTimestamp[i] > self.moleTimeout and self.moles[i] not in self.deletables:
                self.deletables.append(self.moles[i])
        for d in self.deletables:
            i = self.moles.index(d)
            self.moles.pop(i)
            self.molesTimestamp.pop(i)
            self.display.set(d[0], d[1], Shapes.ZERO, Colors.BLACK)
        self.deletables = []

        #check for moles scheduled to appear
        while len(self.moleAppearanceTimes) > 0 and self.moleAppearanceTimes[0] > self.timer.seconds:
            self.moleAppearanceTimes.pop(0)
        if len(self.moleAppearanceTimes) > 0 and self.moleAppearanceTimes[0] == self.timer.seconds:
            self.moleAppearanceTimes.pop(0)
            r = random.randint(1, self.rows-1)
            c = random.randint(0, self.cols-1)
            iter = 0
            while (r,c) in self.moles and iter < 10:
                r = random.randint(1, self.rows-1)
                c = random.randint(0, self.cols-1)
                iter += 1
            self.moles.append((r,c))
            self.molesTimestamp.append(ts)
            self.display.set(r, c, Shapes.ZERO, Colors.YELLOW)

        if self.timer.seconds < 15:
            if self.timer.seconds < 5:
                self.moleTimeout = EXTREME_TIMEOUT
            else:
                self.moleTimeout = FAST_TIMEOUT
            self.display.set(0, 0, Shapes.digitToHex(int(self.timer.seconds / 10)), Colors.RED)
            self.display.set(0, 1, Shapes.digitToHex(int(self.timer.seconds % 10)), Colors.RED)
        else:
            self.display.set(0, 0, Shapes.digitToHex(int(self.timer.seconds / 10)), Colors.WHITE)
            self.display.set(0, 1, Shapes.digitToHex(int(self.timer.seconds % 10)), Colors.WHITE)
        for mole in self.moles:
            self.display.set(mole[0], mole[1], Shapes.ZERO, Colors.YELLOW)
        if self.score > 9:
            self.display.set(0, self.cols - 2, Shapes.digitToHex(int(self.score / 10)), Colors.WHITE)
        self.display.set(0, self.cols - 1, Shapes.digitToHex(self.score % 10), Colors.WHITE)

    def ended(self):
        return self.ended

    def timerFinished(self):
        self.audio.playSound("Success.wav")
        self.winScreen = True
        self.winScreenTimestamp = time.time()
        if self.highScores.isHighScore(self.score):
            self.enterName = EnterName(self.display, self.rows, self.cols, highScore=str(self.score))

def main():
    gameEngine = LSGameEngine(WhackAMole)
    gameEngine.beginLoop()

if __name__ == '__main__':
    main()
