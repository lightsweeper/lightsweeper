#!/usr/bin/python3

import copy
import random
import time
from collections import defaultdict

from lsapi import *

class Snake(LSGame):

    def init (game):
        game.speed = 2
        game.state = list()             # This will keep track of the state of the board
        for r in range(0, game.rows):
            game.state.append(list())
            for c in range(0, game.cols):
                game.state[r].append([Colors.BLACK] * 7)

        # Snake initial values
        game.snakeColor = Colors.WHITE  # The color of the snake
        game.snake = [(0,int(game.cols/2),5)]    # Each item of the list is a section of the snake: (row, col, segment)
        game.direction = "v"            # The direction of the snake's travel: ^, v, <, >

        game.foodColor = Colors.RAINBOW()
        game.snakeFood = game.feedTheSnake()
        game.frameRate = 0

    def heartbeat(game, activeSensors):
        game.updateMorsel()
        if len(game.sensors) is 0:
            game.slitherForward()
        else:
            game.left = 0
            game.right = 0
            game.straight = 0

            for rowCol in activeSensors:
                row = rowCol[0]
                col = rowCol[1]
                if game.nearHead(row, col):
                    game.flee(row, col)
                else:
                    game.follow(row, col)
            game.moveSnake(game.left, game.right)

    def stepOn(game, row, col):
        if game.frameRate is 0:
            game.frameRate = game.speed

    def updateMorsel (self):
        self.morselColor = next(self.foodColor)
        if self.morselColor == self.snakeColor:             # Don't make food the same color as the snake, it's confusing!
            self.morselColor = next(self.foodColor)
        self.addSegment(self.snakeFood, self.morselColor)

    def nearHead (self, row, col):
        # Returns true if the tile is within one space of the head of the snake
        (r, c, s) = self.snake[0]
        if row in range(r-1, r+1):
            if col in range(c-1, c+1):
                return True
        return False

    def flee (self, row, col):
        sensorPcnt = self.sensors[row][col]
        (r, c, s) = self.snake[0]
        if self.direction == "^":
            if col < c:
                self.right += sensorPcnt
            elif col > c:
                self.left += sensorPcnt
            else:
                self.randomVote(sensorPcnt * 2)
        elif self.direction == "v":
            if col < c:
                self.left += sensorPcnt
            elif col > c:
                self.right += sensorPcnt
            else:
                self.randomVote(sensorPcnt * 2)
        elif self.direction == "<":
            if row < r:
                self.left += sensorPcnt
            elif row > r:
                self.right += sensorPcnt
            else:
                self.randomVote(sensorPcnt * 2)
        elif self.direction == ">":
            if row < r:
                self.right += sensorPcnt
            elif row > r:
                self.left += sensorPcnt
            else:
                self.randomVote(sensorPcnt * 2)

    def follow (self, row, col):
        sensorPcnt = self.sensors[row][col]
        (r, c, s) = self.snake[0]
        if self.direction == "^":
            if col < c:
                self.left += sensorPcnt
            elif col > c:
                self.right += sensorPcnt
            else:
                self.straight += sensorPcnt
        elif self.direction == "v":
            if col < c:
                self.right += sensorPcnt
            elif col > c:
                self.left += sensorPcnt
            else:
                self.straight += sensorPcnt
        elif self.direction == "<":
            if row < r:
                self.right += sensorPcnt
            elif row > r:
                self.left += sensorPcnt
            else:
                self.straight += sensorPcnt
        elif self.direction == ">":
            if row < r:
                self.left += sensorPcnt
            elif row > r:
                self.right += sensorPcnt
            else:
                self.straight += sensorPcnt

    def randomVote (self, votes):
        if random.choice([True, False]):
            self.left += votes
        else:
            self.right += votes

    def moveSnake(self, leftVotes, rightVotes):
        if leftVotes == rightVotes:
            if self.straight > 0:
                self.slitherForward()
            else:
                vote = random.choice([self.turnLeft, self.turnRight])
                vote()
        elif leftVotes > rightVotes:
            self.turnLeft()
        else:  # rightVotes > leftVotes
            self.turnRight()

    def addSegment (self, section, color):
        (row, col, seg) = section
        state = self.state[row][col]
        state[seg] = color
        self.state[row][col] = state
        self.display.setCustom(row, col, state)

    def delSegment (self, section):
        (row, col, seg) = section
        state = self.state[row][col]
        state[seg] = Colors.BLACK
        self.state[row][col] = state
        self.display.setCustom(row, col, state)

    def updateSnake (self, newHead):
        if self.moveLoses(newHead):
            self.gameOver()
            return
        snakeCopy = copy.copy(self.snake)
        self.addSegment(newHead, self.snakeColor)
        self.delSegment(self.snake[-1])
        for i in range(1, len(self.snake)):
            self.snake[i] = snakeCopy[i-1]
        self.snake[0] = newHead
        if newHead == self.snakeFood:
            self.growSnake()
            self.paintTheSnake(self.morselColor)
            self.snakeFood = self.feedTheSnake()

    def turnLeft (self):
        (row, col, seg) = self.snake[0]
        if self.direction == "^":
            if seg is 1:
                seg = 0
            elif seg is 2:
                seg = 6
            elif seg is 4:
                col -= 1
                seg = 6
            elif seg is 5:
                col -= 1
                seg = 0
            self.direction = "<"
            self.updateSnake((row, col, seg))
            return
        elif self.direction == "v":
            if seg is 1:
                col += 1
                seg = 6
            elif seg is 2:
                col += 1
                seg = 3
            elif seg is 4:
                seg = 3
            elif seg is 5:
                seg = 6
            self.direction = ">"
            self.updateSnake((row, col, seg))
            return
        elif self.direction == "<":
            if seg is 0:
                seg = 5
            elif seg is 3:
                row += 1
                seg = 5
            elif seg is 6:
                seg = 4
            self.direction = "v"
            self.updateSnake((row, col, seg))
            return
        elif self.direction == ">":
            if seg is 0:
                row -= 1
                seg = 2
            elif seg is 3:
                seg = 2
            elif seg is 6:
                seg = 1
            self.direction = "^"
            self.updateSnake((row, col, seg))
            return

    def turnRight (self):
        (row, col, seg) = self.snake[0]
        if self.direction == "^":
            if seg is 1:
                col += 1
                seg = 0
            elif seg is 2:
                col += 1
                seg = 6
            elif seg is 4:
                seg = 6
            elif seg is 5:
                seg = 0
            self.direction = ">"
            self.updateSnake((row, col, seg))
            return
        elif self.direction == "v":
            if seg is 1:
                seg = 6
            elif seg is 2:
                seg = 3
            elif seg is 4:
                col -= 1
                seg = 3
            elif seg is 5:
                col -= 1
                seg = 6
            self.direction = "<"
            self.updateSnake((row, col, seg))
            return
        elif self.direction == "<":
            if seg is 0:
                row -= 1
                seg = 4
            elif seg is 3:
                seg = 4
            elif seg is 6:
                seg = 5
            self.direction = "^"
            self.updateSnake((row, col, seg))
            return
        elif self.direction == ">":
            if seg is 0:
                seg = 1
            elif seg is 3:
                row += 1
                seg = 1
            elif seg is 6:
                seg = 2
            self.direction = "v"
            self.updateSnake((row, col, seg))
            return

    def slitherForward(self):
        (row, col, seg) = self.snake[0]
        if self.direction == "^":
            if seg is 1:
                row -= 1
                seg = 2
            elif seg is 2:
                seg = 1
            elif seg is 4:
                seg = 5
            elif seg is 5:
                row -= 1
                seg = 4
            self.updateSnake((row, col, seg))
            return
        elif self.direction == "v":
            if seg is 1:
                seg = 2
            elif seg is 2:
                row += 1
                seg = 1
            elif seg is 4:
                row += 1
                seg = 5
            elif seg is 5:
                seg = 4
            self.updateSnake((row, col, seg))
            return
        elif self.direction == "<":
            col -= 1
            self.updateSnake((row, col, seg))
            return
        elif self.direction == ">":
            col += 1
            self.updateSnake((row, col, seg))
            return

    def growSnake (self):
        self.snake.append(copy.copy(self.snake[-1]))

    def feedTheSnake (self):
        randRow = random.randint(0, self.rows-1)
        randCol = random.randint(0, self.cols-1)
        randSeg = random.randint(0, 5)              # Don't put food in the "dash" position
        food = (randRow, randCol, randSeg)
        if (randRow == 0 and randSeg in [0,3,4,5,6]) or (randRow == self.rows and randSeg in [0,1,2,3,6]):  # Don't put food on the edges
            return(self.feedTheSnake())
        elif (randCol == 0 and randSeg in [0,1,5]) or (randCol == self.cols and randSeg in [2,3,4]):          # it's just rude
            return(self.feedTheSnake())
        elif self.inSnake(food):      # Don't put food inside the snake
            return(self.feedTheSnake())
        else:
            return(food)   # Place the food pellet

    def paintTheSnake (self, color):
        self.snakeColor = color
        for section in self.snake:
            self.addSegment(section, color)

    def center (self):
        midRow = int(self.rows/2)
        midCol = int(self.cols/2)
        segment = 4
        location = (midRow, midCol, segment)
        return(location)

    def moveLoses(self, move):
        (r,c,s) = move
        if r >= self.rows or c >= self.cols or r < 0 or c < 0:
            return True
        if self.inSnake(move):
            return True
        return False

    def inSnake(self, move):
        for section in self.snake:
            if move == section:
                return True

    def gameOver(game):
        game.display.clearAll()
        if game.rows > 1 and game.cols > 3:
            r = int(game.rows/2)-1 # Row offset
            c = int(game.cols/2)-2
            game.display.set(r+0, c+1, Shapes.Y, Colors.WHITE)
            game.display.set(r+0, c+2, Shapes.O, Colors.WHITE)
            game.display.set(r+0, c+3, Shapes.U, Colors.WHITE)
            game.display.set(r+1, c+0, Shapes.L, Colors.WHITE)
            game.display.set(r+1, c+1, Shapes.O, Colors.WHITE)
            game.display.set(r+1, c+2, Shapes.S, Colors.WHITE)
            game.display.set(r+1, c+3, Shapes.E, Colors.WHITE)
            game.display.heartbeat()
            time.sleep(3)
        game.over()

def main():
    gameEngine = LSGameEngine(Snake)
    gameEngine.beginLoop()

if __name__ == "__main__":
    main()
