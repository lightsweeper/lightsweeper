
import random

from lsgame import *
import lsanimate

MESSAGE = "LightSweeper"

class FlyingWords(LSScreenSaver):
    
    def init(self):
        self.text = lsanimate.ScrollingText(MESSAGE, width=self.cols)
        self.surface = lsanimate.LSFrameGen(self.rows, self.cols)
        self.surface.fill((0,0,0))
        self.lastRow = random.randint(0, self.surface.rows-1)

    def heartbeat(self, activeSensors):
        self.text.color = Colors.RANDOM(exclude=self.text.color)
        outAnimation = lsanimate.LSAnimation()
        Frame = self.text.nextFrame()
        randomRow = self.lastRow = random.choice([x for x in range(0, self.surface.rows) if x != self.lastRow])
        for frame in Frame:
            outAnimation.addFrame(lsanimate.mergeFrames(self.surface.get(), frame, offset=(randomRow,0)))
        outAnimation.play(self.display, frameRate=5)


class RainbowZipper(LSScreenSaver):
    def init(self):
        text = lsanimate.ScrollingText(MESSAGE, color=Colors.RAINBOW(), width=self.cols)
        self.framesL = text._frames[:]
        text.direction = "right"
        self.framesR = text._frames[:]
        self.surface = lsanimate.LSFrameGen(self.rows, self.cols)
        self.surface.fill((0,0,0))

    def heartbeat(self, activeSensors):
        outAnimation = lsanimate.LSAnimation()
        for frame in map(lambda x, y: (x, y), self.framesL, self.framesR):
            thisFrame = self.surface.get()
            for i in range(self.surface.rows):
                if i % 2 is 0:
                    f = frame[0][:]
                else:
                    f = frame[1][:]
                thisFrame = lsanimate.mergeFrames(thisFrame, f, offset=(i,0))
            outAnimation.addFrame(thisFrame)
        outAnimation.play(self.display, frameRate=10)


def main():
    gameEngine = LSGameEngine(RainbowZipper)
    gameEngine.beginLoop()

if __name__ == "__main__":
    main()
