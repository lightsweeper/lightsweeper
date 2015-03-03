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

def rgbToSegments(rgb):
    print(rgb)
    return([RED, RED, RED, RED, RED, RED, RED])

def segmentsToRgb(segments):
        #Segments:  A  B  C D E F G
    segmentMask = [64,32,16,8,4,2,1]
    r=0
    g=0
    b=0
    i=0
    for seg in map(intToRGB, segments):
        if seg[0] > 0:
            r+=segmentMask[i]
        if seg[1] > 0:
            g+=segmentMask[i]
        if seg[2] > 0:
            b+=segmentMask[i]
        i += 1
   # print("rgb -> {:d} {:d} {:d}".format(r,g,b))  #Debugging
    return([r,g,b])

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
    if i is MAGENTA:
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

def RAINBOW(firstColor = RED):
    rainbowList=[RED,YELLOW,GREEN,CYAN,BLUE,MAGENTA]
    i = rainbowList.index(firstColor)
    
    while True:
        if i is 6:
            i = 0
        yield intToRGB(rainbowList[i])
        i += 1
