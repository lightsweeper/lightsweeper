import random
#segment order starts at top (A) and works clockwise, with the center segment (G) last
SEG_A = 0b01000000
SEG_B = 0b00100000
SEG_C = 0b00010000
SEG_D = 0b00001000
SEG_E = 0b00000100
SEG_F = 0b00000010
SEG_G = 0b00000001

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
    else:
        return 0x0