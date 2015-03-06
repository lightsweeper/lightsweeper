import random
#segment order starts at top (A) and works clockwise, with the center segment (G) last
SEG_A = 0b01000000
SEG_B = 0b00100000
SEG_C = 0b00010000
SEG_D = 0b00001000
SEG_E = 0b00000100
SEG_F = 0b00000010
SEG_G = 0b00000001

OFF = 0
ZERO = SEG_A + SEG_B + SEG_C + SEG_D + SEG_E + SEG_F
ONE = SEG_B + SEG_C
TWO = SEG_A + SEG_B + SEG_D + SEG_E + SEG_G
THREE = SEG_A + SEG_B + SEG_C + SEG_D + SEG_G
FOUR = SEG_B + SEG_C + SEG_F + SEG_G
FIVE = SEG_A + SEG_C + SEG_D + SEG_F + SEG_G
SIX = SEG_A + SEG_C + SEG_D + SEG_E + SEG_F + SEG_G
SEVEN = SEG_A + SEG_B + SEG_C
EIGHT = SEG_A + SEG_B + SEG_C + SEG_D + SEG_E + SEG_F + SEG_G
NINE = SEG_A + SEG_B + SEG_C + SEG_D + SEG_F + SEG_G

#letters not included: K (looks like H), M (two n's), W (two u's), X (looks like H)
A = SEG_A + SEG_B + SEG_C + SEG_E + SEG_F + SEG_G
B = SEG_C + SEG_D + SEG_E + SEG_F + SEG_G
C = SEG_A + SEG_D + SEG_E + SEG_F
D = SEG_B + SEG_C + SEG_D + SEG_E + SEG_G
E = SEG_A + SEG_D + SEG_E + SEG_F + SEG_G
F = SEG_A + SEG_E + SEG_F + SEG_G
G = SEG_A + SEG_B + SEG_C + SEG_D + SEG_F + SEG_G
H = SEG_C + SEG_E + SEG_F + SEG_G
I = SEG_B + SEG_C
i = SEG_C
J = SEG_B + SEG_C + SEG_D
K = SEG_B + SEG_C + SEG_E + SEG_F + SEG_G
L = SEG_D + SEG_E + SEG_F
N = SEG_C + SEG_E + SEG_G
O = SEG_C + SEG_D + SEG_E + SEG_G
P = SEG_A + SEG_B + SEG_E + SEG_F + SEG_G
Q = SEG_A + SEG_B + SEG_C + SEG_F + SEG_G
R = SEG_E + SEG_G
S = SEG_A + SEG_C + SEG_D + SEG_F + SEG_G
T = SEG_D + SEG_E + SEG_F + SEG_G
u = SEG_C + SEG_D + SEG_E
U = SEG_B + SEG_C + SEG_D + SEG_E + SEG_F
V = SEG_C + SEG_D
Y = SEG_B + SEG_C + SEG_D + SEG_F + SEG_G
Z = SEG_A + SEG_B + SEG_D + SEG_E + SEG_G

DASH = SEG_G

def digitToHex(digit):
    if digit is 0:
        return ZERO
    if digit is 1:
        return ONE
    if digit is 2:
        return TWO
    if digit is 3:
        return THREE
    if digit is 4:
        return FOUR
    if digit is 5:
        return FIVE
    if digit is 6:
        return SIX
    if digit is 7:
        return SEVEN
    if digit is 8:
        return EIGHT
    if digit is 9:
        return NINE

def randomDigitInHex():
    return digitToHex(random.randint(0, 9))

def hexToDigit(hex):
    if hex is ZERO:
        return 0
    if hex is ONE:
        return 1
    if hex is TWO:
        return 2
    if hex is THREE:
        return 3
    if hex is FOUR:
        return 4
    if hex is FIVE:
        return 5
    if hex is SIX:
        return 6
    if hex is SEVEN:
        return 7
    if hex is EIGHT:
        return 8
    if hex is NINE:
        return 9

#Does NOT return compound letters
def digitToLetter(digit):
    if digit is 0:
        return A
    if digit is 1:
        return B
    if digit is 2:
        return C
    if digit is 3:
        return D
    if digit is 4:
        return E
    if digit is 5:
        return F
    if digit is 6:
        return G
    if digit is 7:
        return H
    if digit is 8:
        return I
    if digit is 9:
        return J
    if digit is 10:
        return K
    if digit is 11:
        return L
    if digit is 12:
        return N
    if digit is 13:
        return O
    if digit is 14:
        return P
    if digit is 15:
        return Q
    if digit is 16:
        return R
    if digit is 17:
        return S
    if digit is 18:
        return T
    if digit is 19:
        return U
    if digit is 20:
        return V
    if digit is 21:
        return Y
    if digit is 22:
        return Z
    else:
        return 0x0

#Returns a list of shapes needed to make this letter, includes awkward ones like X / H / K
def charToShape(c):
    if c.lower() == 'a':
        return [A]
    if c.lower() == 'b':
        return [B]
    if c.lower() == 'c':
        return [C]
    if c.lower() == 'd':
        return [D]
    if c.lower() == 'e':
        return [E]
    if c.lower() == 'f':
        return [F]
    if c.lower() == 'g':
        return [G]
    if c.lower() == 'h':
        return [H]
    if c.lower() == 'i':
        return [I]
    if c.lower() == 'j':
        return [J]
    if c.lower() == 'k':
        return [K]
    if c.lower() == 'l':
        return [L]
    if c.lower() == 'm':
        return [N, N]
    if c.lower() == 'n':
        return [N]
    if c.lower() == 'o':
        return [O]
    if c.lower() == 'p':
        return [P]
    if c.lower() == 'q':
        return [Q]
    if c.lower() == 'r':
        return [R]
    if c.lower() == 's':
        return [S]
    if c.lower() == 't':
        return [T]
    if c.lower() == 'u':
        return [U]
    if c.lower() == 'v':
        return [V]
    if c.lower() == 'w':
        return [u,V]
    if c.lower() == 'x':
        return [H]
    if c.lower() == 'y':
        return [Y]
    if c.lower() == 'z':
        return [Z]
    if c.lower() == '1':
        return [ONE]
    if c.lower() == '2':
        return [TWO]
    if c.lower() == '3':
        return [THREE]
    if c.lower() == '4':
        return [FOUR]
    if c.lower() == '5':
        return [FIVE]
    if c.lower() == '6':
        return [SIX]
    if c.lower() == '7':
        return [SEVEN]
    if c.lower() == '8':
        return [EIGHT]
    if c.lower() == '9':
        return [NINE]
    if c.lower() == '0':
        return [ZERO]
    if c == '-':
        return [DASH]
    if c == '_':
        return [SEG_D]
    else:
        return [0x0]

def stringToShapes(s):
    shapes = []
    for c in s:
        shapes += charToShape(c)
    return shapes
