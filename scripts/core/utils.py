import os
from pygame import image, font

from scripts.core.tilemap import TileMap

font.init()

IMG_PATH = 'data/images/'
MAP_PATH = 'data/maps/'
MUSIC_PATH = 'data/musics/'
SFX_PATH = 'data/sfx/'

DEBUG_FONT = font.SysFont('Arial', 24)


def load_image(path):
    img = image.load(IMG_PATH + path).convert()
    img.set_colorkey((0, 0, 0))
    return img

def load_images(path):
    imgs = []
    for img_name in sorted(os.listdir(IMG_PATH + path)):
        imgs.append(load_image(path + "/" + img_name))
    return imgs

def load_map(game, path):
    tilemap = TileMap(game)
    tilemap.load(MAP_PATH + '/' + path)
    return tilemap

def load_maps(game):
    maps = []
    for map_name in sorted(os.listdir(MAP_PATH)):
        maps.append(load_map(game, map_name))
    return maps

def play_sfx(sfx):
    sfx.stop()
    sfx.play()

def pg_debug(surface, value, pos=(0, 0), color=(0, 0, 0)):
    text_surface = DEBUG_FONT.render(value, False, color)
    surface.blit(text_surface, pos)

def position_with_offset(pos, offset, add=False):
    if add:
        return pos[0] + offset[0], pos[1] + offset[1]
    return pos[0] - offset[0], pos[1] - offset[1]

def position_to_int(pos):
    return [int(pos[0]), int(pos[1])]
