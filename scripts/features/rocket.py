import pygame
from math import pi, atan2, sqrt, cos, sin

from scripts.core.utils import load_image


class Rocket:
    def __init__(self, pos, angle, force):
        self.start_pos = list(pos)
        self.angle = angle
        self.force = force
        self.time = 0
        self.pos = [i for i in pos]
        self.image = load_image('projectile.png')

    @classmethod
    def create(cls, player_pos, mouse_pos):
        offset_pos = [0, 0]
        vector = [mouse_pos[0] - player_pos[0], mouse_pos[1] - player_pos[1]]
        angle = atan2(-vector[1], vector[0])
        if angle < 0:
            angle += 2 * pi
        force = min(sqrt(vector[0] ** 2 + vector[1] ** 2) / 2, 100)
        return Rocket([player_pos[0] + offset_pos[0], player_pos[1] + offset_pos[1]], angle, force)

    @classmethod
    def calculate_trajectory(self, tilemap, player_pos, mouse_pos, fps):
        vector = [mouse_pos[0] - player_pos[0], mouse_pos[1] - player_pos[1]]
        angle = atan2(-vector[1], vector[0])
        if angle < 0:
            angle += 2 * pi
        force = min(sqrt(vector[0] ** 2 + vector[1] ** 2) / 2, 100)

        gravity = 9.8
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
                        0.5 * gravity * 5 * time ** 2)
                if tilemap.is_pos_in_tile(pos):
                    break
                trajectory.append(pos)

        return trajectory

    def update(self, fps):
        gravity = 9.8
        vel_x = self.force * cos(self.angle)
        vel_y = -self.force * sin(self.angle)

        self.time += 1 / fps
        self.pos[0] = self.start_pos[0] + vel_x * self.time
        self.pos[1] = self.start_pos[1] + (vel_y * self.time) + (
                0.5 * gravity * 5 * self.time ** 2)

    def render(self, surf, offset):
        surf.blit(self.image, (self.pos[0] - offset[0] - self.image.get_width() / 2,
                               self.pos[1] - offset[1] - self.image.get_height() / 2))
