# -*- coding:Utf-8 -*-

from Scripts.logger import logger
import pyglet

import pymunk.pygame_util
import numpy as np

from Classes.managers import BasePageManager
from Classes.base_viewer import BaseViewer
import sprites.sprites as sprites
from Scripts.configurations import sp_cfg, general_cfg


class Viewer(BaseViewer):
    def __init__(self, model, framerate=30, *args, **kwargs):
        logger.debug('initialize Viewer')
        super(Viewer, self).__init__(framerate, logger, *args, **kwargs)
        self.page_manager = self.PageManager()
        self.model = model

    def init_pages(self):
        self.page_manager.switch_page('StartingPage', self.bind, self.unbind, self.model.get_text)

    def play(self):
        self.page_manager.switch_page('InGame', self.model.get_event, self.events, self.actions, 1)

    def on_draw(self):
        self.page_manager.current_page.draw()

    def update(self, _):
        self.page_manager.current_page.update()

    class PageManager(BasePageManager):

        class _ViewerPage:
            def __init__(self, event_binding_callback, event_unbinding_callback):
                self.bind = event_binding_callback
                self.unbind = event_unbinding_callback

            def activate(self):
                raise NotImplementedError

            def deactivate(self):
                raise NotImplementedError

            def draw(self):
                raise NotImplementedError

            def update(self):
                raise NotImplementedError

        class _MainMenu(_ViewerPage):
            def __init__(self, event_binding_callback, event_unbinding_callback, bg_path):
                super().__init__(event_binding_callback, event_unbinding_callback)
                self.bg = pyglet.image.load(bg_path)

            def draw(self):
                self.bg.blit(0, 0)

        class StartingPage(_MainMenu):

            def __init__(self, event_binding_callback, event_unbinding_callback, text_getter):
                bg_path = 'Images/bg.png'
                super().__init__(event_binding_callback, event_unbinding_callback, bg_path)

                self.text_getter = text_getter
                #self.font = pygame.font.Font(sp_cfg['font'], sp_cfg.getint('font_size'))
                self.labels = dict()
                self.label_batch = pyglet.graphics.Batch()
                self.changes = set()

                self.language = general_cfg['language']

            def init_text(self):
                quit_txt = tuple(self.text_getter((self.language,), 2))[0][-1]
                self.labels['quit'] = [pyglet.text.Label(quit_txt,
                                                         font_name='Lucida', batch=self.label_batch,
                                                         font_size=36, x=70, y=100, color=(255, 255, 255, 255)),
                                       True]

                play_txt = tuple(self.text_getter((self.language,), 1))[0][-1]
                self.labels['play'] = [pyglet.text.Label(play_txt,
                                                         font_name='Lucida', batch=self.label_batch,
                                                         font_size=36, x=70, y=200, color=(255, 255, 255, 255)),
                                       True]

            def draw(self):
                super().draw()
                self.label_batch.draw()

            # def display_text(self):
            #
            #     # Quit text
            #     quit_text = tuple(self.text_getter((self.language,), 2))[0][-1]
            #     render = self.font.render(quit_text, True, (255, 255, 255))
            #     rect = render.get_rect().move(70, 540).inflate(-4, -4)
            #
            #     render2 = self.font.render(quit_text, True, (180, 180, 180))
            #     rect2 = render2.get_rect().move(70, 540).inflate(-4, -4)
            #
            #     self.fonts['quit'] = [(render, rect), (render2, rect2), 0]
            #     self.changes.add('quit')
            #
            #     # Play text
            #     play_text = tuple(self.text_getter((self.language,), 1))[0][-1]
            #     render = self.font.render(play_text, True, (255, 255, 255))
            #     rect = render.get_rect().move(70, 440).inflate(-4, -4)
            #
            #     render2 = self.font.render(play_text, True, (180, 180, 180))
            #     rect2 = render2.get_rect().move(70, 440).inflate(-4, -4)
            #
            #     self.fonts['play'] = [(render, rect), (render2, rect2), 0]
            #     self.changes.add('play')

            def is_label_colliding(self, label_name, pos):
                label = self.labels[label_name][0]
                x1, x2 = label.x, label.x + 100
                y1, y2 = label.y, label.y + 50
                return (x1 < pos[0] < x2) and (y1 < pos[1] < y2)

            def activate_label(self, label_name):
                if not self.labels[label_name][-1]:
                    self.labels[label_name][-1] = True
                    self.changes.add(label_name)

            def deactivate_label(self, label_name):
                if self.labels[label_name][-1]:
                    self.labels[label_name][-1] = False
                    self.changes.add(label_name)

            def update(self):

                for label_name in self.changes:
                    if self.labels[label_name][-1]:
                        self.labels[label_name][0].color = (125, 125, 125, 255)
                    else:
                        self.labels[label_name][0].color = (255, 255, 255, 255)

                self.changes.clear()

            def activate(self):
                self.init_text()

            def deactivate(self):
                self.labels.clear()
                self.changes.clear()

        class InGame(_ViewerPage):

            def __init__(self, event_getter, event_binding_dict, action_set, level_id):
                super().__init__(event_binding_dict)
                self.level_id = int(level_id)
                self.sprites = pygame.sprite.Group()
                self.structure_group = pygame.sprite.Group()
                self.window = pygame.display.get_surface()
                self.player_group = pygame.sprite.GroupSingle()
                self.player = None
                self.actions = action_set
                self.bg = None
                self.area = self.window.get_rect()

                self.get_event = event_getter

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
                self.a[0] = -self.player.body.position.x + self.area.width / 2
                # self.a[1] = +self.player.body.position.y - self.area.height / 2
                self.player_group.update()
                self.structure_group.update(self.a)

                self.sprites.clear(self.window, self.bg)
                self.sprites.draw(self.window)

            def bind_events(self, event_handler):
                self.events[KEYDOWN] = event_handler.keydown
                self.events[KEYUP] = event_handler.keyup
                self.events[self.get_event('LANDING')[0]] = event_handler.land
                self.events[self.get_event('STOPPED')[0]] = event_handler.stopped

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
                return np.array(pymunk.pygame_util.to_pygame(p, self.window)) + self.a

            def from_pygame(self, p):
                return np.array(pymunk.pygame_util.to_pygame(p, self.window)) - self.a

            def activate(self):
                pass

            def deactivate(self):
                pass
