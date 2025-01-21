import pygame
from math import pi, atan2, sqrt, cos, sin
from scripts.core.utils import load_image, add_points


class Grenade:

    mass = 20
    max_force = 150
    damage = 50

    def __init__(self, pos, angle, force, game):
        self.start_pos = list(pos)
        self.angle = angle
        self.force = force
        self.time = 0
        self.old_pos = list(pos)
        self.pos = list(pos)
        self.image = load_image('weapons/grenade.png')
        self.rotation = 0
        self.rotation_force = int(15 * (self.force / 150))
        self.timer = 5
        self.collisions = {'top': False, 'bottom': False, 'left': False, 'right': False}
        self.game = game

    @classmethod
    def create(cls, player_pos, mouse_pos, game):
        vector = add_points(player_pos, mouse_pos, sub=True)
        angle = atan2(-vector[1], vector[0])
        if angle < 0:
            angle += 2 * pi
        force = min(sqrt(vector[0] ** 2 + vector[1] ** 2), cls.max_force)
        return Grenade(player_pos, angle, force, game)

    @classmethod
    def calculate_trajectory(cls, tilemap, player_pos, mouse_pos, fps):
        cto = 3  # collide trigger offset
        vector = add_points(player_pos, mouse_pos, sub=True)
        angle = atan2(-vector[1], vector[0])
        if angle < 0:
            angle += 2 * pi
        force = min(sqrt(vector[0] ** 2 + vector[1] ** 2), cls.max_force)
        start_pos = list(player_pos)

        point_timer = 0.2
        time = 0
        timer = 0
        trajectory = []
        pos = list(start_pos)

        while timer <= 5:
            vel_x = force * cos(angle)
            vel_y = -force * sin(angle)

            time += 1 / fps
            timer += 1 / fps
            point_timer -= 1 / fps

            old_pos = list(pos)
            pos[0] = start_pos[0] + vel_x * time
            pos[1] = start_pos[1] + (vel_y * time) + (
                    0.5 * 9.8 * cls.mass * time ** 2)

            v = [pos[0] - old_pos[0], pos[1] - old_pos[1]]
            collision_pos = {}
            collided = False
            if v[0] < 0:
                collision_pos["left"] = [pos[0] - cto, pos[1]]
            elif v[0] > 0:
                collision_pos["right"] = [pos[0] + cto, pos[1]]
            if v[1] > 0:
                collision_pos["bottom"] = [pos[0], pos[1] + cto]
            elif v[1] < 0:
                collision_pos["top"] = [pos[0], pos[1] - cto]

            # Check collision
            for p in collision_pos:
                if tilemap.is_pos_in_tile(collision_pos[p]):
                    collided = True
                    if p == "left":
                        vel_x = abs(vel_x)
                        if v[1] > 0:
                            vel_y = abs(vel_y)
                    elif p == "right":
                        vel_x = -abs(vel_x)
                        if v[1] > 0:
                            vel_y = abs(vel_y)

                    if p == "top":
                        vel_y = abs(vel_y)
                    elif p == "bottom":
                        pos[1] -= 1  # Avoid dancing on the floor
                        vel_y = -abs(vel_y)

            if collided:
                start_pos = list(pos)
                force *= 0.6
                time = 0
                angle = atan2(-vel_y, vel_x)
                if angle < 0:
                    angle += 2 * pi

            if point_timer <= 0:
                point_timer = 0.2
                trajectory.append(list(pos))

        return trajectory

    def update(self, fps):
        cto = 3  # collide trigger offset
        vel_x = self.force * cos(self.angle)
        vel_y = -self.force * sin(self.angle)

        if vel_x >= 0:
            self.rotation -= self.rotation_force
        else:
            self.rotation += self.rotation_force
        self.rotation %= 360

        # Grenade life timer
        self.timer -= 1 / fps
        if self.timer <= 0:
            self.game.tilemap.remove_tiles_around(self.pos, radius=4)
            self.game.damage_player(self.pos, radius=5)
            self.game.projectile = None

        # Time
        self.time += 1 / fps

        # Saving old position
        self.old_pos[0] = self.pos[0]
        self.old_pos[1] = self.pos[1]

        # Compute new position
        self.pos[0] = self.start_pos[0] + vel_x * self.time
        self.pos[1] = self.start_pos[1] + (vel_y * self.time) + (
                0.5 * 9.8 * self.mass * self.time ** 2)

        # Vector between new and old position
        v = [self.pos[0] - self.old_pos[0], self.pos[1] - self.old_pos[1]]

        # Compute collision possibility horizontaly and verticaly
        pos = list(self.pos)
        collision_pos = {}
        collided = False
        if v[0] < 0:
            collision_pos["left"] = [pos[0] - cto, pos[1]]
        elif v[0] > 0:
            collision_pos["right"] = [pos[0] + cto, pos[1]]
        if v[1] > 0:
            collision_pos["bottom"] = [pos[0], pos[1] + cto]
        elif v[1] < 0:
            collision_pos["top"] = [pos[0], pos[1] - cto]

        # Check collision
        for p in collision_pos:
            if self.game.tilemap.is_pos_in_tile(collision_pos[p]):
                collided = True
                # If horizontaly, make sure to take the absolute value of vel_y if falling
                # because of new angle 'atan2(-vel_y, vel_x)'
                if p == "left":
                    vel_x = abs(vel_x)
                    if v[1] > 0:
                        vel_y = abs(vel_y)
                elif p == "right":
                    vel_x = -abs(vel_x)
                    if v[1] > 0:
                        vel_y = abs(vel_y)

                if p == "top":
                    vel_y = abs(vel_y)
                elif p == "bottom":
                    self.pos[1] -= 1  # Avoid dancing on the floor
                    vel_y = -abs(vel_y)

        # If collided, compute new trajectory
        if collided:
            self.start_pos = list(self.pos)
            self.force *= 0.6
            self.time = 0
            self.angle = atan2(-vel_y, vel_x)
            if self.angle < 0:
                self.angle += 2 * pi
            self.rotation_force = int(15 * (self.force / 150))

    def render(self, surf, offset):
        img = self.image.copy()
        img = pygame.transform.rotate(img, self.rotation)
        surf.blit(img, (self.pos[0] - offset[0] - self.image.get_width() / 2,
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