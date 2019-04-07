# -*- coding: Utf-8 -*-

import sys
import pygame
from pygame.locals import *
import sqlite3
import numpy as np
from math import sin, cos
import logging as lg
from logging.handlers import RotatingFileHandler


import Scripts.sprites as sprites

DEBUG = False

logger = lg.getLogger('main')
logger.setLevel(lg.DEBUG)

formatter = lg.Formatter('%(asctime)s | %(levelname)s | %(message)s')

file_handler = RotatingFileHandler('platformer.log', 'a', 1000000, 1)

file_handler.setLevel(lg.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

stream_handler = lg.StreamHandler()

stream_handler.setLevel(lg.DEBUG)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

pygame.init()


class _Page:

    _pages = dict()
    active_page = None

    def __new__(cls, *args, **kwargs):
        instance = object.__new__(cls)
        cls._pages[cls.name] = instance
        return instance

    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    def add_page(cls, instance):
        cls._pages[instance.name] = instance
        return instance

    @classmethod
    def pop_page(cls, name):
        return cls._pages.pop(name)

    @classmethod
    def switch_page(cls, new_page):
        page_instance = cls._pages[new_page]
        if isinstance(page_instance, cls):
            page_instance.activate()
            if cls.active_page is not None:
                cls.active_page.deactivate()
            cls.active_page = page_instance
        else:
            raise TypeError('pages must be a page instance in order to be activated')

    class _Getter:
        def __init__(self, pages):
            self._pages = pages

        def __getitem__(self, item):
            return self._pages[item]

    @classmethod
    def page_getter(cls):
        return cls._Getter(cls._pages)

    def activate(self):
        raise NotImplementedError

    def deactivate(self):
        raise NotImplementedError


dict1 = dict2 = dict(_Page.__dict__)
dict1['_pages'] = dict()
dict2['_pages'] = dict()
BaseViewerPage = type('base viewer page', (object,), dict1)
BaseControllerPage = type('base controller page', (object,), dict2)
del dict1, dict2


class Model:

    def __init__(self):
        logger.debug('initialize Model')
        self.database_connection = sqlite3.connect('data.db')
        self.cursor = self.database_connection.cursor()

    def get_level(self, level_id=-1):

        code = '''SELECT id, base_pos_x, base_pos_y, label
        FROM LevelBaseInfo JOIN BackgroundType on LevelBaseInfo.bg_id = BackgroundType.bg_id'''
        args = []

        if level_id != -1:
            code += ' WHERE id = ?'
            args.append(level_id)

        return self.cursor.execute(code, args)

    def get_structures(self, level_id=-1, structure_id=-1):

        code = '''SELECT id, level_id, pos_x, pos_y, label
        FROM LevelStructures JOIN StructureType on LevelStructures.type = StructureType.structure_id'''

        args = []

        if structure_id != -1:
            code += ' WHERE id = ?'
            args.append(structure_id)

        elif level_id != -1:
            code += ' WHERE level_id = ?'
            args.append(level_id)

        return self.cursor.execute(code, args)

    def structure_getter(self, level_id=-1):
        return self._StructureGetter(self.get_structures(level_id))

    class _StructureGetter:
        def __init__(self, structures):
            self._structures = tuple(structures)
            self._dif = self._structures[0][0]

        def __getitem__(self, index):
            return self.get(index)

        def get(self, index, default=None):
            try:
                if index < 1:
                    raise IndexError
                value = self._structures[index - self._dif]
            except IndexError:
                if default is not None:
                    return default
                raise IndexError('id "{}" does not exist or is out of range'.format(index))
            return value

        def __repr__(self):
            tab = tuple(repr(a) for a in self._structures)
            return 'struct([' + (',\n' + ' ' * 8).join(tab) + '])'

        def __str__(self):
            return repr(self._structures)

        def __iter__(self):
            return iter(self._structures)


class BaseViewer:

    def __init__(self, framerate):
        logger.debug('initialize BaseViewer')
        self.stop_mainloop = False
        self.events = dict()
        self.actions = set()
        self.FRAMERATE = framerate
        self.clock = pygame.time.Clock()

        self.window = None

    def wdisplay(self, window_size, flags=tuple()):
        self.window = pygame.display.set_mode(window_size, *flags)

    def stop_loop(self):
        logger.info('Stopping loop...')
        self.stop_mainloop = True

    def loop(self):
        while not self.stop_mainloop:
            self.clock.tick(self.FRAMERATE)
            for event in pygame.event.get():

                if event.type in self.events.keys():
                    self.events[event.type](event)

                elif event.type == QUIT:
                    logger.warning('The game has been force-quited.')
                    return -1
            pygame.event.pump()

            for action in self.actions:
                action()

            self.main()

            pygame.display.flip()

        logger.info('Done.')
        return 0

    def main(self):
        raise NotImplementedError('Implement this method in subclasses of this class.')


class Viewer(BaseViewer):
    def __init__(self, framerate=30):
        logger.debug('initialize Viewer')
        super(Viewer, self).__init__(framerate)

    def init_pages(self):
        self.StartingPage(self.events)
        self.Level1(self.events)

        self.ViewerPage.switch_page('StartingPage')

    def main(self):
        self.ViewerPage.active_page.update()

    class ViewerPage(BaseViewerPage):
        def __init__(self, event_dict):
            self.events = event_dict

    class MainMenu(ViewerPage):
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

    class StartingPage(MainMenu):
        name = 'StartingPage'

        def __init__(self, event_dict):
            self.name = 'StartingPage'
            bg_path = 'Images\\bg.png'
            super().__init__(event_dict, bg_path)

            self.font = pygame.font.Font('.\\Lucida.ttf', 60)
            self.fonts = dict()
            self.changes = set()

        def display_text(self):

            # Quit text
            render = self.font.render('Quit', True, (255, 255, 255))
            rect = render.get_rect().move(70, 540).inflate(-4, -4)

            render2 = self.font.render('Quit', True, (180, 180, 180))
            rect2 = render2.get_rect().move(70, 540).inflate(-4, -4)

            self.fonts['quit'] = [(render, rect), (render2, rect2), 0]
            self.changes.add('quit')

            #  Play text
            render = self.font.render('Play', True, (255, 255, 255))
            rect = render.get_rect().move(70, 440).inflate(-4, -4)

            render2 = self.font.render('Play', True, (180, 180, 180))
            rect2 = render2.get_rect().move(70, 440).inflate(-4, -4)

            self.fonts['play'] = [(render, rect), (render2, rect2), 0]
            self.changes.add('play')

        def bind_events(self, event_handler):
            self.events[MOUSEMOTION] = event_handler.mouse_motion
            self.events[MOUSEBUTTONDOWN] = event_handler.mouse_button_down

        def update(self):

            for font_name in self.changes:
                font = self.fonts[font_name]
                i = font[-1]
                self.window.blit(font[i][0], font[i][1])

            self.changes.clear()

        def activate(self):
            super().activate()
            self.display_text()

        def deactivate(self):
            self.events.pop(MOUSEMOTION)

    class BaseInGame(ViewerPage):
        pass

    class InGame(BaseInGame):

        def __init__(self, event_dict, level_id):
            super().__init__(event_dict)
            self.level_id = int(level_id)
            self.sprites = pygame.sprite.Group()
            self.structure_group = pygame.sprite.Group()
            self.player = None

        def load_structures(self, structures):

            for structure in structures:
                label = structure[4]
                sprite = sprites.Structure(structures[1:3], 'bouh')
                self.sprites.add(sprite)
                self.structure_group.add(sprite)

        def load_player(self, coords):

            player = sprites.Player(coords, 'image')
            self.sprites.add(player)
            self.player = player

    class Level1(InGame):
        name = 'Level1'

        def __init__(self, event_dict):
            super().__init__(event_dict, 1)


class Controller:

    def __init__(self, model, viewer):
        logger.debug('initialize Controller')
        self.model = model
        self.viewer = viewer

    def init_pages(self):
        self.StartingPage(self.model, self.viewer)
        self.Level1(self.model, self.viewer)

        self.ControllerPage.switch_page('StartingPage')

    class ControllerPage(BaseControllerPage):
        def __init__(self, model, viewer):
            self.viewer = viewer
            self.model = model

    class MainMenu(ControllerPage):

        def __init__(self, model, viewer):
            super().__init__(model, viewer)

        def activate(self):
            if self.viewer.ViewerPage.active_page is None:
                self.viewer.init_pages()

        def deactivate(self):
            pass

    class StartingPage(MainMenu):
        name = 'StartingPage'

        def __init__(self, model, viewer):
            self.name = 'StartingPage'
            super().__init__(model, viewer)
            self.getter = self.viewer.ViewerPage.page_getter()
            self.v_starting_page = None  # viewer's Starting Page, attributed on activation
            self.event_handler = None
            self.action_handler = None

        def activate(self):
            super().activate()
            self.v_starting_page = self.getter[self.name]

            self.action_handler = self.ActionHandler(self.viewer, self.play)
            self.event_handler = self.EventHandler(self.v_starting_page, self.action_handler)

            self.v_starting_page.bind_events(self.event_handler)

        def deactivate(self):
            super().deactivate()
            del self.v_starting_page, self.action_handler, self.event_handler

        def play(self):
            pass

        class EventHandler:
            def __init__(self, v_starting_page, action_handler):
                self.v_starting_page = v_starting_page
                self.action_handler = action_handler

            def mouse_motion(self, evt):
                pos = evt.pos
                for font_name, font in self.v_starting_page.fonts.items():
                    i = font[-1]
                    if font[i][1].collidepoint(pos):
                        if not font[-1]:
                            font[-1] = True
                            self.v_starting_page.changes.add(font_name)
                    else:
                        if font[-1]:
                            font[-1] = False
                            self.v_starting_page.changes.add(font_name)

            def mouse_button_down(self, evt):
                pos = evt.pos
                for font_name, font in self.v_starting_page.fonts.items():
                    i = font[-1]
                    if font[i][1].collidepoint(pos):
                        self.action_handler(font_name)

        class ActionHandler:
            def __init__(self, viewer, play_callback):
                self.viewer = viewer
                self.play = play_callback

            def __call__(self, name):
                getattr(self, name)()

            def quit(self):
                self.viewer.stop_loop()

    class BaseInGame(ControllerPage):
        def __init__(self, model, viewer):
            super().__init__(model, viewer)

        def activate(self):
            pass

        def deactivate(self):
            pass

    class InGame(BaseInGame):
        def __init__(self, model, viewer, level_id):
            super().__init__(model, viewer)
            self.level_id = int(level_id)
            self.structure_getter = self.model.structure_getter(self.level_id)
            self.level = self.model.get_level(self.level_id)

    class Level1(InGame):
        name = 'Level1'

        def __init__(self, model, viewer):
            level_id = 1
            super().__init__(model, viewer, level_id)


def main():
    logger.info('Launching Platformer_v2.pyw')
    model = Model()
    viewer = Viewer(framerate=30)
    controller = Controller(model, viewer)

    flags = tuple() if DEBUG else (FULLSCREEN,)
    viewer.wdisplay((1280, 720), flags)
    controller.init_pages()
    return viewer.loop()


if __name__ == '__main__':
    sys.exit(main())
