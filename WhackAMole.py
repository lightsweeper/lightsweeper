import time
import random

import Colors
import Shapes

TIMEOUT = 3
FAST_TIMEOUT = 1.8
EXTREME_TIMEOUT = 1.2

class WhackAMole():
    def __init__(self, display, audio, rows, cols):
        self.rows = rows
        self.cols = cols
        self.display = display
        self.audio = audio
        self.ended = False
        self.moleTimeout = TIMEOUT
        self.startTimestamp = -1
        self.countdownClock = 30
        self.moles = []
        self.molesTimestamp = []
        self.score = 0

        self.display.setAll(Shapes.ZERO, Colors.BLACK)

    def heartbeat(self, sensorsChanged):
        ts = time.time()
        #update timer
        if self.startTimestamp is -1:
            self.startTimestamp = ts
        if ts - self.startTimestamp > 1.0:
            self.startTimestamp = ts
            self.countdownClock -= 1
            #if self.countdownClock < 6:
                #self.audio.playSound("tick.wav")
        if self.countdownClock is 0:
            self.audio.playSound("Success.wav")
            self.ended = True

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

        if self.countdownClock < 15:
            if self.countdownClock < 5:
                self.moleTimeout = EXTREME_TIMEOUT
            else:
                self.moleTimeout = FAST_TIMEOUT
            self.display.set(0, 0, Shapes.digitToHex(int(self.countdownClock / 10)), Colors.RED)
            self.display.set(0, 1, Shapes.digitToHex(int(self.countdownClock % 10)), Colors.RED)
        else:
            self.display.set(0, 0, Shapes.digitToHex(int(self.countdownClock / 10)), Colors.WHITE)
            self.display.set(0, 1, Shapes.digitToHex(int(self.countdownClock % 10)), Colors.WHITE)
        for mole in self.moles:
            self.display.set(mole[0], mole[1], Shapes.ZERO, Colors.YELLOW)
        if self.score > 9:
            self.display.set(0, self.cols - 2, Shapes.digitToHex(int(self.score / 10)), Colors.WHITE)
        self.display.set(0, self.cols - 1, Shapes.digitToHex(self.score % 10), Colors.WHITE)

    def ended(self):
        return self.ended

def main():
    import lsgame
    gameEngine = lsgame.LSGameEngine(WhackAMole)
    gameEngine.beginLoop()

if __name__ == '__main__':
    main()
