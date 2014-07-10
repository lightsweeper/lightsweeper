import random


class Cell(object):
    def __init__(self, is_mine, is_visible=False, is_flagged=False):
        self.is_mine = is_mine
        self.is_visible = is_visible
        self.is_flagged = is_flagged

    def show(self):
        self.is_visible = True

    def flag(self):
        self.is_flagged = not self.is_flagged

    def place_mine(self):
        self.is_mine = True


class Board():

    def __init__(self):
        super().__init__()
        self.is_playing = True

    def create_board(self, rows, cols, mines):
        print("creating board")
        self.board = tuple([tuple([Cell(False) for col in range(cols)])
                            for row in range(rows)])
        available_pos = list(range((rows-1) * (cols-1)))
        print("creating mines")
        for i in range(mines):
            new_pos = random.choice(available_pos)
            available_pos.remove(new_pos)
            (row_id, col_id) = (new_pos // (cols-1), new_pos % (rows-1))
            self.place_mine(row_id, col_id)
        self.is_playing = True
        return

    def mine_repr(self,row_id, col_id):
        # Debug only 
        # print ("min_repr for: ",row_id,col_id)
        cell = self.board[row_id][col_id]
        if cell.is_visible:
            if cell.is_mine:
                return "M"
            else:
                surr = self.count_surrounding(row_id, col_id)
                return str(surr) if surr else " "
        elif cell.is_flagged:
            return "F"
        else:
            return "."  #u"\uff18"

    def set_display(self, display):
        print("setting display")
        self.display = display
    
    def show(self, row_id, col_id):
        cell = self.board[row_id][col_id]
        if not cell.is_visible:
            print("board.show", row_id, col_id)
            cell.show()
            # self.display.show(row_id, col_id)
            if (cell.is_mine and not
                cell.is_flagged):
                self.is_playing = False
                print("mine'd!")
            elif self.count_surrounding(row_id, col_id) == 0:
                for (surr_row, surr_col) in self.get_neighbours(row_id, col_id):
                    if self.is_in_range(surr_row, surr_col):
                        self.show(surr_row, surr_col) 
	
    def showall(self):
        for row in self.board:
            for cell in row:
                cell.show()               
        
    def flag(self, row_id, col_id):
        cell = self.board[row_id][col_id]
        if not cell.is_visible:
            cell.flag()
        else:
            print("Cannot add flag, cell already visible.")

    def place_mine(self, row_id, col_id):
        self.board[row_id][col_id].place_mine()

    def count_surrounding(self, row_id, col_id):
        return sum(1 for (surr_row, surr_col) in self.get_neighbours(row_id, col_id)
                        if (self.is_in_range(surr_row, surr_col) and
                            self.board[surr_row][surr_col].is_mine))

    def get_neighbours(self, row_id, col_id):
        SURROUNDING = ((-1, -1), (-1,  0), (-1,  1),
                       (0 , -1),           (0 ,  1),
                       (1 , -1), (1 ,  0), (1 ,  1))
        return ((row_id + surr_row, col_id + surr_col) for (surr_row, surr_col) in SURROUNDING)

    def is_in_range(self, row_id, col_id):
        return 0 <= row_id < len(self.board) and 0 <= col_id < len(self.board[0])

    @property
    def remaining_mines(self):
        remaining = 0
        for row in self.board:
            for cell in row:
                if cell.is_mine:
                    remaining += 1
                if cell.is_flagged:
                    remaining -= 1
        return remaining
    
    def get_move(self, row, col):
        row_id = row
        col_id = col
        is_flag = False
        print("board get_move", row, col)
        if self.is_playing and not self.is_solved:
            if (row_id <0 or col_id < 0):
                print ("invalid row or col")
                return
            if not is_flag:
    #            channelA.play(blop_sound)
                self.show(row_id, col_id)
            else:
                print("Flagging:", row_id, col_id)
                self.flag(row_id, col_id)

        if self.is_solved:
    #        channelA.play(success_sound)
            print("Well done! You solved the board!")
        elif not self.is_playing:
    #        channelA.play(explosion_sound)
            print("Uh oh! You blew up!")
            self.showall()
            #self.display.showboard()
            #self.refreshboard()
        return   

    @property
    def is_solved(self):
        return all((cell.is_visible or cell.is_flagged) for row in self.board for cell in row)
		
