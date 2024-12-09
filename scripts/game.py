import pygame
import sys
from time import time
from random import random

from scripts.colors import *
from scripts.constants import *
from scripts.utils import *

class Game:
    # ===== SINGLETON =====
    __instance = None
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(Game, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance


    def __init__(self):
        if (self.__initialized): return
        self.__initialized = True

        pygame.init()

        pygame.display.set_caption('Worms')
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.display = pygame.Surface((SCREEN_SIZE[0]//2, SCREEN_SIZE[1]//2))
        self.clock = pygame.time.Clock()
        self.target_fps = TARGET_FPS
        self.fps = FPS
        self.delta_time = 0   

        self.assets = {
            "bg": load_image('background.png'),
        }
        
        self.musics = {
            "default": pygame.mixer.Sound(MUSIC_PATH + 'music.wav'),
        }
        self.musics['default'].set_volume(0.5)

        self.sfx = {
            'ambience': pygame.mixer.Sound(SFX_PATH + 'ambience.wav'),
        }
        self.sfx['ambience'].set_volume(0.2)

        self.tilemap = True  #TODO
        self.players = []

        self.screenshake   = 0

    
    def run(self):
        prev_time = time()

        self.musics['default'].play(-1)
        self.sfx['ambience'].play(-1)

        while True:
            # DELTA TIME
            self.delta_time = (time() - prev_time) * self.target_fps
            prev_time = time()

            # ==================== START EVENT ==================== #
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            # ==================== END EVENT ==================== #


            # ==================== START UPDATE ==================== #
            
            # ==================== END UPDATE ==================== #


            # ==================== START RENDER ==================== #
            self.display.blit(self.assets['bg'], (0, 0))

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), ((random() * self.screenshake - self.screenshake / 2), (random() * self.screenshake - self.screenshake / 2)))
            
            pygame.display.update()
            self.clock.tick(self.fps)
            # ==================== END RENDER ==================== #