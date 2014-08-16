from board import Board

class ConsoleOutput(object):
    def __init__(self, b):
        self.b = b
    
    def printboard(self):
        board_string = ("Mines: " + str(self.b.remaining_mines()) + "\n  " +
            "".join([str(i) for i in range(len(self.b.board[0]))]))
        for (row_id, row) in enumerate(self.b.board):
            board_string += ("\n" + str(row_id) + " " + 
                             "".join(self.b.mine_repr(row_id, col_id) for (col_id, _) in enumerate(row)) +
                             " " + str(row_id))
        board_string += "\n  " + "".join([str(i) for i in range(len(self.b.board[0]))])
        print(board_string)


