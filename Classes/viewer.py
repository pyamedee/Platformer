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
                self.labels = dict()
                self.label_batch = pyglet.graphics.Batch()
                self.changes = set()

                self.language = general_cfg['language']

            def init_text(self):
                font_size = sp_cfg.getint('font_size')
                font = sp_cfg['font']
                quit_txt = tuple(self.text_getter((self.language,), 2))[0][-1]
                self.labels['quit'] = [pyglet.text.Label(quit_txt,
                                                         font_name=font, batch=self.label_batch,
                                                         font_size=font_size, x=70, y=100, color=(255, 255, 255, 255)),
                                       True]
                play_txt = tuple(self.text_getter((self.language,), 1))[0][-1]
                self.labels['play'] = [pyglet.text.Label(play_txt,
                                                         font_name=font, batch=self.label_batch,
                                                         font_size=font_size, x=70, y=200, color=(255, 255, 255, 255)),
                                       True]

            def draw(self):
                super().draw()
                self.label_batch.draw()

            def is_label_colliding(self, label_name, pos):
                label = self.labels[label_name][0]
                x1, x2 = label.x, label.x + len(label.text) * sp_cfg.getint('font_size') * 0.75
                y1, y2 = label.y, label.y + sp_cfg.getint('font_size')
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
                    sprite = sprites.Structure(structure[0], image,
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

            def activate(self):
                pass

            def deactivate(self):
                pass
