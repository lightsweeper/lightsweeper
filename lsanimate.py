from collections import defaultdict
import Shapes
import Colors

animation = list()

class LSFrameGen:

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.frame = defaultdict(lambda: defaultdict(int))

    # Allows you to edit an existing frame structure, if no colormask is set
    # then the tile will keep its current colormask
    def edit(self,row,col,shape=None,colormask=None):
        if colormask is None:
            try:
                colormask = self.frame[row][col][1]
            except TypeError:
                print("Frame warning: No colormask set for cell at ({:d},{:d})".format(row,col))
        if shape is None:
            try:
                shape = self.frame[row][col][0]
            except TypeError:
                print("Frame warning: No shape set for cell at ({:d},{:d})".format(row,col))
        self.frame[row][col] = [shape, colormask]

    def print(self):
        for row in self.frame:
            print([self.frame[row][col] for col in self.frame[row]])

    def get(self):
        frameOut = list()
        frameOut.append(self.cols)
        for row in self.frame:
            for col in self.frame:
                cell = self.frame[row][col]
         #       frameOut.append(row)
         #       frameOut.append(col)
                frameOut.append(cell[0])
                frameOut.append(cell[1][0])
                frameOut.append(cell[1][1])
                frameOut.append(cell[1][2])
        return(frameOut)  # frameOut is a list consisting of the number of columns in the frame
                          # followed by a repeating pattern of 4 integers, each representing a
                          # subsequent tile's shape, and red, green, and blue colormasks



def main():
    print("TODO: testing lsanimate")

    colormask = Colors.segmentsToRgb([Colors.RED, Colors.RED])

    frame = LSFrameGen(2,2)
    frame.edit(1,1,Shapes.ZERO, colormask)
    frame.edit(1,1,Shapes.SEVEN)
    frame.edit(1,2,Shapes.ONE, colormask)
    frame.edit(2,2,Shapes.ZERO, colormask)
    frame.edit(2,1,Shapes.ONE, colormask)

    frame.print()
    print("")
    print(frame.get())

if __name__ == '__main__':
    main()
