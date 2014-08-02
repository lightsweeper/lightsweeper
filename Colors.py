BLACK = 0
RED = 1
GREEN = 2
YELLOW = 3
BLUE = 4
VIOLET = 5  # Really more pink than violet
CYAN = 6
WHITE = 7

def intToName(i):
    if i is BLACK:
        return "black"
    if i is RED:
        return "red"
    if i is GREEN:
        return "green"
    if i is YELLOW:
        return "yellow"
    if i is BLUE:
        return "blue"
    if i is VIOLET:
        return "violet"
    if i is CYAN:
        return "cyan"
    if i is WHITE:
        return "white"