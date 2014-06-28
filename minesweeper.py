#!/usr/bin/python3

import random
import pygame 

from board import Board, Cell
from inputs import ConsoleInput  
from outputs import ConsoleOutput

def create_board(width, height, mines):
    board = Board(tuple([tuple([Cell(False) for i in range(width)])
                         for j in range(height)]))
    available_pos = list(range((width-1) * (height-1)))
    for i in range(mines):
        new_pos = random.choice(available_pos)
        available_pos.remove(new_pos)
        (row_id, col_id) = (new_pos % (height-1), new_pos // (height-1))
        board.place_mine(row_id, col_id)
    return board



def main():
    SIZE_W = 6
    SIZE_H = 8
    MINES = 9

    # Initialize board
    board = create_board(SIZE_W, SIZE_H, MINES)
    console = ConsoleInput(board)
    output = ConsoleOutput(board)

    # Initialize audio channel - using only a single channel for now
    pygame.mixer.init(48000, -16, 1, 1024)
    channelA = pygame.mixer.Channel(1)
    
    # Initialize sounds
    startup_sound = pygame.mixer.Sound("sounds/StartUp.wav")
    success_sound = pygame.mixer.Sound("sounds/Success.wav")
    reveal_sound = pygame.mixer.Sound("sounds/Reveal.wav")
    blop_sound = pygame.mixer.Sound("sounds/Blop.wav")
    explosion_sound = pygame.mixer.Sound("sounds/Explosion.wav")

    channelA.play(startup_sound)

    #hacky clear screen 
    print(chr(27) + "[2J") 

    output.printboard()
    while board.is_playing and not board.is_solved:
        (row_id, col_id, is_flag) = console.get_move()
        if not is_flag:
            channelA.play(blop_sound)
            board.show(row_id, col_id)
        else:
            board.flag(row_id, col_id)        
        #hacky clear screen 
        print(chr(27) + "[2J") 
        output.printboard()

    if board.is_solved:
        channelA.play(success_sound)
        #hacky clear screen 
        print(chr(27) + "[2J") 
        print("Well done! You solved the board!")
    else:
        channelA.play(explosion_sound)
        #hacky clear screen 
        print(chr(27) + "[2J") 
        print("Uh oh! You blew up!")
        board.showall()
        output.printboard()
    wait = input("\n\nPress any key to return")
    
if __name__ == "__main__":
    main()