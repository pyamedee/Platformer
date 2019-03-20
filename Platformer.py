# -*- coding: utf-8 -*-


import pickle
import sys
import numpy as np
from ordered_set import OrderedSet

import tkinter as tk
from PIL import Image, ImageTk
from glob import iglob
import os
from time import perf_counter
from setup_level import load_blocks, parse_level, properly_resize_img

IMAGES_PATH = './Images/'
CONTROLS = {
    'D': ('move', 'right'),
    'Q': ('move', 'left')
}


class Viewer(tk.Frame):

    def __init__(self, master, **kwargs):
        super(Viewer, self).__init__(master, **kwargs)

        self.root = master
        self.root.attributes('-fullscreen', True)

        self.screenwidth = self.root.winfo_screenwidth()
        self.screenheight = self.root.winfo_screenheight()

        self.canvas = tk.Canvas(self)
        self.canvas['highlightthickness'] = 0
        self.canvas.pack(fill='both', expand=True)

        self.main_menu_displayer = None
        self.game_displayer = None

    def display_main_menu(self, function_on_click):
        self.canvas.bind('<Button-1>', function_on_click)
        self.canvas.focus_set()
        self.main_menu_displayer = self.MainMenuDisplayer(self.canvas, self.screenwidth, self.screenheight)

    def start_game(self):
        del self.main_menu_displayer
        self.canvas.delete('all')
        self.canvas.unbind('<Button-1>')

        self.game_displayer = self.GameDisplayer(self.canvas)

    def bind_events(self, callback_keypress, callback_keyrelease):
        self.canvas.bind('<KeyPress>', callback_keypress)
        self.canvas.bind('<KeyRelease>', callback_keyrelease)

    class MainMenuDisplayer:

        def __init__(self, canvas, screenwidth, screenheight):

            self.canvas = canvas

            self.mmbg_img = tk.PhotoImage(file='Images/bg.png')
            self.canvas.create_image(0, 0, image=self.mmbg_img, anchor='nw')

            self.screenwidth = screenwidth
            self.screenheight = screenheight

            self.level_choice_displayer = None

            self.display_text()

        def display_text(self):

            self.canvas.create_text(
                self.screenwidth // 7,
                self.screenheight // 7 * 5 - 100,
                text="New Game",
                fill="white",
                activefill="gray",
                font=["Lucida", 38],
                tags=("text", 'new_game')
            )

            self.canvas.create_text(
                self.screenwidth // 7 - 40,
                self.screenheight // 7 * 5,
                text="Options",
                fill="white",
                activefill="gray",
                font=["Lucida", 38],
                tags=("text", 'options')
            )

            self.canvas.create_text(
                self.screenwidth // 7 - 80,
                self.screenheight // 7 * 5 + 100,
                text="Quit",
                fill="white",
                activefill="gray",
                font=["Lucida", 38],
                tags=("text", 'quit')
            )

        def delete_text(self):
            self.canvas.delete('text')

    class GameDisplayer:

        def __init__(self, canvas):
            self.canvas = canvas
            self.player_image = None
            self.level_image = None

        def display_player(self, img, coords):
            self.player_image = ImageTk.PhotoImage(img)
            self.canvas.create_image(*coords.flat, image=self.player_image, tag='player')
            self.canvas.tag_raise('player')

        def display_level(self, img, coords):
            self.level_image = ImageTk.PhotoImage(img)
            self.canvas.create_image(*coords.flat, image=self.level_image, tag='level')
            self.canvas.tag_lower('level')


