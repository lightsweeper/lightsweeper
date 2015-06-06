
import random

from lsgame import *
import lsanimate

class FlyingWords(LSScreenSaver):
    

    def init(self):
        self.text = lsanimate.ScrollingText("LightSweeper", width=self.cols)
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


def main():
    gameEngine = LSGameEngine(FlyingWords) # Be sure to change this to reference your game
    gameEngine.beginLoop()

if __name__ == "__main__":
    main()
