import os

import pygame
from pygame import image, font

from scripts.core.tilemap import TileMap

font.init()

IMG_PATH = 'data/images/'
MAP_PATH = 'data/maps/'
MUSIC_PATH = 'data/musics/'
SFX_PATH = 'data/sfx/'

DEBUG_FONT = font.SysFont('Arial', 24)
WINNER_FONT = font.SysFont('Arial', 64)

def show_text(surface, value, pos=(0, 0), color=(0, 0, 0), center=False, font=DEBUG_FONT):
    text_surface = font.render(value, True, color)
    if center:
        width = text_surface.get_width()
        height = text_surface.get_height()
        surface.blit(text_surface, (pos[0] - width // 2, pos[1] - height // 2))
    else:
        surface.blit(text_surface, pos)


def load_image(path, colorkey=(0, 0, 0), alpha=False):
    if alpha:
        img = image.load(IMG_PATH + path).convert_alpha()
    else:
        img = image.load(IMG_PATH + path).convert()
    if colorkey is not None:
        img.set_colorkey(colorkey)
    return img

def load_images(path, colorkey=(0, 0, 0)):
    imgs = []
    for img_name in sorted(os.listdir(IMG_PATH + path)):
        imgs.append(load_image(path + "/" + img_name, colorkey))
    return imgs

def load_map(game, name):
    tilemap = TileMap(game)
    tilemap.load(MAP_PATH + '/' + name + '/map.json')
    return tilemap

def load_maps(game):
    maps = []
    for map_name in sorted(os.listdir(MAP_PATH)):
        maps.append(load_map(game, map_name))
    return maps

def get_map_names():
    maps = []
    for map_name in sorted(os.listdir(MAP_PATH)):
        maps.append(map_name)
    return maps

def add_points(point1, point2, sub=False):
    """ Calculate a position with or without an offset """
    if not sub:
        return point1[0] + point2[0], point1[1] + point2[1]
    return point1[0] - point2[0], point1[1] - point2[1]

def point_to_int(point):
    """ Convert position to int position"""
    return [int(point[0]), int(point[1])]

def scale_img_keep_aspect_ratio(image, width, height):
    width_ratio = width / image.get_width()
    height_ratio = height / image.get_height()
    ratio = max(width_ratio, height_ratio)
    new_width = ratio * image.get_width()
    new_height = ratio * image.get_height()
    return pygame.transform.scale(image, (new_width, new_height))

