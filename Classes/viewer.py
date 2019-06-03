# -*- coding:Utf-8 -*-

from Scripts.logger import logger
import pyglet

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
        self.page_manager.switch_page('InGame', self.bind, self.unbind, 1, (self.width, self.height))

    def on_draw(self):
        self.page_manager.current_page.draw()
        self.set_caption(str(pyglet.clock.get_fps()))

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
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

            def __init__(self, event_binding_callback, event_unbinding_callback, level_id, screen_dimension):
                super().__init__(event_binding_callback, event_unbinding_callback)
                self.level_id = int(level_id)

                self.batch = pyglet.graphics.Batch()

                self.width, self.height = screen_dimension

                self.ord1 = pyglet.graphics.OrderedGroup(1)
                self.ord0 = pyglet.graphics.OrderedGroup(0)

                self.bg_image = pyglet.image.load('Images/level1_bg.png')
                self.bg = pyglet.sprite.Sprite(self.bg_image, x=0, y=0, batch=self.batch, group=self.ord0)

                self.player = None
                self.sprites = set()
                self.structures = set()

                self.a = np.zeros(2, dtype=np.int32)  # decalage additionnel dans la conversion pymunk <-> pyglet
                self.locked = np.zeros(2, dtype=np.bool)
                self.locking_coords = np.zeros(2, np.int64)

            def draw(self):
                self.batch.draw()

            def load_structures(self, structures):
                image = pyglet.image.load('Images/platform.png')
                for structure in structures:
                    label = structure[4]
                    print(structure)
                    sprite = sprites.Structure(image,
                                               x=structure[2], y=structure[3], batch=self.batch, group=self.ord1)
                    self.sprites.add(sprite)
                    self.structures.add(sprite)

            def load_player(self, coords):

                image = pyglet.image.load('Images/player.png')
                print(coords)
                player = sprites.Player(image, x=coords[0], y=coords[1], batch=self.batch, group=self.ord1)
                self.sprites.add(player)
                self.player = player

            @staticmethod
            def update():
                pass

            def lock_axis(self, x=False, y=False):
                if x:
                    self.locked[0] = True
                    self.locking_coords[0] = self.player.body.position.x + self.a[0]
                if y:
                    self.locked[1] = True
                    self.locking_coords[1] = self.player.body.position.y + self.a[1]

            def unlock_axis(self, x=False, y=False):
                if x:
                    self.locked[0] = False
                if y:
                    self.locked[1] = False

            def update_(self):
                x = y = None
                if self.locked[0]:
                    x = self.locking_coords[0]
                    self.a[0] = -self.player.body.position.x + x

                if self.locked[1]:
                    y = self.locking_coords[1]
                    self.a[1] = -self.player.body.position.y + y

                for sprite in self.structures:
                    sprite.update(self.a)
                self.player.update(x, y, self.a)

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

            def activate(self):
                pass

            def deactivate(self):
                pass
