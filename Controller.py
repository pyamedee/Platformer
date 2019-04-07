# -*- coding:Utf-8 -*-

from logger import logger
from math import cos, sin
from page_handler import PageHandler
import numpy as np


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

            class EventHandler:
                def __init__(self, viewer_page, action_handler):
                    self.viewer_page = viewer_page
                    self.action_handler = action_handler

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

            class ActionHandler:
                def __init__(self, viewer, play_callback):
                    self.viewer = viewer
                    self.play = play_callback

                def __call__(self, name):
                    getattr(self, name)()

                def quit(self):
                    self.viewer.stop_loop()

        class InGame(_ControllerPage):
            def __init__(self, model, viewer, level_id):
                super().__init__(model, viewer)
                self.level_id = int(level_id)
                self.structure_getter = self.model.structure_getter(self.level_id)
                self.level = tuple(self.model.get_level(self.level_id))
                self.viewer_page = None
                self.player_coords = np.array(self.level[1:3], dtype=np.int64)

            def activate(self):
                logger.debug('play button was pressed')
                self.viewer_page = self.viewer.page_handler.current_page

                self.viewer_page.load_structures(self.structure_getter)
                self.viewer_page.load_player(self.player_coords)

                logger.debug('Structure and player were loaded')

            def deactivate(self):
                pass
