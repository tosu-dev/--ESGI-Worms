import sys
import pygame

from scripts.core.utils import load_images
from scripts.core.tilemap import TileMap
from scripts.core.utils import MAP_PATH

EDITOR_SCREEN_SIZE = (640*2, 480*2)
RENDER_SCALE = 1

class Editor:
    # ===== SINGLETON =====
    __instance = None
    def __new__(cls, name=None):
        if cls.__instance is None:
            cls.__instance = super(Editor, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, name=None):
        if (self.__initialized): return
        self.__initialized = True

        pygame.init()

        pygame.display.set_caption('Editor')
        self.screen  = pygame.display.set_mode(EDITOR_SCREEN_SIZE)
        self.display = pygame.Surface((EDITOR_SCREEN_SIZE[0]//RENDER_SCALE, EDITOR_SCREEN_SIZE[1]//RENDER_SCALE))
        self.clock   = pygame.time.Clock()

        self.movement = [False, False, False, False]
        self.assets = {
            'grass': load_images('tiles/grass'),
            'stone': load_images('tiles/stone'),
            'decor': load_images('tiles/decor'),
            'large_decor': load_images('tiles/large_decor'),
            'spawners': load_images('tiles/spawners'),
        }

        self.tilemap = TileMap(self)
        if name:
            self.name = name
            self.tilemap.load(MAP_PATH + '/' + name + '/map.json')

        self.scroll          = [0, 0]
        self.tile_list       = list(self.assets)
        self.tile_group      = 0
        self.tile_variant    = 0
        self.on_grid         = True
        self.left_clicking   = False
        self.right_clicking  = False
        self.shift_clicking  = False
        self.ctrl_clicking   = False
        self.alt_clicking   = False
        self.start_mouse_pos = (0, 0)
        self.start_scroll    = (0, 0)
        self.brush_size = 1
        self.name = name

    def run(self):
        while True:
            self.display.fill((0, 0, 0))

            self.scroll[0] += (self.movement[1] - self.movement[0]) * 2
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 2
            self.tilemap.render(self.display, offset=self.scroll)

            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
            current_tile_img.set_alpha(155)

            mouse_pos = pygame.mouse.get_pos()
            mouse_pos = mouse_pos[0]/RENDER_SCALE, mouse_pos[1]/RENDER_SCALE
            tile_pos = (int((mouse_pos[0]+self.scroll[0]) // self.tilemap.tile_size), int((mouse_pos[1]+self.scroll[1]) // self.tilemap.tile_size))

            if self.left_clicking and not self.shift_clicking:
                if self.on_grid:
                    for i in range(-(self.brush_size // 2), (self.brush_size // 2) + self.brush_size % 2):
                        for j in range(-(self.brush_size // 2), (self.brush_size // 2) + self.brush_size % 2):
                            self.tilemap.tilemap[str(tile_pos[0] + i) + ';' + str(tile_pos[1] + j)] = {
                                'type': self.tile_list[self.tile_group],
                                'variant': self.tile_variant,
                                'pos': [tile_pos[0] + i, tile_pos[1] + j]
                            }
            if self.right_clicking:
                for i in range(-(self.brush_size // 2), (self.brush_size // 2) + self.brush_size % 2):
                    for j in range(-(self.brush_size // 2), (self.brush_size // 2) + self.brush_size % 2):
                        tile_loc = str(tile_pos[0] + i) + ';' + str(tile_pos[1] + j)
                        if tile_loc in self.tilemap.tilemap:
                            del self.tilemap.tilemap[tile_loc]
                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_img = self.assets[tile['type']][tile['variant']]
                    tile_rect = pygame.Rect(tile['pos'][0] - self.scroll[0], tile['pos'][1] - self.scroll[1], tile_img.get_width(), tile_img.get_height()) 
                    if tile_rect.collidepoint(mouse_pos):
                        self.tilemap.offgrid_tiles.remove(tile)
            if self.left_clicking and self.shift_clicking:
                self.scroll = [self.start_scroll[0]+self.start_mouse_pos[0]-mouse_pos[0], self.start_scroll[1]+self.start_mouse_pos[1]-mouse_pos[1]]

            self.display.blit(current_tile_img, (5, 5))

            if self.on_grid:
                self.display.blit(current_tile_img, (tile_pos[0]*self.tilemap.tile_size-self.scroll[0], tile_pos[1]*self.tilemap.tile_size-self.scroll[1]))
            else:
                self.display.blit(current_tile_img, mouse_pos)

                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.left_clicking = True
                        if not self.shift_clicking and not self.on_grid:
                            self.tilemap.offgrid_tiles.append({'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': (mouse_pos[0]+self.scroll[0], mouse_pos[1]+self.scroll[1])})
                        if self.shift_clicking:
                            self.start_mouse_pos = mouse_pos
                            self.start_scroll = list(self.scroll)
                    if event.button == 3:
                        self.right_clicking = True

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.left_clicking = False
                    if event.button == 3:
                        self.right_clicking = False
                if event.type == pygame.MOUSEWHEEL:
                    if self.shift_clicking:
                        self.tile_variant = (self.tile_variant + event.y) % len(self.assets[self.tile_list[self.tile_group]])
                    elif self.alt_clicking:
                        self.brush_size += event.y
                        self.brush_size = max(0, self.brush_size)
                        print(f'Brush size: {self.brush_size}')
                    else:
                        self.tile_group = (self.tile_group + event.y) % len(self.tile_list)
                        self.tile_variant = 0

                if event.type == pygame.KEYDOWN:
                    # Movement
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        self.movement[2] = True
                    if event.key == pygame.K_DOWN:
                        self.movement[3] = True
                    # Special keys
                    if event.key == pygame.K_LSHIFT:
                        self.shift_clicking = True
                    if event.key == pygame.K_LCTRL:
                        self.ctrl_clicking = True
                    if event.key == pygame.K_LALT:
                        self.alt_clicking = True
                    # Grid
                    if event.key == pygame.K_g:
                        self.on_grid = not self.on_grid
                        print(f"{'grid' if self.on_grid else 'not grid'}")
                    # Auto tile
                    if event.key == pygame.K_t:
                        self.tilemap.autotile()
                        print('autotile')
                    # Saving
                    if event.key == pygame.K_s:
                        if self.ctrl_clicking:
                            if self.name:
                                self.tilemap.save(MAP_PATH + '/' + self.name + '/map.json')
                                print(f'Saved in {MAP_PATH + '/' + self.name + '/map.json'}')
                            else:
                                self.tilemap.save('data/maps/map.json')
                                print('Saved in data/maps/map.json')

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
                    if event.key == pygame.K_UP:
                        self.movement[2] = False
                    if event.key == pygame.K_DOWN:
                        self.movement[3] = False
                    if event.key == pygame.K_LSHIFT:
                        self.shift_clicking = False
                    if event.key == pygame.K_LCTRL:
                        self.ctrl_clicking = False
                    if event.key == pygame.K_LALT:
                        self.alt_clicking = False

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick()


# ========================================
Editor().run()
