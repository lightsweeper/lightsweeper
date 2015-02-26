import random

#the minesweeper board
class Cell(object):
    def __init__(self, is_mine, is_visible=False, is_flagged=False):
        self.is_mine = is_mine
        self.is_visible = is_visible
        self.is_flagged = is_flagged
        self.is_defused = False

    def show(self):
        self.is_visible = True

    def flag(self):
        self.is_flagged = not self.is_flagged

    def place_mine(self):
        self.is_mine = True

    def set_defused(self):
        if self.is_mine:
            self.is_defused = True


class Board():

    def __init__(self):
        super().__init__()
        self.is_playing = True

    def create_board(self, rows, cols, mines):
        print("creating board")
        self.board = tuple([tuple([Cell(False) for col in range(cols)])
                            for row in range(rows)])
        available_pos = list(range((rows) * (cols)))
        print("creating mines")
        for i in range(mines):
            new_pos = random.choice(available_pos)
            available_pos.remove(new_pos)
            (row_id, col_id) = random.randint(0, rows-1), random.randint(0, cols-1) #(new_pos // (cols), new_pos % (rows))
            self.place_mine(row_id, col_id)
        self.is_playing = True
        return

    def getCellState(self,row_id, col_id):
        # print ("min_repr for: ",row_id,col_id)
        cell = self.board[row_id][col_id]
        if cell.is_defused:
            return "D"
        elif cell.is_visible:
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
        self.showingMultiple = False
        #print("given:", row_id, col_id, "board:", len(self.board), len(self.board[0]))
        cell = self.board[row_id][col_id]
        if not cell.is_visible:
            #print("board.show", row_id, col_id)
            cell.show()
            # self.display.show(row_id, col_id)
            if (cell.is_mine and not cell.is_flagged):
                self.is_playing = False
                print("mine'd!")
            elif self.is_solved():
                self.is_playing = False
            elif self.count_surrounding(row_id, col_id) == 0:
                self.showingMultiple = True
                for (surr_row, surr_col) in self.get_neighbours(row_id, col_id):
                    if self.is_in_range(surr_row, surr_col):
                        self.show(surr_row, surr_col) 

    def show_all(self):
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

    def remaining_mines(self):
        remaining = 0
        for row in self.board:
            for cell in row:
                if cell.is_mine and not cell.is_visible:
                    remaining += 1
                if cell.is_flagged:
                    remaining -= 1
        return remaining
    
    def remaining_hidden(self):
        remaining = 0
        for row in self.board:
            for cell in row:
                if not cell.is_visible:
                    remaining += 1
        return remaining

    def set_all_defused(self):
        for row in self.board:
            for cell in row:
                cell.set_defused()
        self.is_playing = False

    def is_solved(self):
        #return all((cell.is_visible or cell.is_flagged) for row in self.board for cell in row)
        #print("Remaining Mines: ", self.remaining_mines(), " Remaining Hidden: ", self.remaining_hidden())
        return self.remaining_mines() == self.remaining_hidden()
