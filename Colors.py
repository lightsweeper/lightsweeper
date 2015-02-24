import random

BLACK = 0
RED = 1
GREEN = 2
YELLOW = 3
BLUE = 4
MAGENTA = 5
VIOLET = MAGENTA # Deprecated
CYAN = 6
WHITE = 7

colorArray = ["black", "red", "green", "yellow", "blue", "violet", "cyan", "white"]

def intToName(i):
    return colorArray[i]

def intToRGB(i):
    if i is BLACK:
        return (0,0,0)
    if i is RED:
        return (255, 0, 0)
    if i is GREEN:
        return (0, 255, 0)
    if i is YELLOW:
        return (255, 255, 0)
    if i is BLUE:
        return (0, 0, 255)
    if i is VIOLET:
        return (255, 0, 255)
    if i is CYAN:
        return (0, 255, 255)
    if i is WHITE:
        return (255, 255, 255)
    return (0,0,0)

def RANDOM(exclude=None):
    def randC():
        ourRandC = random.randint(1,7)
        if exclude is not None:
            try:
                int(exclude)
            except:
                if ourRandC in exclude:
                    return randC()
                else:
                    return ourRandC
            finally:
                if ourRandC is exclude:
                    return randC()
                else:
                    return ourRandC
        else:
            return ourRandC
    
    return randC()
