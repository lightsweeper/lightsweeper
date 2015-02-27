
class WhackAMole():
    def __init__(self, display, audio, rows, cols):
        self.rows = rows
        self.cols = cols
        self.display = display
        self.audio = audio
        self.ended = False
        self.moleTimeout = 20
        self.moles = []
        self.molesTimeLeft = []

    def heartbeat(self, sensorsChanged):
        pass

    def ended(self):
        pass

def main():
    import LSGameEngine
    gameEngine = LSGameEngine.GameEngine(WhackAMole)
    gameEngine.beginLoop()

if __name__ == '__main__':
    main()
