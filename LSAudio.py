import pygame

#this class serves as a common controller for audio
class Audio():
    def __init__(self):
        # .mixer.init()
        pygame.mixer.init()
        pass

    def loadSong(self, filename, name):
        # pygame.mixer.music.load("sounds/" + filename)
        pass

    def playSong(self, filename, loops=0):
        # pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
        # sound = pygame.mixer.Sound('Time_to_coffee.wav').play()
        pygame.mixer.music.load("sounds/" + filename)
        pygame.mixer.music.play(loops)

    def stopSong(self, fadeOut = 0.1):
        pass

    def setSongVolume(self, vol):
        pass

    #plays loaded songs in a random order
    def shuffleSongs(self):
        pass

    def loadSound(self, filename, name):
        pass

    def playSound(self, name):
        pass

    def stopSounds(self):
        pass

    def setSoundVolume(self, vol):
        pass