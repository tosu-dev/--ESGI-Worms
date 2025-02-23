import math
import sys
from time import time
from random import random, randint, choice, uniform

from scripts.core.animation import Animation
from scripts.core.constants import *
from scripts.core.font import Font
from scripts.core.particle import Particle
from scripts.core.utils import *
from scripts.entities.player import Player
from scripts.features.minimap import Minimap
from scripts.features.timer import Timer
from scripts.menu import  Menu

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
        pygame.font.init()

        pygame.display.set_caption('Worms')
        self.render_scale = 1.5
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.display = pygame.Surface((SCREEN_SIZE[0] // self.render_scale, SCREEN_SIZE[1] // self.render_scale))
        self.clock = pygame.time.Clock()
        self.target_fps = TARGET_FPS
        self.fps = FPS
        self.delta_time = 0
        self.menu = Menu(self)
        self.font = Font('data/fonts/large_font.png', scale=4)


    def init_game(self, map):
        self.weapon_overlay = pygame.Surface((64, 64))
        self.assets = {
            'bg': load_image('background.png'),
            'projectile': load_image('projectile.png'),

            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'spawners': load_images('tiles/spawners'),
            'stone': load_images('tiles/stone'),

            'player0/idle': Animation(load_images('entities/player0/idle'), 6),
            'player0/run': Animation(load_images('entities/player0/run'), 4),
            'player0/jump': Animation(load_images('entities/player0/jump')),

            'player1/idle': Animation(load_images('entities/player1/idle'), 6),
            'player1/run': Animation(load_images('entities/player1/run'), 4),
            'player1/jump': Animation(load_images('entities/player1/jump')),

            'parachute': load_image('weapons/parachute.png'),
            'rocket': load_image('weapons/rocket.png'),
            'grenade': load_image('weapons/grenade.png'),
            'weapon_frame_border': load_image('overlays/frame_border.png'),

            'particles/particle': Animation(load_images('particles/particle'), 8, loop=False),
            'particles/blood': Animation(load_images('particles/blood'), 12, loop=False),
        }
        self.menu_assets = {
            'main_menu': pygame.transform.scale_by(load_image('menu/main_menu.png', colorkey=None, alpha=True), 3),
        }
        self.menu_rects = {
            'main_menu': pygame.Rect((SCREEN_SIZE[0] // 2 - self.menu_assets['main_menu'].get_width() // 2,
                                        SCREEN_SIZE[1] - self.menu_assets['main_menu'].get_height() - 20),
                                       self.menu_assets['main_menu'].get_size()),
        }

        self.musics = {
            'potato': pygame.mixer.Sound(MUSIC_PATH + 'potato.wav'),
            'time_for_adventure': pygame.mixer.Sound(MUSIC_PATH + 'time_for_adventure.mp3'),
        }
        self.musics['potato'].set_volume(0.2)
        self.musics['time_for_adventure'].set_volume(0.2)
        self.music = self.musics[choice(list(self.musics.keys()))]

        self.sfx = {
            'ambience': pygame.mixer.Sound(SFX_PATH + 'ambience.wav'),
            'menu_click': pygame.mixer.Sound(SFX_PATH + 'jump.wav'),
            'hurt': pygame.mixer.Sound(SFX_PATH + 'hurt.wav'),
            'tap': pygame.mixer.Sound(SFX_PATH + 'tap.wav'),
            'explosion': pygame.mixer.Sound(SFX_PATH + 'explosion.wav'),
            'parachute': pygame.mixer.Sound(SFX_PATH + 'parachute.wav'),
            'jump': pygame.mixer.Sound(SFX_PATH + 'jump.wav'),
            'footstep': pygame.mixer.Sound(SFX_PATH + 'footstep.wav'),
            'victory': pygame.mixer.Sound(SFX_PATH + 'victory.wav'),
        }
        self.sfx['ambience'].set_volume(0.2)
        self.sfx['menu_click'].set_volume(0.1)
        self.sfx['explosion'].set_volume(0.1)
        self.sfx['tap'].set_volume(0.5)
        self.sfx['hurt'].set_volume(2)
        self.sfx['parachute'].set_volume(0.5)
        self.sfx['jump'].set_volume(0.6)
        self.sfx['footstep'].set_volume(0.4)
        self.sfx['victory'].set_volume(0.5)

        self.players = [
            Player(self, (0, 0), (8, 15), 0),
            Player(self, (0, 0), (8, 15), 1),
        ]
        self.winner = None
        self.projectile = None
        self.particles = []
        self.wind_particles = []
        for _ in range(20):
            x = randint(0, SCREEN_SIZE[0])
            y = randint(0, SCREEN_SIZE[1])
            self.wind_particles.append([x, y])

        self.mouse_pos = [0, 0]
        self.movement = [[False, False], [False, False]]
        self.scroll = [0, 0]
        self.screenshake = 0
        self.screenshake_timer = 0
        self.player_turn = 0
        self.zoom = 1
        self.changing_turn = False
        self.changing_turn_timer = 2
        self.wind = [randint(-50, 51), randint(-50, 51)]
        self.minimap = Minimap(self, (8, 8), SCREEN_SIZE, 8, 1)
        pygame.time.set_timer(pygame.USEREVENT, 1000)
        self.timer = Timer(30, (64, 64))
        self.victory_music = False
        self.load_level(map)

    def load_level(self, map):
        self.tilemap = load_map(self, map)
        self.music.play(-1)
        self.sfx['ambience'].play(-1)
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

    def is_playing(self):
        return not (self.projectile or self.changing_turn or self.winner is not None)

    def change_player_transition(self):
        self.changing_turn_timer = 2
        self.changing_turn = True
        self.players[self.player_turn].charge_shooting = False
        self.movement = [[False, False], [False, False], ]

    def change_player_turn(self):
        self.changing_turn_timer = 2
        self.changing_turn = False
        self.timer.reset()
        self.player_turn = (self.player_turn + 1) % 2

    def damage_player(self, pos, radius=1):
        for i, player in enumerate(self.players):
            v = (player.pos[0] - pos[0]), (player.pos[1] - pos[1])
            r = radius * self.tilemap.tile_size
            if v[0] ** 2 + v[1] ** 2 <= r ** 2:
                l = math.sqrt(v[0]**2 + v[1]**2)
                ratio = 1 - (l / r)
                player.health -= self.projectile.damage * ratio
                self.sfx['hurt'].play()
                for _ in range(7):
                    r = 1
                    vx = uniform(-r, r)
                    vy = uniform(-r, r)
                    self.particles.append(Particle(self, "blood", player.pos, (vx, vy)))

    def kill_player(self, player):
        player.health = 0
        for _ in range(50):
            r = 3
            vx = uniform(-r, r)
            vy = uniform(-r, r)
            self.particles.append(Particle(self, "blood", player.pos, (vx, vy)))

    def check_player_death(self):
        for i, player in enumerate(self.players):
            if player.health <= 0:
                self.kill_player(player)
                self.winner = (i + 1) % 2
                return True
        return False

    def shake_screen(self, force, duration):
        self.screenshake_timer = duration
        self.screenshake = force

    def run(self):
        prev_time = time()
        while True:
            if self.menu.running:
                self.menu.run()
                pygame.display.update()
                self.clock.tick(FPS)
                continue

            # DELTA TIME
            self.delta_time = (time() - prev_time) * self.target_fps
            prev_time = time()

            # Get mouse pos
            self.mouse_pos = list(pygame.mouse.get_pos())
            self.mouse_pos[0] //= self.render_scale
            self.mouse_pos[1] //= self.render_scale

            # Camera
            if not self.changing_turn:
                if self.projectile:
                    self.scroll[0] += (self.projectile.pos[0] - self.display.get_width() / 2 -
                                       self.scroll[0]) / 10
                    self.scroll[1] += (self.projectile.pos[1] - self.display.get_height() / 2 -
                                       self.scroll[1]) / 10
                else:
                    self.scroll[0] += (self.players[self.player_turn].rect().centerx - self.display.get_width() / 2 -
                                       self.scroll[0]) / 10
                    self.scroll[1] += (self.players[self.player_turn].rect().centery - self.display.get_height() / 2 -
                                       self.scroll[1]) / 10
            render_scroll = [
                int(self.scroll[0]),
                int(self.scroll[1])
            ]

            # ==================== START EVENT ==================== #
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.USEREVENT:
                    if self.is_playing():
                        self.timer.countdown()
                        if self.timer.is_finished():
                            self.change_player_transition()

                if event.type == pygame.KEYDOWN:
                    if self.is_playing():
                        if event.key == pygame.K_LEFT:
                            self.movement[self.player_turn][0] = True
                        if event.key == pygame.K_RIGHT:
                            self.movement[self.player_turn][1] = True
                        if event.key == pygame.K_UP:
                            self.players[self.player_turn].charge_jump()

                if event.type == pygame.KEYUP:
                    if self.is_playing():
                        if event.key == pygame.K_LEFT:
                            self.movement[self.player_turn][0] = False
                        if event.key == pygame.K_RIGHT:
                            self.movement[self.player_turn][1] = False
                        if event.key == pygame.K_UP:
                            self.players[self.player_turn].jump()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.is_playing():
                        if event.button == 1:
                            self.players[self.player_turn].charge_shoot()
                        if event.button == 3:
                            self.players[self.player_turn].cancel_shoot()
                    elif self.winner is not None and not self.changing_turn:
                        if event.button == 1:
                            if self.menu_rects['main_menu'].collidepoint(event.pos):
                                self.music.stop()
                                self.sfx['ambience'].stop()
                                self.sfx['menu_click'].play()
                                self.menu.running = True

                if event.type == pygame.MOUSEBUTTONUP:
                    if self.is_playing():
                        if event.button == 1:
                            self.players[self.player_turn].shoot()

                if event.type == pygame.MOUSEWHEEL:
                    if self.is_playing():
                        self.players[self.player_turn].weapon += event.y
                        self.players[self.player_turn].weapon %= 2

            # ==================== END EVENT ==================== #

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

            # Projectile
            if self.projectile:
                self.zoom = min(1.8, self.zoom + 0.1)
                self.projectile.render(self.display, offset=render_scroll)
                self.projectile.update(fps=FPS)
                self.movement = [[False, False], [False, False]]
                # Player death
                self.check_player_death()
            # Changing turn
            elif self.changing_turn:
                self.changing_turn_timer -= 1 / FPS
                if self.changing_turn_timer <= 0:
                    self.change_player_turn()
            # Victory
            elif self.winner is not None:
                self.player_turn = self.winner
                self.changing_turn = False
                self.zoom = min(1.8, self.zoom + 0.1)
            # Playing
            else:
                self.zoom = max(1, self.zoom - 0.1)

                # Player death
                if self.check_player_death():
                    self.changing_turn = True

                # Timer
                self.timer.render(self.display, (10, 406))

                # Weapon type
                self.weapon_overlay.fill((0, 0, 0))
                if self.players[self.player_turn].weapon == 0:
                    weapon_img = self.assets["rocket"]
                elif self.players[self.player_turn].weapon == 1:
                    weapon_img = self.assets["grenade"]
                else:
                    weapon_img = self.assets["rocket"]
                self.weapon_overlay.blit(pygame.transform.scale(weapon_img, (32, 32)), (16, 16))
                self.weapon_overlay.blit(self.assets["weapon_frame_border"], (0, 0))
                self.display.blit(self.weapon_overlay, (80, 406))

                # Minimap
                self.minimap.render(self.display, render_scroll)

            # Wind
            for particle in self.wind_particles:
                particle[0] += self.wind[0] / 2
                particle[1] += self.wind[1] / 2

                # Redémarrer la particule si elle sort de l'écran
                if particle[0] > SCREEN_SIZE[0]:
                    particle[0] = 0
                    particle[1] = randint(0, SCREEN_SIZE[1])
                elif 0 > particle[0]:
                    particle[0] = SCREEN_SIZE[0]
                    particle[1] = randint(0, SCREEN_SIZE[1])

                if particle[1] > SCREEN_SIZE[1]:
                    particle[0] = randint(0, SCREEN_SIZE[0])
                    particle[1] = 0
                elif 0 > particle[1]:
                    particle[0] = randint(0, SCREEN_SIZE[0])
                    particle[1] = SCREEN_SIZE[1]

                pygame.draw.line(self.display, (255, 255, 255), (particle[0], particle[1]), (particle[0] + self.wind[0] / 2, particle[1] + self.wind[1] / 2), 2)

            # Particles
            particles_to_kill = []
            for i, particle in enumerate(self.particles):
                kill = particle.update()
                if kill:
                    particles_to_kill.append(i)

            particles = []
            for i in range(len(self.particles)):
                if i not in particles_to_kill:
                    particles.append(self.particles[i])

            for particule in self.particles:
                particule.render(self.display, render_scroll)

            self.particles = particles

            # Screenshake
            screenshake = ((random() * self.screenshake - self.screenshake / 2), (random() * self.screenshake - self.screenshake / 2))
            if self.screenshake_timer > 0:
                self.screenshake_timer -= 1 / FPS
            else:
                self.screenshake_timer = 0
                self.screenshake = 0

            # Display
            screen_size = (SCREEN_SIZE[0] * self.zoom, SCREEN_SIZE[1] * self.zoom)
            screen = pygame.transform.scale(self.display, screen_size)
            dest = (
                -((self.zoom - 1) * SCREEN_SIZE[0] / 2),
                -((self.zoom - 1) * SCREEN_SIZE[1] / 2)
            )
            self.screen.blit(screen, (dest[0] + screenshake[0], dest[1] + screenshake[1]))

            if self.winner is not None and not self.changing_turn:
                if not self.victory_music:
                    self.music.stop()
                    self.sfx['victory'].play()
                    self.victory_music = True
                self.font.render(self.screen, f"Winner is player {self.winner + 1}", (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2 - 120), center=True, bg=(0, 0, 0))
                self.screen.blit(self.menu_assets['main_menu'], self.menu_rects['main_menu'])

            pygame.display.update()
            self.clock.tick(FPS)
