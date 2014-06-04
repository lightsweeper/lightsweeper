from board import Board

class ConsoleInput(object):
	def __init__(self, b):
		self.board = b
	
	def is_valid(self, move_input):
	    if move_input == "H" or (len(move_input) not in (2, 3) or
	                             not move_input[:1].isdigit() or
	                             int(move_input[0]) not in range(len(self.board[0])) or
	                             int(move_input[1]) not in range(len(self.board))):
	        return False

	    if len(move_input) == 3 and move_input[2] != "f":
	        return False

	    return True

	def get_move(self):
	    INSTRUCTIONS = ("First, enter the column, followed by the row. To add or "
	                    "remove a flag, add \"f\" after the row (for example, 64f "
	                    "would place a flag on the 6th column, 4th row). Enter "
	                    "your move: ")

	    move = input("Enter your move (for help enter \"H\"): ")
	    if move == "H":
	        move = input(INSTRUCTIONS)

	    while not self.is_valid(move):
	        move = input("Invalid input. Enter your move (for help enter \"H\"): ")
	        if move == "H":
	            move = input(INSTRUCTIONS)

	    return (int(move[1]), int(move[0]), move[-1] == "f")
