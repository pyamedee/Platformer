# -*- coding:Utf-8 -*-

from math import cos, sin
import math

import numpy as np
import pymunk
from pygame.locals import *
from pymunk.vec2d import Vec2d
import pymunk.pygame_util

from operator import truth
import pygame.key

from Classes.my_queue import DequeQueue as Queue
from Classes.handlers import BaseActionHandler, BaseEventHandler
from Classes.my_queue import DequeQueue as Queue
from Classes.my_queue import Empty
from Classes.ordered_set import OrderedSet
from Classes.page_handler import PageHandler
from Scripts.logger import logger

from sprites.sprites import Structure

LANDING = USEREVENT + 1


class Controller:

    def __init__(self, model, viewer):
        logger.debug('initialize Controller')
        self.model = model
        self.viewer = viewer
        self.page_handler = self.ControllerPageHandler()

    def _play(self):  # callback pour StartingPage
        self.viewer.play()
        self.page_handler.switch_page('InGame', self.model, self.viewer, 1)

    def init_pages(self):
        if self.viewer.page_handler.current_page is None:
            self.viewer.init_pages()
        self.page_handler.add_page('StartingPage', self.model, self.viewer, self._play)

    class ControllerPageHandler(PageHandler):

        class _ControllerPage:
            def __init__(self, model, viewer):
                self.viewer = viewer
                self.model = model

            def activate(self):
                raise NotImplementedError

            def deactivate(self):
                raise NotImplementedError

        class StartingPage(_ControllerPage):

            def __init__(self, model, viewer, play_callback):
                super().__init__(model, viewer)
                self.event_handler = None
                self.action_handler = None
                self.play = play_callback

            def activate(self):
                self.action_handler = self.ActionHandler(self.viewer, self.play)
                self.event_handler = self.EventHandler(self.viewer.page_handler.current_page, self.action_handler)

                self.viewer.page_handler.current_page.bind_events(self.event_handler)

            def deactivate(self):
                pass

            class EventHandler(BaseEventHandler):
                def mouse_motion(self, evt):
                    pos = evt.pos
                    for font_name in self.viewer_page.fonts.keys():

                        if self.viewer_page.is_font_colliding(font_name, pos):
                            self.viewer_page.activate_font(font_name)
                        else:
                            self.viewer_page.deactivate_font(font_name)

                def mouse_button_down(self, evt):
                    pos = evt.pos
                    for font_name in self.viewer_page.fonts.keys():
                        if self.viewer_page.is_font_colliding(font_name, pos):
                            self.action_handler('do', font_name)

            class ActionHandler(BaseActionHandler):
                def __init__(self, viewer, play_callback):
                    self.do_quit = viewer.stop_loop
                    self.do_play = play_callback

        class InGame(_ControllerPage):
            def __init__(self, model, viewer, level_id):
                super().__init__(model, viewer)
                self.level_id = int(level_id)
                self.structure_getter = self.model.structure_getter(self.level_id)
                self.level = tuple(self.model.get_level(self.level_id))[0]
                self.viewer_page = None
                self.player_coords = np.array(self.level[1:3], dtype=np.int64)

                self.event_handler = None
                self.action_handler = None

                self.action_queue = OrderedSet()

                self.todo = np.zeros(5, dtype=np.uint8)


                self.gravity = (0, -1000)
                self.space = self.init_pymunk_space(self.gravity)

                self.mods = None
                self.v = None

                self.player = None

                self.spups = 5  # number of space updates per second
                self.dt = 1. / self.viewer.FRAMERATE / self.spups

            @staticmethod
            def init_pymunk_space(gravity):
                space = pymunk.Space()
                space.gravity = gravity

                return space

            def activate(self):
                logger.debug('play button was pressed')
                self.viewer_page = self.viewer.page_handler.current_page
                self.draw_configuration = pymunk.pygame_util.DrawOptions(self.viewer_page.window)
                self.viewer_page.display_bg(self.level[3])

                self.viewer_page.load_structures(self.structure_getter)
                self.viewer_page.load_player(self.player_coords)

                self.player = self.viewer_page.player

                self.viewer_page.display()
                logger.debug('Structure and player were loaded')

                self.action_handler = self.ActionHandler(self.viewer_page, self.viewer.stop_loop)
                self.event_handler = self.EventHandler(self.viewer_page, self.action_handler)

                self.viewer_page.bind_events(self.event_handler)
                self.viewer_page.actions.add(self.update)

                self.viewer_page.player.init_body(self.to_pygame, self.from_pygame, 1.3, 25000)
                self.player.add_to_space(self.space)

                sprites = self.viewer_page.structure_group.sprites()
                for structure in sprites:
                    structure.init_body(self.to_pygame, self.from_pygame,
                                        self.from_pygame((structure.rect.right, structure.rect.top)),
                                        self.from_pygame((structure.rect.left, structure.rect.top)))
                self.space.add(Structure.body, [s.shape for s in sprites])

            def deactivate(self):
                pass

            class EventHandler(BaseEventHandler):
                def __init__(self, viewer_page, action_handler):
                    super().__init__(viewer_page, action_handler)
                    self.controls = {
                        K_d: ('move_right', 'move'),
                        K_a: ('move_left', 'move'),
                        K_SPACE: ('jump', None),
                        K_ESCAPE: ('quit', None),
                    }

                def keydown(self, evt):
                    try:
                        action_name = self.controls[evt.key]
                    except KeyError:
                        return

                    self.action_handler('do', action_name[0])

                def keyup(self, evt):
                    try:
                        action_name = self.controls[evt.key]
                    except KeyError:
                        return

                    self.action_handler('stop', action_name[1])

            class ActionHandler(BaseActionHandler):

                def __init__(self, viewer_page, quit_callback):
                    self.viewer_page = viewer_page
                    self.player = viewer_page.player
                    self.do_quit = quit_callback
                    self.action_queue = Queue()

                def do_move_right(self):
                    if self.player.on_ground:
                        self.player.direction = 1
                        self._move()
                    else:
                        self.action_queue.put(self.do_move_right())

                def do_move_left(self):
                    if self.player.on_ground:
                        self.player.direction = -1
                        self._move()
                    else:
                        self.action_queue.put(self.do_move_right())

                def _move(self):
                    self.player.bf = 1
                    self.player.stopped = False
                    self.player.is_moving = True

                def stop_move(self):
                    self.player.is_moving = False
                    self.player.is_stopping = True

                def do_jump(self):
                    if self.player.on_ground:
                        self.player.body.apply_impulse_at_world_point(
                            (0, 500),
                            self.player.body.position + self.player.body.center_of_gravity)

            def from_pygame(self, d):
                return self.viewer_page.from_pygame(d)

            def to_pygame(self, d):
                return self.viewer_page.to_pygame(d)

            def is_on_ground(self, arbiter):
                shapes = arbiter.shapes
                for shape in shapes:
                    if isinstance(shape, pymunk.Segment) and not getattr(shape, 'iswall', False):
                        self.player.on_ground = True
                        return

            def move(self, is_mods):
                modif = truth(is_mods) + 1
                div = math.sqrt(self.v.dot(self.v)) / 4 + 1
                self.player.body.apply_force_at_local_point(
                    Vec2d(self.player.VELOCITY / div * self.player.direction / modif * self.spups, 0), (0, 0))

            def stop(self):
                if self.player.bf > 30:
                    self.player.is_stumbling = True
                if round(self.v.x) * self.player.direction <= 0:
                    self.player.stopped = True
                    self.player.is_stopping = False
                else:
                    self.player.bf += 1
                    self.player.body.apply_force_at_local_point(
                        Vec2d(-self.player.VELOCITY * self.spups / 15 * self.player.direction, 0), (0, 0))

            def update(self):
                self.mods = pygame.key.get_mods()
                self.v = self.player.body.velocity

                before = self.player.on_ground
                self.player.on_ground = False
                self.player.body.each_arbiter(self.is_on_ground)
                if not before and self.player.on_ground:
                    pygame.event.post(LANDING)

                if self.player.is_moving:
                    self.move(self.mods & KMOD_LCTRL)

                elif self.player.is_stopping:
                    self.stop()

                if self.player.stopped:
                    self.player.body.velocity -= Vec2d(self.v.x, 0)

                elif self.player.is_stumbling:
                    if round(v.x) == 0:
                        self.player.is_stumbling = False
                    else:
                        print('stumbling')

                for _ in range(self.spups):
                    self.space.step(self.dt)

                self.viewer_page.player_group.update()
                self.viewer_page.structure_group.update(self.viewer_page.a)
                #self.space.debug_draw(self.draw_configuration)
