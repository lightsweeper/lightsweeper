#!/usr/bin/python3

import copy
import random
import time
from collections import defaultdict

from lsgame import *

class Snake(LSGame):

    def init (self):
        self.frameRate = 3
        self.state = list()             # This will keep track of the state of the board
        for r in range(0, self.rows):
            self.state.append(list())
            for c in range(0, self.cols):
                self.state[r].append([Colors.BLACK] * 7)

        # Snake initial values
        self.snakeColor = Colors.WHITE  # The color of the snake
        self.snake = [self.center()]    # Each item of the list is a section of the snake: (row, col, segment)
        self.direction = "v"            # The direction of the snake's travel: ^, v, <, >

        self.foodColor = Colors.RAINBOW()
        self.snakeFood = self.feedTheSnake()

    def heartbeat(self, sensors):
        self.morselColor = next(self.foodColor)
        if self.morselColor == self.snakeColor:             # Don't make food the same color as the snake, it's confusing!
            self.morselColor = next(self.foodColor)
        self.addSegment(self.snakeFood, self.morselColor)
        if len(sensors) is 0:
            self.slitherForward()
        else:
            self.left = 0
            self.right = 0
            self.straight = 0

            for move in sensors:
                if self.nearHead(move.row, move.col):
                    self.flee(move)
                else:
                    self.follow(move)
            self.moveSnake(self.left, self.right)

    def nearHead (self, row, col):
        # Returns true if the tile is within one space of the head of the snake
        (r, c, s) = self.snake[0]
        if row in range(r-1, r+1):
            if col in range(c-1, c+1):
                return True
        return False

    def flee (self, move):
        (r, c, s) = self.snake[0]
        if self.direction == "^":
            if move.col < c:
                self.right += move.val
            elif move.col > c:
                self.left += move.val
            else:
                self.randomVote(1000)
        elif self.direction == "v":
            if move.col < c:
                self.left += move.val
            elif move.col > c:
                self.right += move.val
            else:
                self.randomVote(1000)
        elif self.direction == "<":
            if move.row < r:
                self.left += move.val
            elif move.row > r:
                self.right += move.val
            else:
                self.randomVote(1000)
        elif self.direction == ">":
            if move.row < r:
                self.right += move.val
            elif move.row > r:
                self.left += move.val
            else:
                self.randomVote(1000)

    def follow (self, move):
        (r, c, s) = self.snake[0]
        if self.direction == "^":
            if move.col < c:
                self.left += move.val
            elif move.col > c:
                self.right += move.val
            else:
                self.straight += move.val
        elif self.direction == "v":
            if move.col < c:
                self.right += move.val
            elif move.col > c:
                self.left += move.val
            else:
                self.straight += move.val
        elif self.direction == "<":
            if move.row < r:
                self.right += move.val
            elif move.row > r:
                self.left += move.val
            else:
                self.straight += move.val
        elif self.direction == ">":
            if move.row < r:
                self.left += move.val
            elif move.row > r:
                self.right += move.val
            else:
                self.straight += move.val

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
                self.randomVote()
                self.moveSnake(leftVotes, rightVotes)
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

    def gameOver(self):
        self.ended = True
        self.display.clearAll()
        if self.rows > 1 and self.cols > 3:
            r = int(self.rows/2)-1 # Row offset
            c = int(self.cols/2)-2
            self.display.set(r+0, c+1, Shapes.Y, Colors.WHITE)
            self.display.set(r+0, c+2, Shapes.O, Colors.WHITE)
            self.display.set(r+0, c+3, Shapes.U, Colors.WHITE)
            self.display.set(r+1, c+0, Shapes.L, Colors.WHITE)
            self.display.set(r+1, c+1, Shapes.O, Colors.WHITE)
            self.display.set(r+1, c+2, Shapes.S, Colors.WHITE)
            self.display.set(r+1, c+3, Shapes.E, Colors.WHITE)
            self.display.heartbeat()
            time.sleep(3)
        super().gameOver()

def main():
    gameEngine = LSGameEngine(Snake)
    gameEngine.beginLoop()

if __name__ == "__main__":
    main()