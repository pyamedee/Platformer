# -*- coding:Utf-8 -*-

import pyglet
from pyglet.window import key
import os

class Viewer0(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.image = pyglet.resource.image('Images/bg.png')

        bouh_image = pyglet.resource.image('Images/player.png')
        bouh_image.anchor_x = bouh_image.width // 2
        bouh_image.anchor_y = bouh_image.height // 2

        self.bouh = pyglet.sprite.Sprite(bouh_image, 50, 200)

        self.fps_display = pyglet.window.FPSDisplay(self)

        self.dt = 1./60.

        self.direction = 0

        self.clock = pyglet.clock.Clock()
        pyglet.clock.schedule_interval(self.update, self.dt)

        self.move = False

    def update(self, _):
        if self.move:
            self.bouh.x += 10 * self.direction
            self.bouh.rotation += 2 * self.direction
            self.bouh.scale += self.direction / 10

    def on_draw(self):
        self.image.blit(0, 0)
        self.bouh.draw()
        self.fps_display.draw()

    def on_key_press(self, symbol, _):
        if symbol == key.D:
            self.direction = 1
        elif symbol == key.Q:
            self.direction = -1
        self.move = True

    def on_key_release(self, *_):
        self.move = False


class BaseViewer:

    def __init__(self, fps, *args, **kwargs):
        self.window = pyglet.window.Window(*args, **kwargs)

        self.fps = fps
        self.dt = 1. / fps

        self.event = self.window.event

        pyglet.clock.schedule_interval(self.update, self.dt)

    def close(self):
        self.window.close()

    def bind(self, event_manager):
        if not isinstance(event_manager, EventManager):
            raise ValueError('event_manager is not an instance of EventManager but of {}'.format(type(event_manager)))
        for name, func in event_manager.get_handlers().items():
            self.window.set_handler(name, func)

    def unbind(self, event_manager):
        if not isinstance(event_manager, EventManager):
            raise ValueError('event_manager is not an instance of EventManager but of {}'.format(type(event_manager)))
        for name, func in event_manager.get_handlers().items():
            self.window.remove_handler(name, func)

    def update(self, *args, **kwargs):
        raise NotImplementedError


class Viewer(BaseViewer):

    def update(self, *args, **kwargs):
        pass


class EventManager:

    def __init__(self):
        self.handlers = {
            'on_key_press': self.hdlr_key_pressed,
            'on_key_release': self.hdlr_key_released
        }

    def get_handlers(self):
        return self.handlers

    def hdlr_key_pressed(self, *_, **__):
        print(0)

    def hdlr_key_released(self, *_, **__):
        print(1)


if __name__ == "__main__":
    viewer = Viewer(1280, 720, fullscreen=False)

    evt_manager = EventManager()
    viewer.bind(evt_manager)

    pyglet.app.run()
