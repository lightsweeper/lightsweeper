import time

def wait(seconds):
    currentTime = time.time()
    while time.time() - currentTime < seconds:
        pass
