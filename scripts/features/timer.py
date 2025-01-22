from math import sin, pi, cos, sqrt
import pygame


class Timer:
    def __init__(self, seconds, size=(20, 20), bg=(0, 0, 0), fg=(255, 255, 255)):
        self.size = size
        self.display = pygame.Surface(size, pygame.SRCALPHA)
        self.seconds = seconds
        self.current_seconds = self.seconds
        self.points = [(size[0]/2, size[1]/2), (size[0]/2, size[1]/2-sqrt(size[0]**2 + size[1]**2))]
        self.bg = bg
        self.fg = fg

    def reset(self):
        self.current_seconds = self.seconds
        self.points = [(self.size[0]/2, self.size[1]/2), (self.size[0]/2, self.size[1]/2-sqrt(self.size[0]**2 + self.size[1]**2))]

    def countdown(self):
        self.current_seconds -= 1
        angle = int(360 / self.seconds * (self.seconds - self.current_seconds))
        self.points.append((self.size[0] * sin(pi * 2 * angle / 360) + self.size[0]/2, -self.size[1] * cos(pi * 2 * angle / 360) + self.size[1]/2))

    def is_finished(self):
        return self.current_seconds <= 0

    def render(self, display, pos):
        pygame.draw.rect(self.display, self.bg, ((0, 0), self.size))
        if len(self.points) > 2:
            pygame.draw.polygon(self.display, self.fg, self.points)
        display.blit(self.display, pos)
