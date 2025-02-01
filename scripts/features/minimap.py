from pygame import Surface, mask, transform, SRCALPHA, draw
from scripts.core.tilemap import PHYSICS_TILES


class Minimap:
    def __init__(self, game, pos, size, size_ratio=1, unzoom=1):
        self.game = game
        self.pos = list(pos)
        self.size = size
        self.size_ratio = size_ratio
        self.unzoom = unzoom

        self.display = Surface(size, SRCALPHA)

    def render(self, surf, offset=[0, 0]):
        self.display.fill((0, 0, 0, 180))

        for i, player in enumerate(self.game.players):
            color = (255, 0, 0, 180)
            if i == self.game.player_turn:
                color = (0, 255, 0, 180)
            draw.rect(self.display, color,
                      ((player.pos[0] - offset[0]) / self.unzoom + self.size[0] / self.size_ratio,
                       (player.pos[1] - offset[1]) / self.unzoom + self.size[1] / self.size_ratio,
                       player.animation.img().get_width() / self.unzoom,
                       player.animation.img().get_height() / self.unzoom))

        for tile in self.game.tilemap.offgrid_tiles:
            if tile['type'] in PHYSICS_TILES:
                pass

        for tile in self.game.tilemap.tilemap.values():
            if tile['type'] in PHYSICS_TILES:
                draw.rect(self.display, (255, 255, 255, 180),
                          ((tile['pos'][0] * self.game.tilemap.tile_size - offset[0]) / self.unzoom + self.size[
                              0] / self.size_ratio,
                           (tile['pos'][1] * self.game.tilemap.tile_size - offset[1]) / self.unzoom + self.size[
                               1] / self.size_ratio,
                           self.game.tilemap.tile_size / self.unzoom,
                           self.game.tilemap.tile_size / self.unzoom))

        surf.blit(transform.scale(self.display, (self.size[0] / self.size_ratio, self.size[1] / self.size_ratio)),
                  self.pos)