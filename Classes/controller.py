# -*- coding:Utf-8 -*-

from math import cos, sin
import math

import numpy as np
import pymunk
from pymunk.vec2d import Vec2d
import pymunk.pyglet_util

import pyglet
from pyglet.window import key

from operator import truth
import pygame.key

from Classes.my_queue import DequeQueue as Queue
from Classes.my_queue import Empty
from Classes.managers import BasePageManager, BaseEventManager, BaseActionManager
from Scripts.logger import logger

from sprites.sprites import Structure


class Controller:

    def __init__(self, model, viewer):
        logger.debug('initialize Controller')
        self.model = model
        self.viewer = viewer
        self.page_manager = self.PageManager()

    def _play(self):  # callback pour StartingPage
        self.viewer.play()
        self.page_manager.switch_page('InGame', self.model, self.viewer, 1, self._return_to_starting_page)

    def _open_options(self):
        self.viewer.page_manager.switch_page('Options', self.viewer.bind, self.viewer.unbind)
        self.page_manager.switch_page('Options', self.model, self.viewer, self._close_options)

    def _close_options(self):
        self._return_to_starting_page()

    def _return_to_starting_page(self):
        self.viewer.init_starting_page()
        self.page_manager.switch_page('StartingPage', self.model, self.viewer, self._play, self._open_options,
                                      self.clear_cache)

    def init_pages(self):
        if self.viewer.page_manager.current_page is None:
            self.viewer.init_starting_page()
        self.page_manager.switch_page('StartingPage', self.model, self.viewer, self._play, self._open_options,
                                      self.clear_cache)

    def clear_cache(self):
        self.page_manager.clear_cache()
        self.viewer.page_manager.clear_cache()

    class PageManager(BasePageManager):

        class _ControllerPage:
            def __init__(self, model, viewer):
                self.viewer = viewer
                self.model = model

            def activate(self):
                raise NotImplementedError

            def deactivate(self):
                raise NotImplementedError

        class StartingPage(_ControllerPage):

            def __init__(self, model, viewer, play_callback, open_options_callback, clear_cache_callback):
                super().__init__(model, viewer)
                self.event_manager = None
                self.action_manager = None
                self.play = play_callback
                self.open_options = open_options_callback
                self.clear_cache = clear_cache_callback

            def activate(self):
                self.action_manager = self.ActionManager(self.viewer, self.play, self.open_options,
                                                         self.clear_cache)
                self.event_manager = self.EventManager(self.viewer.page_manager.current_page, self.action_manager)

                self.viewer.page_manager.current_page.bind(self.event_manager)

            def deactivate(self):
                self.viewer.page_manager.current_page.unbind(self.event_manager)

            class EventManager(BaseEventManager):

                def __init__(self, viewer_page, action_manager):
                    super().__init__(action_manager)
                    self.viewer_page = viewer_page
                    self.handlers = {
                        'on_mouse_motion': self.mouse_motion,
                        'on_mouse_press': self.mouse_button_down,
                        'on_key_press': self.keydown
                    }

                def get_handlers(self):
                    return self.handlers

                def mouse_motion(self, x, y, *_, **__):
                    pos = x, y
                    for label in self.viewer_page.labels.keys():

                        if self.viewer_page.is_label_colliding(label, pos):
                            self.viewer_page.activate_label(label)
                        else:
                            self.viewer_page.deactivate_label(label)

                def mouse_button_down(self, x, y, *_, **__):
                    pos = x, y
                    for label in self.viewer_page.labels.keys():
                        if self.viewer_page.is_label_colliding(label, pos):
                            return self.action_manager('do', label)

                def keydown(self, symbol, *_, **__):
                    if symbol == key.DELETE:
                        self.action_manager('do', 'clear_cache')

            class ActionManager(BaseActionManager):
                def __init__(self, viewer, play_callback, open_options_callback, clear_cache_callback):

                    self.do_quit = viewer.close
                    self.do_play = play_callback
                    self.do_opt = open_options_callback
                    self.do_clear_cache = clear_cache_callback

        class Options(_ControllerPage):
            def __init__(self, model, viewer, close_options_callback):
                super().__init__(model, viewer)
                self.close_options = close_options_callback
                self.event_manager = None
                self.action_manager = None

            class EventManager(BaseEventManager):
                def __init__(self, action_manager):
                    super().__init__(action_manager)

                    self.handlers = {'on_key_press': self.keydown}

                def keydown(self, symbol, *_, **__):
                    if symbol == key.P:
                        self.action_manager('do', 'close_options')

            class ActionManager(BaseActionManager):
                def __init__(self, close_options_callback):
                    super().__init__()
                    self.do_close_options = close_options_callback

            def activate(self):
                self.action_manager = self.ActionManager(self.close_options)
                self.event_manager = self.EventManager(self.action_manager)

                self.viewer.page_manager.current_page.bind(self.event_manager)

            def deactivate(self):
                self.viewer.page_manager.current_page.unbind(self.event_manager)

        class InGame(_ControllerPage):
            def __init__(self, model, viewer, level_id, return_to_starting_page_callback):
                super().__init__(model, viewer)
                self.level_id = int(level_id)
                self.structure_getter = self.model.structure_getter(self.level_id)
                self.level = tuple(self.model.get_level(self.level_id))[0]
                self.viewer_page = None
                self.player_coords = np.array(self.level[1:3], dtype=np.int64)

                self.event_manager = None
                self.action_manager = None

                self.gravity = (0, -1000)
                self.space = self.init_pymunk_space(self.gravity)

                self.mods = None
                self.v = None

                self.player = None

                self.spups = 5  # number of space updates per second
                self.dt = 1. / self.viewer.fps / self.spups

                self.loaded = False

                self.return_to_starting_page = return_to_starting_page_callback
                logger.debug('Game was initialised')

            @staticmethod
            def init_pymunk_space(gravity):
                space = pymunk.Space()
                space.gravity = gravity

                return space

            def load(self):

                self.viewer_page.load_structures(self.structure_getter)
                self.viewer_page.load_player(self.player_coords)

                self.player = self.viewer_page.player

                self.viewer_page.player.init_body(1.3, 35000)
                self.player.add_to_space(self.space)

                shapes = set()
                structures = self.viewer_page.structures
                for structure in structures:
                    static_segments = self.model.get_static_lines(structure.id)
                    for seg in static_segments:
                        structure.add_segment(np.array(seg[2:4]), np.array(seg[4:6]), seg[6], seg[7])

                    static_polygones = self.model.get_static_poly(structure.id, True)
                    for poly in static_polygones:
                        structure.add_poly(np.array(poly[2]), poly[3], poly[4])

                    shapes.update(structure.shapes)

                self.space.add(Structure.body, shapes)

                self.loaded = True
                logger.debug('Sprites were loaded')

            def activate(self):
                self.viewer_page = self.viewer.page_manager.current_page
                self.draw_configuration = pymunk.pyglet_util.DrawOptions()
                # self.viewer_page.display_bg(self.level[3])

                if not self.loaded:
                    self.load()

                self.action_manager = self.ActionManager(self.viewer_page, self.viewer.close,
                                                         self.return_to_starting_page)
                self.event_manager = self.EventManager(self.viewer_page, self.model.get_event, self.action_manager)

                self.viewer_page.bind(self.event_manager)

                self.viewer_page.update = self.update
                self.viewer_page.lock_axis(x=True)

            def update(self):
                self._update()
                self.viewer_page.update_()

            def deactivate(self):
                self.viewer_page.unbind(self.event_manager)
                if self.player.is_moving:
                    self.action_manager.stop_move()

            class EventManager(BaseEventManager):
                def __init__(self, viewer_page, event_getter, action_manager):
                    super().__init__(action_manager)
                    self.viewer_page = viewer_page
                    self.controls = {
                        key.D: ('move_right', 'move'),
                        key.Q: ('move_left', 'move'),
                        key.SPACE: ('jump', None),
                        key.ESCAPE: ('quit', None),
                        key.P: ('lock', None),
                        key.M: ('unlock', None),
                        key.TAB: ('return_to_starting_page', None)
                    }
                    self.handlers = {'on_key_press': self.keydown,
                                     'on_key_release': self.keyup}
                    self.virtual_handlers = {event_getter('LANDING'): self.land,
                                             event_getter('STOPPED'): self.stopped}

                def get_virtual_handlers(self):
                    return self.virtual_handlers

                def keydown(self, symbol, *_, **__):
                    try:
                        action_name = self.controls[symbol]
                    except KeyError:
                        return

                    self.action_manager('do', action_name[0])

                def keyup(self, symbol, *_, **__):
                    try:
                        action_name = self.controls[symbol]
                    except KeyError:
                        return

                    self.action_manager('stop', action_name[1])

                def land(self, *_, **__):
                    self.action_manager.clear_flying_queue()

                def stopped(self, *_, **__):
                    self.action_manager.clear_stopping_queue()

            class ActionManager(BaseActionManager):

                def __init__(self, viewer_page, quit_callback, return_to_starting_page_callback):
                    self.viewer_page = viewer_page
                    self.player = viewer_page.player

                    self.do_quit = quit_callback
                    self.do_return_to_starting_page = return_to_starting_page_callback

                    self.flying_queue = Queue()
                    self.action_queue = Queue()
                    self.stopping_queue = Queue()
                    self.move_or_stop = None

                def do_lock(self):
                    self.viewer_page.lock_axis(x=True)

                def do_unlock(self):
                    self.viewer_page.unlock_axis(x=True)

                def do_move_right(self):
                    if self.player.is_moving:
                        return
                    if not self.player.on_ground:
                        self.move_or_stop = self.do_move_right
                        return
                    if not self.player.is_stopping:
                        self.player.direction = 1
                        return self._move()
                    self.stopping_queue.put(self.do_move_right)

                def do_move_left(self):
                    if self.player.is_moving:
                        return
                    if not self.player.on_ground:
                        self.move_or_stop = self.do_move_left
                        return
                    if not self.player.is_stopping:
                        self.player.direction = -1
                        return self._move()
                    self.stopping_queue.put(self.do_move_left)

                def _move(self):
                    self.player.bf = 1
                    self.player.stopped = False
                    self.player.is_moving = True

                def stop_move(self):
                    if not self.player.on_ground:
                        self.move_or_stop = self.stop_move
                        return
                    self.player.is_moving = False
                    self.player.is_stopping = True

                def do_jump(self):
                    if self.player.on_ground:
                        if self.player.is_stopping:
                            return
                        self.player.is_jumping = True

                def clear_flying_queue(self):
                    if self.move_or_stop is not None:
                        if self.move_or_stop.direction * self.player.body.velocity.x < 0:
                            self.stopping_queue.put(self.move_or_stop)
                            self.move_or_stop = self.stop_move
                        self.move_or_stop()
                        self.move_or_stop = None
                    self.action_queue.update(self.flying_queue.elements())

                def clear_stopping_queue(self):
                    self.action_queue.update(self.stopping_queue.elements())

                def execute_action_queue(self):
                    for action in self.action_queue.elements():
                        action()

                do_move_right.direction = 1
                do_move_left.direction = -1
                stop_move.direction = np.nan

            def is_on_ground(self, arbiter):
                shapes = arbiter.shapes
                for shape in shapes:
                    if getattr(shape, 'is_structure', False) and not getattr(shape, 'iswall', False):
                        self.player.on_ground = True
                        return

            def move(self, is_mods):
                modif = truth(is_mods) + 1
                div = math.sqrt(self.v.x ** 2 + (self.v.y / 2) ** 2) / 6 + 1
                self.player.body.apply_force_at_local_point(
                    Vec2d(self.player.VELOCITY / div * self.player.direction * self.spups, 0), (0, 0))

            def stop(self):
                if self.player.bf > 30:
                    self.player.is_stumbling = True
                if round(self.v.x) * self.player.direction <= 0:
                    self.viewer.post(self.model.get_event('STOPPED'))
                    self.player.stopped = True
                    self.player.is_stopping = False
                else:
                    self.player.bf += 1
                    self.player.body.apply_force_at_local_point(
                        Vec2d(-self.player.VELOCITY * self.spups / 8 * self.player.direction, 0), (0, 0))

            def _update(self):
                self.action_manager.execute_action_queue()
                self.v = self.player.body.velocity
                before = self.player.on_ground
                self.player.on_ground = False
                self.player.body.each_arbiter(self.is_on_ground)
                if not before and self.player.on_ground:
                    self.viewer.post(self.model.get_event('LANDING'))

                if self.player.on_ground:
                    if self.player.is_moving:
                        self.move(0)

                    elif self.player.is_stopping:
                        self.stop()

                else:
                    if self.player.is_moving:
                        self.player.is_moving = False
                        if self.player.direction == -1:
                            self.action_manager.move_or_stop = self.action_manager.do_move_left
                        else:
                            self.action_manager.move_or_stop = self.action_manager.do_move_right
                    self.player.is_stopping = False

                if self.player.stopped:
                    self.player.body.velocity -= Vec2d(self.v.x, 0)
                    self.player.direction = 0

                elif self.player.is_stumbling:
                    if round(self.v.x) == 0:
                        self.player.is_stumbling = False
                    else:
                        print('stumbling')

                if self.player.is_jumping and self.player.on_ground:
                    self.player.is_jumping = False
                    self.player.body.apply_impulse_at_world_point(
                        (0, 650),
                        self.player.body.position + self.player.body.center_of_gravity)

                for _ in range(self.spups):
                    self.space.step(self.dt)

            def delete(self):
                """this function must be call in order to reinitialise the pymunk space"""

                for sprite in self.viewer_page.structures:
                    self.space.remove(sprite.shapes)
                self.space.remove(Structure.body)
                self.space.remove(self.player.shape)
                self.space.remove(self.player.body)
