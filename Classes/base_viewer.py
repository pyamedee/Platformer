# -*- coding:Utf-8 -*-

import pygame
from pygame.constants import MOUSEBUTTONDOWN, QUIT

pygame.init()


class BaseViewer:

    def __init__(self, framerate, logger):
        self.logger = logger
        self.logger.debug('initialize BaseViewer')
        self.stop_mainloop = False
        self.events = dict()
        self.actions = set()
        self.FRAMERATE = framerate
        self.clock = pygame.time.Clock()

        self.window = None

    def wdisplay(self, window_size, flags=tuple()):
        self.window = pygame.display.set_mode(window_size, *flags)

    def stop_loop(self):
        self.logger.info('Stopping loop...')
        self.stop_mainloop = True

    def loop(self):
        while not self.stop_mainloop:
            self.clock.tick(self.FRAMERATE)
            for event in pygame.event.get():

                if event.type in self.events.keys():
                    self.events[event.type](event)

                elif event.type == QUIT:
                    self.logger.warning('The game has been force-quited.')
                    return -1

                elif event.type == MOUSEBUTTONDOWN:
                    self.logger.debug(str(self.clock.get_fps()))
            pygame.event.pump()

            for action in self.actions:
                action()

            self.main()

            pygame.display.flip()

        self.logger.info('Done.')
        return 0

    def main(self):
        raise NotImplementedError('Implement this method in subclasses of this class.')
