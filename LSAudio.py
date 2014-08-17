import pygame
import random

#this class serves as a common controller for audio
class Audio():
    SONG_END = pygame.USEREVENT + 1

    def __init__(self):
        pygame.mixer.init()
        pygame.init()
        self.loadedSongs = []

    def heartbeat(self):
        for event in pygame.event.get():
            if event.type == self.SONG_END:
                self.shuffleSongs()

    def loadSong(self, filename, name):
        #pygame.mixer.music.load("sounds/" + filename)
        self.loadedSongs.append(filename)
        pass

    def playSong(self, filename, loops=0):
        # pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
        # sound = pygame.mixer.Sound('Time_to_coffee.wav').play()
        pygame.mixer.music.load("sounds/" + filename)
        pygame.mixer.music.play(loops)

    def stopSong(self, fadeOut = 0.1):
        pass

    def setSongVolume(self, vol):
        pygame.mixer.music.set_volume(vol)

    #plays loaded songs in a random order
    def shuffleSongs(self):
        song = random.randint(0, len(self.loadedSongs) - 1)
        self.playSong(self.loadedSongs[song], 1)
        pygame.mixer.music.set_endevent(self.SONG_END)

    def playSound(self, filename):
        print("playing sound", filename)
        sound = pygame.mixer.Sound("sounds/" + filename)
        pygame.mixer.Sound.play(sound)
        #pygame.mixer.music.load("sounds/" + filename)
        #pygame.mixer.music.play(1)

    def stopSounds(self):
        pass

    def setSoundVolume(self, vol):
        pygame.mixer.Sound.set_volume(1.0)