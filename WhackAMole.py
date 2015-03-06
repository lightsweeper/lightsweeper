import time
import random

import Colors
import Shapes
from LSGameUtils import HighScores
from LSGameUtils import CountdownTimer
from LSGameUtils import EnterName

TIMEOUT = 3
FAST_TIMEOUT = 1.8
EXTREME_TIMEOUT = 1.2

class WhackAMole():
    def __init__(self, display, audio, rows, cols):
        self.rows = rows
        self.cols = cols
        self.display = display
        self.audio = audio
        self.audio.setSoundVolume(0.2)
        self.ended = False
        self.moleTimeout = TIMEOUT
        self.startTimestamp = -1
        self.moles = []
        self.molesTimestamp = []
        self.score = 0
        self.highScores = HighScores("WhackAMole")
        self.winScreen = False
        self.winScreenTimestamp = -1
        self.enterName = None
        self.timer = CountdownTimer(30, self.timerFinished)
        self.display.setAll(Shapes.ZERO, Colors.BLACK)

    def heartbeat(self, sensorsChanged):
        #show appropriate win screen
        ts = time.time()
        if self.winScreen:
            if self.enterName is not None:
                self.enterName.heartbeat(sensorsChanged)
                if self.enterName.ended:
                    self.enterName = None
                    self.winScreenTimestamp = ts
            elif ts - self.winScreenTimestamp > 6:
                self.ended = True
            else:
                self.display.setAll(Shapes.ZERO, Colors.BLACK)
                self.display.showHighScores(self.highScores.getHighScores())
            return

        #update timer
        self.timer.heartbeat()

        deletables = []
        #check if mole is stepped on
        for move in sensorsChanged:
            if (move.row, move.col) in self.moles:
                self.score += 1
                self.audio.playSound("Blop.wav")
                deletables.append((move.row, move.col))

        #delete expired moles
        for i in range(len(self.moles)):
            if ts - self.molesTimestamp[i] > self.moleTimeout and self.moles[i] not in deletables:
                deletables.append(self.moles[i])
        for d in deletables:
            i = self.moles.index(d)
            mole = self.moles[i]
            self.display.set(mole[0], mole[1], Shapes.ZERO, Colors.BLACK)
            self.moles.pop(i)
            self.molesTimestamp.pop(i)

        #add new moles
        if random.randint(0, 20) < 1 and len(self.moles) < 4:
            r = random.randint(1, self.rows-1)
            c = random.randint(0, self.cols-1)
            if (r,c) not in self.moles:
                self.moles.append((r,c))
                self.molesTimestamp.append(ts)

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
            self.enterName = EnterName(self.display, self.rows, self.cols)

def main():
    import lsgame
    gameEngine = lsgame.LSGameEngine(WhackAMole)
    gameEngine.beginLoop()

if __name__ == '__main__':
    main()
