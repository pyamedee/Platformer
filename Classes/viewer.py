# -*- coding:Utf-8 -*-

from Scripts.logger import logger
import pygame
from pygame.locals import *

import pymunk.pygame_util
import numpy as np

from Classes.page_handler import PageHandler
from Classes.base_viewer import BaseViewer
import sprites.sprites as sprites
from Scripts.configurations import sp_cfg, general_cfg
pygame.init()


class Viewer(BaseViewer):
    def __init__(self, text_getter, framerate=30):
        logger.debug('initialize Viewer')
        super(Viewer, self).__init__(framerate, logger)
        self.page_handler = self.ViewerPageHandler()
        self.text_getter = text_getter

    def init_pages(self):
        self.page_handler.add_page('StartingPage', self.events, self.text_getter)

    def play(self):
        self.page_handler.current_page.unbind_events()
        self.page_handler.switch_page('InGame', self.events, self.actions, 1)

    def main(self):
        self.page_handler.current_page.update()

    class ViewerPageHandler(PageHandler):

        class _ViewerPage:
            def __init__(self, event_dict):
                self.events = event_dict

            def activate(self):
                raise NotImplementedError

            def deactivate(self):
                raise NotImplementedError

        class _MainMenu(_ViewerPage):
            def __init__(self, event_dict, bg_path):
                super().__init__(event_dict)
                self.window = pygame.display.get_surface()
                self.area = self.window.get_rect()
                self.displayed = False
                self.bg = pygame.image.load(bg_path).convert()
                self.rect = self.bg.get_rect()

            def activate(self):
                if not self.displayed:
                    self.display_bg(self.area)
                    self.displayed = True

            def display_bg(self, area):
                self.window.blit(self.bg, self.rect, area)

            def deactivate(self):
                pass

        class StartingPage(_MainMenu):

            def __init__(self, event_dict, text_getter):
                bg_path = 'Images\\bg.png'
                super().__init__(event_dict, bg_path)

                self.text_getter = text_getter
                self.font = pygame.font.Font(sp_cfg['font'], sp_cfg.getint('font_size'))
                self.fonts = dict()
                self.changes = set()
                self.language = general_cfg['language']

            def display_text(self):

                # Quit text
                quit_text = tuple(self.text_getter((self.language,), 2))[0][-1]
                render = self.font.render(quit_text, True, (255, 255, 255))
                rect = render.get_rect().move(70, 540).inflate(-4, -4)

                render2 = self.font.render(quit_text, True, (180, 180, 180))
                rect2 = render2.get_rect().move(70, 540).inflate(-4, -4)

                self.fonts['quit'] = [(render, rect), (render2, rect2), 0]
                self.changes.add('quit')

                # Play text
                play_text = tuple(self.text_getter((self.language,), 1))[0][-1]
                render = self.font.render(play_text, True, (255, 255, 255))
                rect = render.get_rect().move(70, 440).inflate(-4, -4)

                render2 = self.font.render(play_text, True, (180, 180, 180))
                rect2 = render2.get_rect().move(70, 440).inflate(-4, -4)

                self.fonts['play'] = [(render, rect), (render2, rect2), 0]
                self.changes.add('play')

            def is_font_colliding(self, font_name, pos):
                font = self.fonts[font_name]
                return font[font[-1]][1].collidepoint(pos)

            def activate_font(self, font_name):
                if not self.fonts[font_name][-1]:
                    self.fonts[font_name][-1] = True
                    self.changes.add(font_name)

            def deactivate_font(self, font_name):
                if self.fonts[font_name][-1]:
                    self.fonts[font_name][-1] = False
                    self.changes.add(font_name)

            def bind_events(self, event_handler):
                self.events[MOUSEMOTION] = event_handler.mouse_motion
                self.events[MOUSEBUTTONDOWN] = event_handler.mouse_button_down

            def unbind_events(self):
                return self.events.pop(MOUSEMOTION), self.events.pop(MOUSEBUTTONDOWN)

            def update(self):

                for font_name in self.changes:
                    font = self.fonts[font_name]
                    i = font[-1]
                    self.window.blit(font[i][0], font[i][1])

                self.changes.clear()

            def activate(self):
                super().activate()
                self.display_text()

        class InGame(_ViewerPage):

            def __init__(self, event_dict, action_set, level_id):
                super().__init__(event_dict)
                self.level_id = int(level_id)
                self.sprites = pygame.sprite.Group()
                self.structure_group = pygame.sprite.Group()
                self.window = pygame.display.get_surface()
                self.player_group = pygame.sprite.GroupSingle()
                self.player = None
                self.actions = action_set
                self.bg = None

                self.a = np.zeros(2, dtype=np.int32)  # decalage additionnel dans la conversion pymunk <-> pygame

            def display_bg(self, label):
                image = pygame.image.load('Images\\level1_bg.png').convert()
                self.window.blit(image, image.get_rect())
                self.bg = image

            def load_structures(self, structures):
                image = pygame.image.load('Images\\platform.png').convert_alpha()
                for structure in structures:
                    label = structure[4]
                    print(structure)
                    sprite = sprites.Structure(structure[2:4], image)
                    self.sprites.add(sprite)
                    self.structure_group.add(sprite)

            def load_player(self, coords):

                image = pygame.image.load('Images\\player.png').convert_alpha()
                print(coords)
                player = sprites.Player(coords, image)
                self.sprites.add(player)
                self.player_group.add(player)
                self.player = player

            def display(self):
                self.sprites.draw(self.window)

            def update(self):
                self.player_group.clear(self.window, self.bg)
                self.player_group.draw(self.window)
                self.structure_group.draw(self.window)

            def bind_events(self, event_handler):
                self.events[KEYDOWN] = event_handler.keydown
                self.events[KEYUP] = event_handler.keyup

            def is_player_on_ground(self):
                return pygame.sprite.spritecollideany(
                    self.player.bottom_rect.move(self.player.vector / 10),
                    self.structure_group,
                    collided=self.collide)

            def refresh_structures(self):
                self.structure_group.draw(self.window)

            @staticmethod
            def collide(rect, sprite):
                return rect.colliderect(sprite.rect)

            def to_pygame(self, p):
                return np.array(pymunk.pygame_util.to_pygame(p, self.screen)) + self.a

            def from_pygame(self, p):
                return np.array(pymunk.pygame_util.to_pygame(p, self.screen)) - self.a

            def activate(self):
                pass

            def deactivate(self):
                pass
