""" Shortcuts for color constants """

import random

BLACK = 0
RED = 1
GREEN = 2
YELLOW = 3
BLUE = 4
MAGENTA = 5
CYAN = 6
WHITE = 7

colorArray = ["black", "red", "green", "yellow", "blue", "violet", "cyan", "white"]


def intToName(i):
    return colorArray[i]

    #Segments:  A  B  C D E F G
SEGMENTMASK = [64,32,16,8,4,2,1]

def unpack(b):
# Unpacks an int's binary flags
    while b:
        o = b&(~b+1)
        yield o
        b ^= o

def rgbToSegments(rgb):
    segments = [None] * 7
    for r in unpack(rgb[0]):
        segments[SEGMENTMASK.index(r)] = RED
    for g in unpack(rgb[1]):
        if segments[SEGMENTMASK.index(g)] is RED:
            segments[SEGMENTMASK.index(g)] = YELLOW
        else:
            segments[SEGMENTMASK.index(g)] = GREEN
    for b in unpack(rgb[2]):
        if segments[SEGMENTMASK.index(b)] is YELLOW:
            segments[SEGMENTMASK.index(b)] = WHITE
        elif segments[SEGMENTMASK.index(b)] is GREEN:
            segments[SEGMENTMASK.index(b)] = CYAN
        elif segments[SEGMENTMASK.index(b)] is RED:
            segments[SEGMENTMASK.index(b)] = MAGENTA
        else:
            segments[SEGMENTMASK.index(b)] = BLUE
    return(segments)

def segmentsToRgb(segments):
    (r,g,b) = (0,0,0)
    i=0
    for seg in map(intToRGB, segments):
        if seg[0] > 0:
            r+=SEGMENTMASK[i]
        if seg[1] > 0:
            g+=SEGMENTMASK[i]
        if seg[2] > 0:
            b+=SEGMENTMASK[i]
        i += 1
   # print("rgb -> {:d} {:d} {:d}".format(r,g,b))  #Debugging
    return([r,g,b])

def intToRGB(i):
    if i is 0:                  # BLACK
        return (0,0,0)
    if i is 1:                  # RED
        return (255, 0, 0)
    if i is 2:                  # GREEN
        return (0, 255, 0)
    if i is 3:                  # YELLOW
        return (255, 255, 0)
    if i is 4:                  # BLUE
        return (0, 0, 255)
    if i is 5:                  # MAGENTA
        return (255, 0, 255)
    if i is 6:                  # CYAN
        return (0, 255, 255)
    if i is 7:                  # WHITE
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

def RAINBOW(firstColor = RED):
    rainbowList=[RED,YELLOW,GREEN,CYAN,BLUE,MAGENTA]
    i = rainbowList.index(firstColor)
    
    while True:
        if i is 6:
            i = 0
        yield intToRGB(rainbowList[i])
        i += 1
