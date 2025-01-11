import pygame

from scripts.core.constants import FPS
from scripts.core.utils import SFX_PATH, play_sfx, position_with_offset, position_to_int
from scripts.entities.physics_entity import PhysicsEntity
from math import atan2, degrees, sqrt, pi

from scripts.features.rocket import Rocket


class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size, outline=(0, 0, 0, 180))
        self.air_time = 0
        self.jumps = 1
        self.max_jumps = 1
        self.charge_jumping = False
        self.jump_force = 1.5
        self.rockets = []

        self.jump_sound = pygame.mixer.Sound(SFX_PATH + 'jump.wav')
        self.jump_sound.set_volume(0.7)

        self.shoot_offset = [10, 10]

    def start_charge_jump(self):
        if self.jumps > 0:
            self.charge_jumping = True

    def jump(self):
        if self.jumps > 0:
            play_sfx(self.jump_sound)
            self.velocity[1] = -self.jump_force
            self.jumps -= 1
            self.air_time = 8
            self.jump_force = 1.5
            self.charge_jumping = False

    def shoot(self):
        mouse_pos = self.game.mouse_pos
        offset = self.game.scroll
        mouse_pos = mouse_pos[0] + offset[0], mouse_pos[1] + offset[1]
        pos = position_with_offset(self.pos, self.shoot_offset, add=True)
        self.rockets.append(Rocket.create(pos, mouse_pos))

    def update(self, tilemap, movement=(0, 0), delta_time=1):
        if self.charge_jumping:
            self.set_action('idle')
            self.jump_force = min(self.jump_force + 0.1, 5)
        else:
            super().update(tilemap, movement, delta_time)

        self.air_time += 1

        if self.collisions['bottom']:
            self.air_time = 0
            self.jumps = self.max_jumps

        if (self.collisions['left'] or self.collisions['right']) and self.air_time > 8:
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True

        if self.air_time > 8:
            self.set_action('jump')
        elif movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)

        # Rockets
        for rocket in self.rockets:
            rocket.update(FPS)

    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset)

        mouse_pos = self.game.mouse_pos
        offset = self.game.scroll
        mouse_pos = position_with_offset(mouse_pos, offset, add=True)
        pos = position_with_offset(self.pos, self.shoot_offset, add=True)
        rocket_trajectory = Rocket.calculate_trajectory(self.game.tilemap, position_to_int(pos), mouse_pos, FPS)
        for point in rocket_trajectory:
            pygame.draw.circle(surf, (255, 255, 255), position_with_offset(point, offset), 2)

        for rocket in self.rockets:
            rocket.render(surf, offset)
