# -*- coding:Utf-8 -*-

from Scripts.logger import logger
from math import cos, sin
from Classes.page_handler import PageHandler
from Classes.handlers import BaseEventHandler, BaseActionHandler
from Classes.ordered_set import OrderedSet
from Classes.my_queue import DequeQueue as Queue, Empty


import numpy as np
from pygame.locals import *

import pymunk
from pymunk.vec2d import Vec2d


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
                            self.action_handler(font_name)

            class ActionHandler(BaseActionHandler):
                def __init__(self, viewer, play_callback):
                    self.viewer = viewer
                    self.do_play = play_callback

                def do_quit(self):
                    self.viewer.stop_loop()

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

                self.gravity = (0, -1000)
                self.space = self.init_pymunk_space(self.gravity)

            @staticmethod
            def init_pymunk_space(gravity):
                space = pymunk.Space()
                space.gravity = gravity

                return space

            def activate(self):
                logger.debug('play button was pressed')
                self.viewer_page = self.viewer.page_handler.current_page

                self.viewer_page.display_bg(self.level[3])

                self.viewer_page.load_structures(self.structure_getter)
                self.viewer_page.load_player(self.player_coords)

                self.viewer_page.display()
                logger.debug('Structure and player were loaded')

                self.action_handler = self.ActionHandler(self.viewer_page, self.viewer.stop_loop)
                self.event_handler = self.EventHandler(self.viewer_page, self.action_handler)

                self.viewer_page.bind_events(self.event_handler)
                self.viewer_page.actions.add(self.update)

            def deactivate(self):
                pass

            class EventHandler(BaseEventHandler):
                def __init__(self, viewer_page, action_handler):
                    super().__init__(viewer_page, action_handler)
                    self.controls = {
                        K_d: 'move_right',
                        K_a: 'move_left',
                        K_SPACE: 'jump',
                        K_ESCAPE: 'quit',
                        K_w: 'tp',
                        K_i: 'refresh_structures'
                    }

                def keydown(self, evt):
                    action_name = self.controls.get(evt.key, None)
                    if action_name is not None:
                        self.action_handler(action_name)

                def keyup(self, evt):
                    action_name = self.controls.get(evt.key, None)
                    if action_name is not None:
                        try:
                            self.action_handler(action_name, stop=True)
                        except AttributeError:
                            pass

            class ActionHandler(BaseActionHandler):
                def __init__(self, viewer_page, quit_callback):
                    self.viewer_page = viewer_page
                    self.quit_callback = quit_callback

                    self.queue = OrderedSet()

                def do_move_right(self):
                    if not self.viewer_page.player.isfalling:
                        self.viewer_page.player.vector += np.array((80, 0))
                    else:
                        self.queue.add(self.do_move_right)

                def stop_move_right(self):
                    if not self.stop_moving():
                        self.queue.add(self.stop_move_right)

                def stop_move_left(self):
                    if not self.stop_moving():
                        self.queue.add(self.stop_move_left)

                def stop_moving(self):
                    if not self.viewer_page.player.isfalling:
                        self.viewer_page.player.vector[0] = 0
                        return True
                    return False

                def do_move_left(self):
                    if not self.viewer_page.player.isfalling:
                        self.viewer_page.player.vector += np.array((-80, 0))
                    else:
                        self.queue.add(self.do_move_left)

                def do_jump(self):
                    if not self.viewer_page.player.isfalling:
                        self.viewer_page.player.vector += np.array((0, -130))
                        self.viewer_page.player.isfalling = True

                def do_quit(self):
                    self.quit_callback()

                def do_refresh_structures(self):
                    self.viewer_page.refresh_structures()

                def do_tp(self):
                    player = self.viewer_page.player

                    player.isfalling = True
                    player.vector[:] = 0, 2
                    player.place(4, 5)
                    print(self.queue)

            def update_state(self):
                vector = self.viewer_page.player.vector
                sprite = self.viewer_page.is_player_on_ground()
                if sprite:
                    vector[1] = (sprite.rect.top - self.viewer_page.player.rect.bottom) * 10
                    if self.viewer_page.player.isfalling:
                        self.viewer_page.player.isfalling = False
                        self.action_queue.update(self.action_handler.queue)
                        self.action_handler.queue.clear()
                else:
                    if not self.viewer_page.player.isfalling:
                        self.viewer_page.player.isfalling = True

            def update_vector(self):
                if self.viewer_page.player.isfalling:
                    self.viewer_page.player.vector += (0, 4)
                else:
                    self.viewer_page.player.vector[1] = 0

            def update(self):
                self.update_vector()
                self.update_state()

                self.viewer_page.player_group.update(*self.viewer_page.player.vector / 10)
                for action in self.action_queue:
                    action()
                self.action_queue.clear()


