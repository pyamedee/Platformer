# -*- coding: utf-8 -*-

import sys
import pygame
import numpy as np

FULLSCREEN = QUIT = KEYDOWN = None
from pygame.locals import *
pygame.init()


class BaseViewer:

    def __init__(self, window_size, flags=tuple(), framerate=30):
        self.window = pygame.display.set_mode(window_size, *flags)
        self.stop_mainloop = False
        self.events = dict()
        self.actions = set()
        self.FRAMERATE = framerate
        self.clock = pygame.time.Clock()

    def loop(self):
        while not self.stop_mainloop:
            self.clock.tick(self.FRAMERATE)
            for event in pygame.event.get():

                if event.type in self.events.keys():
                    self.events[event.type](event)

                elif event.type == QUIT:
                    print('Stopping loop...')
                    self.stop_mainloop = True
            pygame.event.pump()

            for action in self.actions:
                action()

            self.main()

            pygame.display.flip()

        print('Done.')

    def main(self):
        raise NotImplementedError('Implement this method in subclasses of this class.')


class Block(pygame.sprite.Sprite):

    def __init__(self, image):
        super(Block, self).__init__()

        self.image = image
        self.rect = image.get_rect()
        self.area = pygame.display.get_surface().get_rect()

    def calculate_new_position(self, velocity, angle):
        dx = np.cos(angle) * velocity
        dy = np.sin(angle) * velocity
        return self.rect.move(dx, dy)

    def update(self, velocity, angle):
        new_rect = self.calculate_new_position(velocity, angle)
        self.rect = new_rect


class Viewer(BaseViewer):

    def __init__(self, window_size, window_options=(), framerate=30):
        super(Viewer, self).__init__(window_size, window_options, framerate)
        self.image = pygame.image.load('Images\\bg.png').convert()
        self.image_rect = self.image.get_rect()

        self.window.blit(self.image, self.image_rect)

        self.events[KEYDOWN] = self.event_keydown_handler
        self.events[KEYUP] = self.event_keyup_handler

        self.group = pygame.sprite.Group()
        img = pygame.image.load(''.join(('C:\\Users\\Hélène Le Berre\\Documents\\Programation\\pyalb\\pyalb',
                                         '\\src\\Platformer\\Images\\Blocks\\!Font videD;solid=0;id=4!.png'))).convert()

        self.group.add(Block(img))
        self.group.draw(self.window)
        self.angle = 0

        self.key_queue = dict()
        self.ctrls = {
            K_a: self.left,
            K_d: self.right
        }

    def event_keydown_handler(self, evt):
        key = evt.key
        if key == K_x:
            print(self.clock.get_fps())
        else:
            func = self.ctrls.get(evt.key, None)
            if func is not None:
                self.key_queue[key] = func
                self.actions.add(func)

    def event_keyup_handler(self, evt):
        if evt.key in self.key_queue.keys():
            self.actions.remove(self.key_queue[evt.key])
            self.key_queue.pop(evt.key)

    def left(self):
        self._move_image((4, 0))

    def right(self):
        self._move_image((-4, 0))

    def _move_image(self, way):
        self.image_rect.move_ip(*way)

    def main(self):
        self.angle += 0.1
        velocity = 5
        self.window.blit(self.image, self.image_rect)
        self.group.update(velocity, self.angle)
        self.group.draw(self.window)


if __name__ == '__main__':
    viewer = Viewer((1280, 720), [FULLSCREEN], framerate=30)
    viewer.loop()
    del viewer
