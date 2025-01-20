import pygame
from math import pi, atan2, sqrt, cos, sin

from scripts.core.utils import load_image, add_points


class Rocket:

    mass = 5

    def __init__(self, pos, angle, force):
        self.start_pos = list(pos)
        self.angle = angle
        self.force = force
        self.time = 0
        self.pos = list(pos)
        self.image = load_image('projectile.png')

    @classmethod
    def create(cls, player_pos, mouse_pos):
        vector = add_points(player_pos, mouse_pos, sub=True)
        angle = atan2(-vector[1], vector[0])
        if angle < 0:
            angle += 2 * pi
        force = min(sqrt(vector[0] ** 2 + vector[1] ** 2), 200)
        return Rocket(player_pos, angle, force)

    @classmethod
    def calculate_trajectory(cls, tilemap, player_pos, mouse_pos, fps):
        vector = add_points(player_pos, mouse_pos, sub=True)
        angle = atan2(-vector[1], vector[0])
        if angle < 0:
            angle += 2 * pi
        force = min(sqrt(vector[0] ** 2 + vector[1] ** 2), 200)

        vel_x = force * cos(angle)
        vel_y = -force * sin(angle)

        point_timer = 0.2
        time = 0
        trajectory = []
        while time < 10:
            time += 1 / fps
            point_timer -= 1 / fps
            if point_timer <= 0:
                point_timer = 0.2
                pos = [0, 0]
                pos[0] = player_pos[0] + vel_x * time
                pos[1] = player_pos[1] + (vel_y * time) + (
                        0.5 * 9.8 * cls.mass * time ** 2)
                if tilemap.is_pos_in_tile(pos):
                    break
                trajectory.append(pos)

        return trajectory

    def update(self, fps):
        vel_x = self.force * cos(self.angle)
        vel_y = -self.force * sin(self.angle)

        self.time += 1 / fps
        self.pos[0] = self.start_pos[0] + vel_x * self.time
        self.pos[1] = self.start_pos[1] + (vel_y * self.time) + (
                0.5 * 9.8 * self.mass * self.time ** 2)

    def render(self, surf, offset):
        surf.blit(self.image, (self.pos[0] - offset[0] - self.image.get_width() / 2,
                               self.pos[1] - offset[1] - self.image.get_height() / 2))

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