import math
import random

import pygame
from math import pi, atan2, sqrt, cos, sin, exp

from scripts.core.utils import load_image, add_points
from scripts.core.particle import Particle


class Rocket:

    mass = 10
    max_force = 300
    damage = 30

    def __init__(self, pos, angle, force, game):
        self.start_pos = list(pos)
        self.angle = angle
        self.force = force
        self.time = 0
        self.old_pos = list(pos)
        self.pos = list(pos)
        self.image = load_image('weapons/rocket.png')
        self.rotation = 0
        self.particles = []
        self.game = game

    @classmethod
    def create(cls, player_pos, mouse_pos, game):
        vector = add_points(player_pos, mouse_pos, sub=True)
        angle = atan2(-vector[1], vector[0])
        if angle < 0:
            angle += 2 * pi
        force = min(sqrt(vector[0] ** 2 + vector[1] ** 2), cls.max_force)
        return Rocket(player_pos, angle, force, game)

    @classmethod
    def calculate_trajectory(cls, tilemap, wind, player_pos, mouse_pos, fps):
        vector = add_points(player_pos, mouse_pos, sub=True)
        angle = atan2(-vector[1], vector[0])
        if angle < 0:
            angle += 2 * pi
        force = min(sqrt(vector[0] ** 2 + vector[1] ** 2), cls.max_force)

        vel_x = force * cos(angle)
        vel_y = -force * sin(angle)
        g = 9.8

        point_timer = 0.2
        time = 0
        pos = list(player_pos)
        trajectory = []
        while time < 10:
            time += 1 / fps
            point_timer -= 1 / fps
            if point_timer <= 0:
                point_timer = 0.2

                old_pos = list(pos)
                pos[0] = player_pos[0] + vel_x * time + wind[0] * time ** 2
                pos[1] = player_pos[1] + (vel_y * time) + (0.5 * g * cls.mass * time ** 2) + wind[1] * time ** 2

                point = tilemap.line_touch_tile((old_pos[0], old_pos[1]), (pos[0], pos[1]))
                if point:
                    trajectory.append(list(point))
                    break

                trajectory.append(list(pos))

        return trajectory

    def update(self, fps):
        vel_x = self.force * cos(self.angle)
        vel_y = -self.force * sin(self.angle)

        self.time += 1 / fps
        self.old_pos[0] = self.pos[0]
        self.old_pos[1] = self.pos[1]
        wind = self.game.wind
        g = 9.8

        self.pos[0] = self.start_pos[0] + vel_x * self.time + wind[0] * self.time ** 2
        self.pos[1] = self.start_pos[1] + (vel_y * self.time) + (0.5 * g * self.mass * self.time ** 2) + wind[1] * self.time ** 2


        v = [self.pos[0] - self.old_pos[0], self.pos[1] - self.old_pos[1]]

        self.rotation = math.degrees(atan2(-v[1], v[0]))
        if self.rotation < 0:
            self.rotation += 360

        if self.game.tilemap.is_pos_in_tile(self.pos):
            self.game.tilemap.remove_tiles_around(self.pos, radius=2)
            self.game.damage_player(self.pos, radius=3)
            self.game.change_player_transition()
            for _ in range(50):
                r = 2
                vx = random.uniform(-r, r)
                vy = random.uniform(-r, r)
                self.game.particles.append(Particle(self.game, "particle", (self.pos[0], self.pos[1]), (vx, vy)))
            self.game.projectile = None

    def render(self, surf, offset):
        img = self.image.copy()
        img = pygame.transform.rotate(img, self.rotation)
        surf.blit(img, (self.pos[0] - offset[0] - self.image.get_width() / 2,
                               self.pos[1] - offset[1] - self.image.get_height() / 2))

        for particule in self.particles:
            particule.render(surf, offset)

class Rockets:

    def __init__(self, game):
        self.game = game
        self.rockets = []

    def add_rocket(self, pos, mouse_pos):
        self.rockets.append(Rocket.create(pos, mouse_pos))

    def update(self, fps):
        rocket_to_destroy = []
        for i, rocket in enumerate(self.rockets):
            rocket.update(fps)
            if self.game.tilemap.is_pos_in_tile(rocket.pos):
                rocket_to_destroy.append(i)

        for index_rocket in rocket_to_destroy:
            self.rockets.pop(index_rocket)

    def render(self, surf, offset):
        for rocket in self.rockets:
            rocket.render(surf, offset)