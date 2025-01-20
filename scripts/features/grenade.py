import pygame
from math import pi, atan2, sqrt, cos, sin

from pygame import Rect

from scripts.core.utils import load_image, add_points


class Grenade:

    mass = 20

    def __init__(self, pos, angle, force):
        self.start_pos = list(pos)
        self.angle = angle
        self.force = force
        self.time = 0
        self.pos = list(pos)
        self.image = load_image('projectile.png')
        self.timer = 5
        self.collisions = {'top': False, 'bottom': False, 'left': False, 'right': False}

    @classmethod
    def create(cls, player_pos, mouse_pos):
        vector = add_points(player_pos, mouse_pos, sub=True)
        angle = atan2(-vector[1], vector[0])
        if angle < 0:
            angle += 2 * pi
        force = min(sqrt(vector[0] ** 2 + vector[1] ** 2), 200)
        return Grenade(player_pos, angle, force)

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
        while time < 5:
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

    def update(self, tilemap, fps):
        vel_x = self.force * cos(self.angle)
        vel_y = -self.force * sin(self.angle)

        self.timer -= 1 / fps
        self.time += 1 / fps
        self.pos[0] = self.start_pos[0] + vel_x * self.time
        self.pos[1] = self.start_pos[1] + (vel_y * self.time) + (
                0.5 * 9.8 * self.mass * self.time ** 2)

        pos = list(self.pos)
        collision_pos = {}
        if vel_x < 0:
            collision_pos["left"] = [pos[0] - 2, pos[1]]
        elif vel_x > 0:
            collision_pos["right"] = [pos[0] + 2, pos[1]]

        if vel_y < 0:
            collision_pos["bottom"] = [pos[0], pos[1] + 2]
        elif vel_y > 0:
            collision_pos["top"] = [pos[0], pos[1] - 2]

        for p in collision_pos:
            if tilemap.is_pos_in_tile(collision_pos[p]):
                if p == "left":
                    self.pos[0] += 2
                    vel_x = abs(vel_x)
                elif p == "right":
                    self.pos[0] -= 2
                    vel_x = -abs(vel_x)

                if p == "top":
                    self.pos[1] += 2
                    vel_y = -abs(vel_y)
                elif p == "bottom":
                    self.pos[1] -= 2
                    vel_y = abs(vel_y)

                self.start_pos = list(self.pos)
                self.force *= 0.7
                self.time = 0
                self.angle = atan2(vel_y, vel_x)
                if self.angle < 0:
                    self.angle += 2 * pi

    def render(self, surf, offset):
        surf.blit(self.image, (self.pos[0] - offset[0] - self.image.get_width() / 2,
                               self.pos[1] - offset[1] - self.image.get_height() / 2))

class Grenades:

    def __init__(self, game):
        self.game = game
        self.grenades = []

    def add_grenade(self, pos, mouse_pos):
        self.grenades.append(Grenade.create(pos, mouse_pos))

    def update(self, fps):
        grenade_to_destroy = []
        for i, grenade in enumerate(self.grenades):
            grenade.update(self.game.tilemap, fps)
            if grenade.timer <= 0:
                grenade_to_destroy.append(i)

        for index_grenade in grenade_to_destroy:
            self.grenades.pop(index_grenade)

    def render(self, surf, offset):
        for grenade in self.grenades:
            grenade.render(surf, offset)