# TODO : Framerate independant gravity
from math import cos, sin

import pygame
import sys
from time import time
from random import random

from scripts.core.animation import Animation
from scripts.core.colors import *
from scripts.core.constants import *
from scripts.core.utils import *
from scripts.entities.player import Player
from scripts.features.timer import Timer


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
        self.render_scale = 1
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.display = pygame.Surface((SCREEN_SIZE[0] // self.render_scale, SCREEN_SIZE[1] // self.render_scale))
        self.clock = pygame.time.Clock()
        self.target_fps = TARGET_FPS
        self.fps = FPS
        self.delta_time = 0

        self.assets = {
            'bg': load_image('background.png'),
            'projectile': load_image('projectile.png'),

            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'spawners': load_images('tiles/spawners'),
            'stone': load_images('tiles/stone'),

            'player/idle': Animation(load_images('entities/player/idle'), 6),
            'player/run': Animation(load_images('entities/player/run'), 4),
            'player/jump': Animation(load_images('entities/player/jump')),
        }

        self.musics = {
            'default': pygame.mixer.Sound(MUSIC_PATH + 'music.wav'),
        }
        self.musics['default'].set_volume(0.5)

        self.sfx = {
            'ambience': pygame.mixer.Sound(SFX_PATH + 'ambience.wav'),
        }
        self.sfx['ambience'].set_volume(0.2)

        self.tilemap = load_map(self, "map.json")
        self.players = [
            Player(self, (0, 0), (8, 15)),
            Player(self, (0, 0), (8, 15)),
        ]

        self.movement = [[False, False], [False, False], ]
        self.scroll = [0, 0]
        self.screenshake = 0
        self.player_turn = 0

        pygame.time.set_timer(pygame.USEREVENT, 1000)
        self.timer = Timer(120, (50, 50))

        self.load_level()

    def load_level(self):
        self.player_turn = 0
        self.players[0].air_time = 0
        self.scroll = [0, 0]
        self.screenshake = 0

        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.players[0].pos = spawner['pos']
            elif spawner['variant'] == 1:
                self.players[1].pos = spawner['pos']

        self.scroll[0] = self.players[self.player_turn].rect().centerx - self.display.get_width() / 2
        self.scroll[1] = self.players[self.player_turn].rect().centery - self.display.get_height() / 2

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

                if event.type == pygame.USEREVENT:
                    self.timer.countdown()
                    if self.timer.is_finished():
                        self.timer.reset()
                        self.player_turn = (self.player_turn + 1) % 2
                        self.movement = [[False, False], [False, False], ]

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[self.player_turn][0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[self.player_turn][1] = True
                    if event.key == pygame.K_UP:
                        self.players[self.player_turn].start_charge_jump()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[self.player_turn][0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[self.player_turn][1] = False
                    if event.key == pygame.K_UP:
                        self.players[self.player_turn].jump()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.players[self.player_turn].shoot(event.pos, offset=self.scroll)

            # ==================== END EVENT ==================== #

            # Camera
            self.scroll[0] += (self.players[self.player_turn].rect().centerx - self.display.get_width() / 2 -
                               self.scroll[0]) / 30
            self.scroll[1] += (self.players[self.player_turn].rect().centery - self.display.get_height() / 2 -
                               self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            # Background
            self.display.blit(pygame.transform.scale(self.assets['bg'], self.display.get_size()), (0, 0))

            # Tilemap
            self.tilemap.render(self.display, offset=render_scroll)

            # Player
            self.players[0].update(self.tilemap, movement=(self.movement[0][1] - self.movement[0][0], 0),
                                   delta_time=self.delta_time)
            self.players[1].update(self.tilemap, movement=(self.movement[1][1] - self.movement[1][0], 0),
                                   delta_time=self.delta_time)
            self.players[0].render(self.display, offset=render_scroll)
            self.players[1].render(self.display, offset=render_scroll)

            # Timer
            self.timer.render(self.display, (20, 20))

            # Display
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (
            (random() * self.screenshake - self.screenshake / 2), (random() * self.screenshake - self.screenshake / 2)))
            pygame.display.update()
            self.clock.tick(FPS)
