import time

import Colors
import Shapes

HI_SCORE_CUTOFF = 5
class HighScores():
    def __init__(self, fname):
        #self.file = open(fname,mode='r')
        self.namesAndScores = [("God", "99"), ("Bob", "10"), ("Ass", "1")]
        self.scores = [99,10,1]
        if len(self.scores) < HI_SCORE_CUTOFF:
            self.highScoreThreshold = 0
        else:
            self.highScoreThreshold = self.scores[HI_SCORE_CUTOFF-1]

    def isHighScore(self, score):
        return score > self.highScoreThreshold

    def saveHighScore(self, name, score):
        if score < self.scores[len(self.scores) - 1]:
            self.scores.append(score)
            self.namesAndScores.append((name, str(score)))
            return
        for i in range(len(self.scores)):
            if self.scores[i] < score:
                self.scores.insert(i, score)
                self.namesAndScores.insert(i, (name, str(score)))

    def getHighScores(self, limit=10, start=0):
        result = []
        i = start
        while len(result) < limit and i < len(self.namesAndScores):
            result.append(self.namesAndScores[i])
            i += 1
        return result

class EnterName():
    def __init__(self, display, rows, cols, seconds=30):
        self.rows = rows
        self.cols = cols
        self.timer = CountdownTimer(seconds, self.timesUp, self.secondTick)
        self.display = display
        self.seconds = seconds
        self.currentText = "_" * (cols - 3)
        self.timestamp = time.time()
        self.enteringName = False
        self.rainbow = [Colors.RED, Colors.YELLOW, Colors.GREEN,Colors.CYAN,Colors.BLUE,Colors.MAGENTA]
        self.color = self.rainbow.pop(0)
        self.ended = False
        self.letterMap = []
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
        self.display.clearAll()
        if not self.enteringName:
            self.display.setMessage(1, "HIGH", self.color)
            self.display.setMessage(2, "SCORE", self.color)
            if len(self.rainbow) > 0:
                if time.time() - self.timestamp > 0.5:
                    self.color = self.rainbow.pop(0)
                    self.timestamp = time.time()
                return
            elif len(self.rainbow) == 0:
                self.enteringName = True
                #self.ended = True

        #display letters
        self.display.setMessage(0, self.currentText)
        for i in range(len(self.letterMap)):
            self.display.setMessage(i, self.letterMap[i])

        #check for letter pressed
        for move in sensorsChanged:
            self.currentText = self.currentText.replace('_', self.letterMap[move.row][move.col], 1)
            if '_' not in self.currentText:
                self.ended = True
        self.timer.heartbeat()

        #time left
        self.display.set(0, self.rows - 2, Shapes.digitToHex(int(self.timer.seconds / 10)), Colors.WHITE)
        self.display.set(0, self.rows - 1, Shapes.digitToHex(int(self.timer.seconds % 10)), Colors.WHITE)

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