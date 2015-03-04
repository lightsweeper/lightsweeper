import random

class _lsAudio:
    def __init__(self, initSound=True):
        self.soundVolume = 1.0
        self.loadedSongs = []
        self.soundDictionary = {}
        self.playSound('StartUp.wav')

    def heartbeat(self):
        pass

    def loadSong(self, filename, name):
        pass

    def playSong(self, filename, loops=0):
        pass

    def stopSong(self, fadeOut = 0.1):
        pass

    def setSongVolume(self, vol):
        pass

    #plays loaded songs in a random order
    def shuffleSongs(self):
        pass

    def loadSound(self, filename, name):
        pass

    def playSound(self, filename):
        pass

    def playLoadedSound(self, name):
        pass

    def stopSounds(self):
        pass

    def setSoundVolume(self, vol):
        pass


class _pygameAudio(_lsAudio):

    def __init__(self, initSound=True):
        print("Using pygame for Audio...")
        self.SONG_END = pygame.USEREVENT + 1
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        _lsAudio.__init__(self)

    def heartbeat(self):
        #for event in pygame.event.get():
        #    if event.type == self.SONG_END:
        #        self.shuffleSongs()
        pass

    def loadSong(self, filename, name):
        pygame.mixer.music.load("sounds/" + filename)
        self.loadedSongs.append(filename)
        pass

    def playSong(self, filename, loops=0):
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=256)
  #      sound = pygame.mixer.Sound('Time_to_coffee.wav').play()
        pygame.mixer.music.load("sounds/" + filename)
        pygame.mixer.music.play(loops)
        pass

    def stopSong(self, fadeOut = 0.1):
        pass

    def setSongVolume(self, vol):
        pygame.mixer.music.set_volume(vol)
        pass

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
        try:
            pygame.mixer.music.load("sounds/" + filename)
            pygame.mixer.music.play(1)
        except:
            print("Could not load file " + filename)

    def playLoadedSound(self, name):
        sound = self.soundDictionary[name]
        pygame.mixer.Sound.play(sound)

    def stopSounds(self):
        pass

    def setSoundVolume(self, vol):
        #print("setting sound vol:" + str(vol))
        #self.soundVolume = vol
        pass

try:
    import pygame
    lsAudioBackend = _pygameAudio
except:
    lsAudioBackend = _lsAudio
    print("No sound platform installed. Make sure pygame is installed with sdl mixer support.")

#this class serves as a common controller for audio
class LSAudio(lsAudioBackend):
    pass
