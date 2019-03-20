# -*- coding: Utf-8 -*-

import sys
import pygame
from pygame.locals import *
import sqlite3
import numpy as np

import Scripts.sprites as sprites

DEBUG = False

pygame.init()


class Model:

    def __init__(self):
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
        self.stop_mainloop = False
        self.events = dict()
        self.actions = set()
        self.FRAMERATE = framerate
        self.clock = pygame.time.Clock()

        self.window = None

    def wdisplay(self, window_size, flags=tuple()):
        self.window = pygame.display.set_mode(window_size, *flags)

    def stop_loop(self):
        print('Stopping loop...')
        self.stop_mainloop = True

    def loop(self):
        while not self.stop_mainloop:
            self.clock.tick(self.FRAMERATE)
            for event in pygame.event.get():

                if event.type in self.events.keys():
                    self.events[event.type](event)

                elif event.type == QUIT:
                    return
            pygame.event.pump()

            for action in self.actions:
                action()

            self.main()

            pygame.display.flip()

        print('Done.')

    def main(self):
        raise NotImplementedError('Implement this method in subclasses of this class.')


class Viewer(BaseViewer):
    def __init__(self, framerate=30):
        super(Viewer, self).__init__(framerate)
        self.game = None

    def init_pages(self):
        self.StartingPage(self.events)

        self.Page.switch_page('StartingPage')

    def main(self):
        self.Page.active_page.update()

    class Page:
        _pages = dict()
        active_page = None

        def __init__(self, name, event_dict):
            self.events = event_dict
            self.name = name
            type(self).add_page(self)

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

    class MainMenu(Page):
        def __init__(self, name, event_dict, bg_path):
            super().__init__(name, event_dict)
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

        def __init__(self, event_dict):
            self.name = 'StartingPage'
            bg_path = 'Images\\bg.png'
            super().__init__(self.name, event_dict, bg_path)

            self.sys_font = pygame.font.SysFont('Helvetica', 80, bold=True)
            self.fonts = dict()
            self.changes = set()

        def display_text(self):

            # Quit text
            render = self.sys_font.render('Quit', True, (255, 255, 255))
            rect = render.get_rect().move(70, 540)

            render2 = self.sys_font.render('Quit', True, (180, 180, 180))
            rect2 = render2.get_rect().move(70, 540)

            self.fonts['quit'] = [(render, rect), (render2, rect2), 0]
            self.changes.add('quit')

            #  Play text
            render = self.sys_font.render('Play', True, (255, 255, 255))
            rect = render.get_rect().move(70, 440)

            render2 = self.sys_font.render('Play', True, (180, 180, 180))
            rect2 = render2.get_rect().move(70, 440)

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


class Controller:

    def __init__(self, model, viewer):
        self.model = model
        self.viewer = viewer

    def init_pages(self):
        self.StartingPage(self.model, self.viewer)

        self.Page.switch_page('StartingPage')

    class Page:
        _pages = dict()
        active_page = None

        def __init__(self, model, viewer, name):
            self.name = name
            self.model = model
            self.viewer = viewer
            type(self).add_page(self)

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

    class MainMenu(Page):

        def __init__(self, model, viewer, name):
            super().__init__(model, viewer, name)

        def activate(self):
            if self.viewer.Page.active_page is None:
                self.viewer.init_pages()

        def deactivate(self):
            pass

    class StartingPage(MainMenu):

        def __init__(self, model, viewer):
            self.name = 'StartingPage'
            super().__init__(model, viewer, self.name)
            self.getter = self.viewer.Page.page_getter()
            self.v_starting_page = None  # viewer's Starting Page, attributed on activation
            self.event_handler = None
            self.action_handler = None

        def activate(self):
            super().activate()
            self.v_starting_page = self.getter[self.name]

            self.action_handler = self.ActionHandler(self.viewer, self.play)
            self.event_handler = self.EventHandler(self.v_starting_page, self.action_handler)

            self.v_starting_page.bind_events(self.event_handler)

        def deactivation(self):
            super().deactivate()
            del self.v_starting_page, self.action_handler, self.event_handler

        def play(self):
            print('play')

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

    class BaseInGame(Page):
        def __init__(self, model, viewer, name):
            super().__init__(model, viewer, name)

        def activate(self):
            pass

        def deactivate(self):
            pass

    class InGame(BaseInGame):
        pass


def main():
    model = Model()
    viewer = Viewer(framerate=30)
    controller = Controller(model, viewer)

    flags = tuple() if DEBUG else (FULLSCREEN,)
    viewer.wdisplay((1280, 720), flags)
    controller.init_pages()
    viewer.loop()
    return model, viewer, controller


if __name__ == '__main__':
    main()
    sys.exit()
