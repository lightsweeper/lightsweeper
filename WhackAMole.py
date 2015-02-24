
class WhackAMole():
    def __init__(self, display, audio, rows, cols):
        self.rows = rows
        self.cols = cols
        self.display = display
        self.audio = audio
        self.ended = False

    def heartbeat(self, sensorsChanged):
        pass

    def ended(self):
        pass
