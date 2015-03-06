import time

import Colors

HI_SCORE_CUTOFF = 3
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
        print("Scoreboard save score: " + name, str(score))

    def getHighScores(self, limit=10, start=0):
        result = []
        i = start
        while len(result) < limit and i < len(self.namesAndScores):
            result.append(self.namesAndScores[i])
            i += 1
        return result

class EnterName():
    def __init__(self, display, rows, cols, seconds=15):
        self.rows = rows
        self.cols = cols
        self.timer = CountdownTimer(seconds, self.timesUp, self.secondTick)
        self.display = display
        self.seconds = seconds
        self.currentText = "_" * (cols - 2)
        self.timestamp = time.time()
        self.enteringName = False
        self.rainbow = [Colors.RED, Colors.YELLOW, Colors.GREEN,Colors.CYAN,Colors.BLUE,Colors.MAGENTA]
        self.ended = False
        pass

    def heartbeat(self, sensorsChanged):
        if not self.enteringName:
            if len(self.rainbow) > 0:
                if time.time() - self.timestamp > 0.5:
                    color = self.rainbow.pop(0)
                    self.display.setMessage(0, "HIGH", color)
                    self.display.setMessage(1, "SCORE", color)
                    self.timestamp = time.time()
                return
            elif len(self.rainbow) == 0:
                #self.enteringName = True
                self.ended = True

        self.display.setMessageSplit(0, self.currentText, str(self.seconds))
        alphabet = "abcdefghijklmnopqrtuvwxyz"
        left = 0
        right = self.cols
        for r in range(1, self.rows):
            msg = alphabet[left:right]
            self.display.setMessage(r, msg)
            left += self.cols
            right += self.cols
        self.timer.heartbeat()

    def timesUp(self):
        pass

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