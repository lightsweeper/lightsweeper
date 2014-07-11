#!/usr/bin/python3

import random

from board import Board
from inputs import ConsoleInput
from outputs import ConsoleOutput

def main():
    ROWS = 6
    COLS = 8
    MINES = 9

    # Initialize board
    board = Board()
    board.create_board(ROWS, COLS, MINES)
    console = ConsoleInput(board)
    output = ConsoleOutput(board)

    # Initialize audio channel - using only a single channel for now
    #pygame.mixer.init(48000, -16, 1, 1024)
    #channelA = pygame.mixer.Channel(1)
    
    # Initialize sounds
    #startup_sound = pygame.mixer.Sound("sounds/StartUp.wav")
    #success_sound = pygame.mixer.Sound("sounds/Success.wav")
    #reveal_sound = pygame.mixer.Sound("sounds/Reveal.wav")
    #blop_sound = pygame.mixer.Sound("sounds/Blop.wav")
    #explosion_sound = pygame.mixer.Sound("sounds/Explosion.wav")

    #channelA.play(startup_sound)

    #hacky clear screen 
    print(chr(27) + "[2J") 

    output.printboard()
    while board.is_playing and not board.is_solved():
        (row_id, col_id, is_flag) = console.get_move()
        if not is_flag:
            #channelA.play(blop_sound)
            board.show(row_id, col_id)
        else:
            board.flag(row_id, col_id)        
        #hacky clear screen 
        print(chr(27) + "[2J") 
        output.printboard()

    if board.is_solved():
        #channelA.play(success_sound)
        #hacky clear screen 
        print(chr(27) + "[2J") 
        print("Well done! You solved the board!")
    else:
        #channelA.play(explosion_sound)
        #hacky clear screen 
        print(chr(27) + "[2J") 
        print("Uh oh! You blew up!")
        board.show_all()
        output.printboard()
    wait = input("\n\nPress any key to return")
    
if __name__ == "__main__":
    main()
