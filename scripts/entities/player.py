import pygame

from scripts.core.constants import FPS
from scripts.core.utils import SFX_PATH, play_sfx, add_points, point_to_int, pg_debug
from scripts.entities.physics_entity import PhysicsEntity

from scripts.features.grenade import Grenade
from scripts.features.rocket import Rocket


class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size, outline=(0, 0, 0, 180))
        self.air_time = 0
        self.jumps = 1
        self.max_jumps = 1
        self.charge_jumping = False
        self.jump_force = 1.5

        self.jump_sound = pygame.mixer.Sound(SFX_PATH + 'jump.wav')
        self.jump_sound.set_volume(0.7)

        self.charge_shooting = False
        self.shoot_offset = [10, 10]

        self.weapon = 0
        self.health = 100

    def charge_jump(self):
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

    def charge_shoot(self):
        if not self.charge_jumping and self.air_time <= 6:
            self.set_action('idle')
            self.charge_shooting = True

    def shoot(self):
        if self.charge_shooting:
            self.charge_shooting = False
            mouse_pos = add_points(self.game.mouse_pos, self.game.scroll)
            pos = add_points(self.pos, self.shoot_offset)
            if self.weapon == 0:
                self.game.projectile = Rocket.create(pos, mouse_pos, self.game)
            elif self.weapon == 1:
                self.game.projectile = Grenade.create(pos, mouse_pos, self.game)

    def update(self, tilemap, movement=(0, 0), delta_time=1):
        # Charge jump
        if self.charge_jumping:
            self.set_action('idle')
            self.jump_force = min(self.jump_force + 0.1, 5)
            movement = (0, 0)

        if self.charge_shooting:
            movement = (0, 0)

        super().update(tilemap, movement, delta_time)

        self.air_time += 1

        # Bottom collision
        if self.collisions['bottom']:
            self.air_time = 0
            self.jumps = self.max_jumps

        # Animation action
        if self.air_time > 8:
            self.set_action('jump')
        elif movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

        # Clamp velocity
        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)

    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset)

        # Health bar
        player_render_pos = self.get_render_pos(offset)
        healthbar_pos = (player_render_pos[0] - 3, player_render_pos[1] - 5)
        healthbar_width = 20
        pygame.draw.rect(surf, (255, 0, 0), (healthbar_pos, (healthbar_width, 2)))
        pygame.draw.rect(surf, (0, 255, 0), (healthbar_pos, (self.health / 100 * healthbar_width, 2)))

        # Rocket trajectory
        if self.charge_shooting:
            mouse_pos = add_points(self.game.mouse_pos, self.game.scroll)
            pos = add_points(self.pos, self.shoot_offset)

            if self.weapon == 0:
                rocket_trajectory = Rocket.calculate_trajectory(self.game.tilemap, point_to_int(pos), mouse_pos, FPS)
                for point in rocket_trajectory:
                    pygame.draw.circle(surf, (255, 255, 255), add_points(point, self.game.scroll, sub=True), 2)
            elif self.weapon == 1:
                grenade_trajectory = Grenade.calculate_trajectory(self.game.tilemap, point_to_int(pos), mouse_pos, FPS)
                for point in grenade_trajectory:
                    pygame.draw.circle(surf, (255, 255, 255), add_points(point, self.game.scroll, sub=True), 2)
