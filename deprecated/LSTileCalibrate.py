# Run this to calibrate a single tile's stepped-on sensor feedback

# Launch LSTileCalibrate
# Enter Row, Col index
# Read Stepped-On Sensor Reading
# Read Stepped-Off Sensor Reading
# Read previous EEPROM
# Previous Readings were: [Low/High], New Readings are: [Low/High] Do you wish to overwrite? [Y/N]
# Write to EEPROM

# Consider wrapping this into LSRealFloor main

import time

class TileCalibrate():
    FRAME_GAP = 1 / 30

    def __init__(self):
        pass

    def __init__(self):
        pass

    def beginLoop(self):
        while True:
            self.wait(self.FRAME_GAP)
            self.enterFrame()

    def wait(self, seconds):
        currentTime = time.time()
        while time.time() - currentTime < seconds:
            pass

    def enterFrame(self):
        sensorsChanged = self.pollSensors()

    def pollSensors(self):
        sensorsChanged = self.display.pollSensors()
        return sensorsChanged

def main():
    print("Starting Tile Calibrationr")
    tileCalibrate = TileCalibrate()
    tileCalibrate.beginLoop()

if __name__ == '__main__':
    main()