#we want a sound to play for each tile when it is stepped on
import LSGameAPI
class SoundBoard(LSGameAPI):
    def __init__(self):
        print("init")

    def heartbeat(self, sensorsChanged):
        print("heartbeat")

    def ended(self):
        return False