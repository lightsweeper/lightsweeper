import pygame
import random

#this class serves as a common controller for audio
class Audio():
    SONG_END = pygame.USEREVENT + 1

    def __init__(self):
        pygame.mixer.init()
        pygame.init()
        self.soundVolume = 1.0
        self.loadedSongs = []
        self.soundDictionary = {}

    def heartbeat(self):
        for event in pygame.event.get():
            if event.type == self.SONG_END:
                self.shuffleSongs()

    def loadSong(self, filename, name):
        pygame.mixer.music.load("sounds/" + filename)
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
        songCount = len(self.loadedSongs)
        song = random.randint(0, songCount - 1)
        print("songs", songCount)
        print("playing song", self.loadedSongs[song])
        self.playSong(self.loadedSongs[song], 1)
        pygame.mixer.music.set_endevent(self.SONG_END)

    def loadSound(self, filename, name):
        print("loading sound " + filename + " into " + name)
        sound = pygame.mixer.Sound("sounds/" + filename)
        self.soundDictionary[name] = sound

    def playSound(self, filename):
        print("playing sound", filename)
        sound = pygame.mixer.Sound("sounds/" + filename)
        sound.set_volume(self.soundVolume)
        pygame.mixer.Sound.play(sound)
        #pygame.mixer.music.load("sounds/" + filename)
        #pygame.mixer.music.play(1)

    def playLoadedSound(self, name):
        sound = self.soundDictionary[name]
        pygame.mixer.Sound.play(sound)

    def stopSounds(self):
        pass

    def setSoundVolume(self, vol):
        print("setting sound vol:" + str(vol))
        self.soundVolume = vol