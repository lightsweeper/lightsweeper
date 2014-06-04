from board import Board

class ConsoleOutput(object):
    def __init__(self, b):
        self.board = b
    
    def printboard(self):
        board_string = ("Mines: " + str(self.board.remaining_mines) + "\n  " +
            "".join([str(i) for i in range(len(self.board[0]))]))
        for (row_id, row) in enumerate(self.board):
            board_string += ("\n" + str(row_id) + " " + 
                             "".join(self.board.mine_repr(row_id, col_id) for (col_id, _) in enumerate(row)) +
                             " " + str(row_id))
        board_string += "\n  " + "".join([str(i) for i in range(len(self.board[0]))])
        print(board_string)


