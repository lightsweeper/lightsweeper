import random

ZERO = 0x7E
ONE = 0x30
TWO = 0x6D
THREE = 0x79
FOUR = 0x33
FIVE = 0x5B
SIX = 0x7D
SEVEN = 0x70
EIGHT = 0x7F
NINE = 0x7B

DASH = 0x1

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
