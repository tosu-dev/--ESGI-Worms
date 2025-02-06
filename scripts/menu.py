import pygame
import sys

from scripts.core.constants import SCREEN_SIZE
from scripts.core.utils import load_image, get_map_names
from scripts.core.font import Font

class Menu:
    def __init__(self, game):
        self.game = game
        self.running = True
        self.font = Font('data/fonts/large_font.png')
        scale_factor = 3
        self.assets = {
            'bg': load_image('background.png'),
            'play': pygame.transform.scale_by(load_image('menu/play.png', colorkey=None, alpha=True), scale_factor),
            'previous': pygame.transform.scale_by(load_image('menu/previous.png', colorkey=None, alpha=True), scale_factor),
            'next': pygame.transform.scale_by(load_image('menu/next.png', colorkey=None, alpha=True), scale_factor),
        }
        self.menus = {
            'main': {
                'play_button': pygame.Rect((SCREEN_SIZE[0] // 2 - self.assets['play'].get_width() // 2, SCREEN_SIZE[1] // 2 - self.assets['play'].get_height() // 2), self.assets['play'].get_size()),
            },
            'map': {
                'map_list': [],
                'play_button': pygame.Rect((SCREEN_SIZE[0] // 2 - self.assets['play'].get_width() // 2,
                                            SCREEN_SIZE[1] - self.assets['play'].get_height() - 20),
                                           self.assets['play'].get_size()),
                'previous_button': pygame.Rect((20, SCREEN_SIZE[1] // 2 - self.assets['previous'].get_height() // 2), self.assets['previous'].get_size()),
                'next_button': pygame.Rect((SCREEN_SIZE[0] - self.assets['next'].get_width() - 20, SCREEN_SIZE[1] // 2 - self.assets['next'].get_height() // 2), self.assets['next'].get_size()),
            },
        }
        self.current_menu = 'main'

    def load_maps(self):
        for i, map_name in enumerate(get_map_names()):
            self.menus['map']['map_list'].append({
                'name': map_name,
                'thumbnail': load_image(f'../maps/{map_name}/thumbnail.png', colorkey=None),
            })
            self.menus['map']['current_map'] = 0

    def run(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.current_menu == 'main':
                        if self.menus['main']['play_button'].collidepoint(event.pos):
                            self.current_menu = 'map'
                            self.load_maps()

                    elif self.current_menu == 'map':
                        if self.menus['map']['play_button'].collidepoint(event.pos):
                            map = self.menus['map']['map_list'][self.menus['map']['current_map']]
                            self.game.init_game(map['name'])
                            self.running = False
                        elif self.menus['map']['previous_button'].collidepoint(event.pos):
                            self.menus['map']['current_map'] -= 1
                            self.menus['map']['current_map'] %= len(self.menus['map']['map_list'])
                        elif self.menus['map']['next_button'].collidepoint(event.pos):
                            self.menus['map']['current_map'] += 1
                            self.menus['map']['current_map'] %= len(self.menus['map']['map_list'])


        # Background
        self.game.screen.blit(pygame.transform.scale(self.assets['bg'], self.game.screen.get_size()), (0, 0))

        # Main menu
        if self.current_menu == 'main':
            self.game.screen.blit(self.assets['play'], self.menus['main']['play_button'])

        # Map select menu
        elif self.current_menu == 'map':
            # Map info
            map = self.menus['map']['map_list'][self.menus['map']['current_map']]
            thumbnail = map['thumbnail']
            thumbnail_pos = (SCREEN_SIZE[0] // 2 - thumbnail.get_width() // 2, SCREEN_SIZE[1] // 2 - thumbnail.get_height() // 2)
            name_pos = (SCREEN_SIZE[0] // 2, thumbnail_pos[1] - 20)
            self.game.screen.blit(thumbnail, thumbnail_pos)
            self.font.render(self.game.screen, map['name'], name_pos, center=True)

            # Buttons
            self.game.screen.blit(self.assets['play'], self.menus['map']['play_button'])
            self.game.screen.blit(self.assets['previous'], self.menus['map']['previous_button'])
            self.game.screen.blit(self.assets['next'], self.menus['map']['next_button'])





