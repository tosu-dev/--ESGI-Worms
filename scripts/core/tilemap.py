import json
from pygame import Rect

NEIGHBOR_OFFSET = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
PHYSICS_TILES = {'grass', 'stone'}
AUTOTILE_TYPES = {'grass', 'stone'}
AUTOTILE_MAP = {
    tuple(sorted([(1, 0), (0, 1)])): 0,  # top-left
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,  # top
    tuple(sorted([(-1, 0), (0, 1)])): 2,  # top-right
    tuple(sorted([(-1, 0), (0, 1), (0, -1)])): 3,  # right
    tuple(sorted([(-1, 0), (0, -1)])): 4,  # bottom-right
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,  # bottom
    tuple(sorted([(1, 0), (0, -1)])): 6,  # bottom-left
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7,  # left
    tuple(sorted([(-1, 0), (1, 0), (0, -1), (0, 1)])): 8,  # middle
}


class TileMap:
    def __init__(self, game, tilemap={}, tile_size: int = 16):
        self.tile_size = tile_size
        self.tilemap = tilemap
        self.offgrid_tiles = []
        self.game = game
    def extract(self, id_pairs, keep=False):
        matches = []

        deleted_offgrid_tiles = []
        for tile in self.offgrid_tiles.copy():
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    deleted_offgrid_tiles.append(tile)
        for tile in deleted_offgrid_tiles:
            self.offgrid_tiles.remove(tile)

        deleted_tiles = []
        for loc, tile in self.tilemap.items():
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                matches[-1]['pos'] = matches[-1]['pos'].copy()
                matches[-1]['pos'][0] *= self.tile_size
                matches[-1]['pos'][1] *= self.tile_size
                if not keep:
                    deleted_tiles.append(loc)
        for loc in deleted_tiles:
            del self.tilemap[loc]

        return matches

    def is_pos_in_tile(self, pos, physics=True):
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        loc = str(tile_loc[0]) + ';' + str(tile_loc[1])
        if physics:
            return loc in self.tilemap and self.tilemap[loc]['type'] in PHYSICS_TILES
        return loc in self.tilemap

    def get_tile(self, pos):
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        loc = str(tile_loc[0]) + ';' + str(tile_loc[1])
        if loc in self.tilemap:
            return self.tilemap[loc]

    def get_tile_rect(self, pos):
        tile = self.get_tile(pos)
        if tile:
            return Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size)

    def tiles_around(self, pos):
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_OFFSET:
            loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if loc in self.tilemap:
                tiles.append(self.tilemap[loc])
        return tiles

    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append(Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size,
                                  self.tile_size))
        return rects

    def solid_check(self, pos):
        tile_loc = str(int(pos[0] // self.tile_size)) + ';' + str(int(pos[1] // self.tile_size))
        if tile_loc in self.tilemap:
            if self.tilemap[tile_loc]['type'] in PHYSICS_TILES:
                return self.tilemap[tile_loc]

    def remove_tiles_around(self, pos, radius=1):
        start_loc = str(int(pos[0] // self.tile_size)) + ';' + str(int(pos[1] // self.tile_size))
        for y in range(-radius, radius+1, 1):
            for x in range(-radius, radius + 1, 1):
                if y**2 + x**2 <= radius**2:
                    t = start_loc.split(';')
                    tile_loc = str(int(t[0]) + x) + ';' + str(int(t[1]) + y)
                    if tile_loc in self.tilemap:
                        del self.tilemap[tile_loc]

        offgrid_tile_to_del = []
        for i in range(len(self.offgrid_tiles)):
            tpos = self.offgrid_tiles[i]["pos"]
            if (tpos[0] - pos[0])**2 + (tpos[1] - pos[1])**2 <= (radius * self.tile_size)**2:
                offgrid_tile_to_del.append(i)

        offgrid_tiles = []
        for i in range(len(self.offgrid_tiles)):
            if i not in offgrid_tile_to_del:
                offgrid_tiles.append(self.offgrid_tiles[i])
        self.offgrid_tiles = offgrid_tiles


    def autotile(self):
        for tile in self.tilemap.values():
            neighbors = set()
            for shift in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
                check_loc = str(tile['pos'][0] + shift[0]) + ';' + str(tile['pos'][1] + shift[1])
                if check_loc in self.tilemap and self.tilemap[check_loc]['type'] == tile['type']:
                    neighbors.add(shift)
            neighbors = tuple(sorted(neighbors))
            if (tile['type'] in AUTOTILE_TYPES) and (neighbors in AUTOTILE_MAP):
                tile['variant'] = AUTOTILE_MAP[neighbors]

    def save(self, path):
        with open(path, 'w') as json_file:
            json.dump({'tilemap': self.tilemap, 'tile_size': self.tile_size, 'offgrid': self.offgrid_tiles}, json_file)

    def load(self, path):
        with open(path, 'r') as json_file:
            map_data = json.load(json_file)
            self.tilemap = map_data['tilemap']
            self.tile_size = map_data['tile_size']
            self.offgrid_tiles = map_data['offgrid']

    def render(self, surf, offset=[0, 0]):
        for tile in self.offgrid_tiles:
            surf.blit(
                self.game.assets[tile['type']][tile['variant']],
                (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))
            if tile['type'] in PHYSICS_TILES:
                pass

        for x in range(int(offset[0] // self.tile_size), int((offset[0] + surf.get_width()) // self.tile_size) + 1):
            for y in range(int(offset[1] // self.tile_size),
                           int((offset[1] + surf.get_height()) // self.tile_size) + 1):
                loc = str(x) + ';' + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    if tile["type"] != "":
                        surf.blit(
                            self.game.assets[tile['type']][tile['variant']],
                            (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))

        for tile in self.tilemap.values():
            if tile['type'] in PHYSICS_TILES:
                pass
