import pygame

from scripts.core.constants import FPS
from scripts.core.utils import add_points, point_to_int, show_text
from scripts.entities.physics_entity import PhysicsEntity

from scripts.features.grenade import Grenade
from scripts.features.rocket import Rocket


class Player(PhysicsEntity):
    def __init__(self, game, pos, size, number):
        super().__init__(game, 'player', number, pos, size, outline=(0, 0, 0, 180))
        self.air_time = 0
        self.jumps = 1
        self.max_jumps = 1
        self.charge_jumping = False
        self.jump_force = 1.5
        self.parachute = False

        self.charge_shooting = False
        self.shoot_offset = [10, 10]

        self.weapon = 0
        self.health = 100

        self.footstep_tick = 16

    def charge_jump(self):
        if self.jumps > 0 and self.air_time <= 6:
            self.charge_jumping = True

    def jump(self):
        if self.charge_jumping:
            self.game.sfx['jump'].play()
            self.velocity[1] = -self.jump_force
            self.jumps -= 1
            self.air_time = 8
            self.jump_force = 1.5
            self.charge_jumping = False

    def charge_shoot(self):
        if not self.charge_jumping and self.air_time <= 6:
            self.set_action('idle')
            self.charge_shooting = True

    def cancel_shoot(self):
        if self.charge_shooting:
            self.set_action('idle')
            self.charge_shooting = False

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

        # Footstep
        if abs(movement[0]) >= 1 and self.air_time <= 8:
            self.footstep_tick -= 1
            if self.footstep_tick == 0:
                self.game.sfx['footstep'].play()
                self.footstep_tick = 16
        else:
            self.footstep_tick = 16

        self.air_time += 1

        # Bottom collision
        if self.collisions['bottom']:
            self.air_time = 0
            self.jumps = self.max_jumps
            self.parachute = False

        # Animation action
        if self.air_time > 8:
            self.set_action('jump')
        elif movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

        # Parachute
        if self.velocity[1] >= 8:
            self.game.sfx['parachute'].play()
            self.parachute = True
        if self.parachute:
            self.velocity[1] = max(2, self.velocity[1] - 0.3)

        # Clamp velocity
        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)

    def render(self, surf, offset=(0, 0)):
        player_render_pos = self.get_render_pos(offset)

        # Parachute
        if self.parachute:
            surf.blit(self.game.assets['parachute'], (player_render_pos[0] - 2, player_render_pos[1] - 8))

        super().render(surf, offset)

        # Health bar
        healthbar_pos = (player_render_pos[0] - 3, player_render_pos[1] - 5)
        healthbar_width = 20
        pygame.draw.rect(surf, (255, 0, 0), (healthbar_pos, (healthbar_width, 2)))
        pygame.draw.rect(surf, (0, 255, 0), (healthbar_pos, (self.health / 100 * healthbar_width, 2)))

        # Rocket trajectory
        if self.charge_shooting:
            mouse_pos = add_points(self.game.mouse_pos, self.game.scroll)
            pos = add_points(self.pos, self.shoot_offset)

            trajectory = []
            if self.weapon == 0:
                trajectory = Rocket.calculate_trajectory(self.game.tilemap, self.game.wind, point_to_int(pos), mouse_pos, FPS)
            elif self.weapon == 1:
                trajectory = Grenade.calculate_trajectory(self.game.tilemap, point_to_int(pos), mouse_pos, FPS)

            radius = 4.5
            c = 255
            for i, point in enumerate(trajectory):
                pygame.draw.circle(surf, (c, c, c), add_points(point, self.game.scroll, sub=True), radius)
                radius = max(2, radius * 0.95)
                c = max(100, c * 0.97)