class Controller:

    def __init__(self, model, viewer):

        self.model = model
        self.viewer = viewer

        self.n_x = 20
        self.n_y = None

        self.level_img = None
        self.array_level_img = None

        self.mainmenu_controller = None
        self.ingame_controller = None

        self.mainmenu_controller = self.MainMenu(self.viewer, self.start_game)
        self.viewer.display_main_menu(self.mainmenu_controller.click)

        self.binfos = None

    def load_level(self, path):

        with open(path, 'rb') as level_file:
            unpickler = pickle.Unpickler(level_file)
            level = unpickler.load()

        array_map = level.get('array_map', None)
        if array_map is None:
            raise KeyError('Loaded dictionary must have an "array_map" key.')

        blocks = load_blocks(IMAGES_PATH + 'Blocks/')
        aunresized_level_img, self.model.solid_blocks_array = parse_level(array_map, blocks)

        unresized_level_img = Image.fromarray(aunresized_level_img)

        self.level_img = properly_resize_img(unresized_level_img, self.viewer.screenheight, 70)
        self.binfos = (70,  'h')

        level_data = level.get('level_data', None)
        if level_data is None:
            raise KeyError('Loaded dictionary must have an "level_data" key.')

        self.model.load_lvldata(level_data)

        print(0)

    class MainMenu:

        def __init__(self, viewer, start_game_callback):

            self.current_menu = 'main'

            self.viewer = viewer
            self.start = start_game_callback

        def click(self, evt):
            item = self.viewer.canvas.find_closest(evt.x, evt.y)

            if item and item != self.viewer.main_menu_displayer.mmbg_img:
                tags = self.viewer.canvas.gettags(item[0])
                try:
                    try:
                        getattr(self, tags[1])(tags[2])
                    except TypeError:
                        getattr(self, tags[1])()
                except IndexError:
                    pass

        def new_game(self):
            self.current_menu = None
            print('new_game')
            self.start()

        def options(self):
            print('options')

        def quit(self):
            self.viewer.quit()
            sys.exit()

    def start_game(self):
        del self.mainmenu_controller

        self.viewer.start_game()
        self.ingame_controller = self.InGame(self.viewer, self.model, self.level_img, self.binfos, 'relative2top_left')
        event_handler = self.ingame_controller.event_handler
        self.viewer.bind_events(event_handler.key_press, event_handler.key_release)

    class InGame:

        def __init__(self, viewer, model, level_img, binfos, onscreen_player_coords='center'):

            self.viewer = viewer
            self.model = model

            self.CENTER = np.array((self.viewer.screenwidth // 2, self.viewer.screenheight // 2))

            #  Determines the on-screen size of one single block
            n, horw = binfos
            n = int(n)
            onscreen_bsize = self.viewer.screenheight / n if horw == 'h' else self.viewer.screenwidth / n
            self.B = onscreen_bsize
            print(self.B)

            if onscreen_player_coords == 'center':
                self.onscreen_player_coords = self.CENTER
            elif onscreen_player_coords == 'relative2top_left':
                self.onscreen_player_coords = self.rl2ons(self.model.player_coords)
            else:
                self.onscreen_player_coords = onscreen_player_coords

            #  Level img creation
            base_levelimg_coords = self.onscreen_player_coords + tuple(
                int(round(a / 2 - self.B / 2)) for a in level_img.size)
            self.level_img_coords = base_levelimg_coords - self.model.player_coords * self.B

            player_image = Image.open('pers.png').resize((int(round(self.B)),) * 2, Image.NEAREST)
            self.viewer.game_displayer.display_level(level_img, self.level_img_coords)
            self.viewer.game_displayer.display_player(player_image, self.onscreen_player_coords)

            self.action_handler = self.ActionHandler(self.viewer.canvas)
            self.event_handler = self.EventHandler(globals()['CONTROLS'], self.action_handler)
            self.action_handler.init(self.event_handler.next_action)

        def rl2ons(self, coords):
            """Coverts "real" coordinates to on-screen coordinates.
            Real coordinates are based on the entity position inside the level, on-screen coordinates are based on
            entity image on screen.
            """
            return coords * self.B + int(round(self.B / 2))

        class ActionHandler:

            def __init__(self, canvas):
                self.canvas = canvas
                self.callback = None

            def init(self, callback):
                self.callback = callback
                for attr in dir(self):
                    if attr.startswith('_') and not attr.endswith('__'):
                        action_type = getattr(self, attr)
                        setattr(self, attr[1:].lower(), action_type(self.canvas, self.callback))

            def __call__(self, action):
                getattr(getattr(self, action[0]), action[1])()

            class _Move:

                def __init__(self, canvas, callback):
                    self.canvas = canvas
                    self.callback = callback
                    self.ways = {
                        'right': (4, 0),
                        'left': (-4, 0)
                    }

                def left(self):
                    self._move('left')

                def right(self):
                    self._move('right')

                def _move(self, way):
                    self.canvas.after(32, self._end_of_action)
                    self.canvas.move('player', *self.ways[way])

                def _end_of_action(self):
                    self.callback()

        class EventHandler:

            def __init__(self, key2action, action_handler):
                self.input_queue = OrderedSet()
                self.key2action = key2action
                self.action_handler = action_handler
                self.actionisrunning = False

            def key_press(self, evt):
                key = evt.keysym.upper()
                action = self.key2action.get(key, None)
                if action is not None:
                    self.input_queue.add(action)
                    if not self.actionisrunning:
                        self.next_action()

            def key_release(self, evt):
                key = evt.keysym.upper()
                action = self.key2action.get(key, None)
                if action is not None:
                    self.input_queue.discard(action)
                    if not self.actionisrunning:
                        self.next_action()

            def next_action(self):
                if self.input_queue:
                    self.actionisrunning = True
                    action = self.input_queue[-1]
                    self.action_handler(action)
                else:
                    self.actionisrunning = False


class Model:

    def __init__(self):

        self.solid_blocks_array = None
        self.player_coords = None
        self.static_entities = None
        self.dynamic_entities = None

    def load_lvldata(self, data):
        try:
            # self.player_coords = np.array(data['player_coords'], dtype=np.int32)
            self.player_coords = np.array((8, 5))

        except KeyError as e:
            #  add logger
            raise e

        self.static_entities = data.get('static_entities', None)
        if self.static_entities is not None:
            self.load_static_entities()

    def load_static_entities(self):
        pass


if __name__ == '__main__':

    root = tk.Tk()
    pr_viewer = Viewer(root)
    pr_model = Model()
    controller = Controller(pr_model, pr_viewer)
    pr_viewer.pack(fill='both', expand=1)
    controller.load_level('Levels/test/level_test.lvl')

    root.mainloop()
