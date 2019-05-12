# -*- coding:UTF-8 -*-

import numpy as np
from numpy import cos, sin
from pygame import Rect
from pygame.sprite import Sprite
import pymunk
from math import pi
from pymunk.vec2d import Vec2d

D45 = pi / 4


class BaseSprite(Sprite):

    def __init__(self, coords, image):
        super().__init__()
        self.image = image
        self.rect = image.get_rect().move(tuple(coords))
        self.coords = coords


class Structure(BaseSprite):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    body.position = 0, 0

    def __init__(self, coords, image):
        super().__init__(coords, image)

        self.radius = self.rect.width

        self.to_pygame = self.from_pygame = self.shape = self.a = self.b = None

    def init_body(self, to_pygame_callback, from_pygame_callback, a, b, thickness=5, iswall=False):
        self.from_pygame = from_pygame_callback
        self.to_pygame = to_pygame_callback

        self.shape = pymunk.Segment(type(self).body, a, b, thickness)
        self.shape.friction = 1
        if iswall:
            self.shape.iswall = True
        self.a = self.to_pygame(a)
        self.b = self.to_pygame(b)

    def update(self):
        self.coords = self.to_pygame(self.body.position)
        self.rect.x, self.rect.y = self.coords
        print(self.rect)
        # - Vec2d(
        # self.rect.width / 2, self.rect.height - self.radius)


class Player0(BaseSprite):
    def __init__(self, coords, image):
        super(Player, self).__init__(coords, image)
        self.isfalling = False
        self.bottom_rect = None
        self.place(self.rect.left, self.rect.top)
        self.vector = np.zeros(2, dtype=np.int)

    def place(self, left, top):
        self.rect = Rect(left, top, self.rect.width, self.rect.height)
        t = self.rect.width * 8 // 25
        self.bottom_rect = Rect(left + t, self.rect.bottom, self.rect.width - 2 * t, 5)

    def update(self, dx, dy):
        super(Player, self).update(dx, dy)
        self.bottom_rect.move_ip(dx, dy)


class Player(BaseSprite):
    def __init__(self, coords, image):
        super().__init__(coords, image)
        self.image = image

        self.is_moving = False
        self.is_stumbling = False
        self.on_ground = False
        self.is_stopping = False
        self.stopped = True

        self.bf = 1
        self.direction = 1

        self.to_pygame = self.from_pygame = self.mass = self.radius = self.points = self.moment = self.body = None
        self.shape = self.VELOCITY = None

    def init_body(self, to_pygame_callback, from_pygame_callback, mass, velocity):
        
        self.to_pygame = to_pygame_callback
        self.from_pygame = from_pygame_callback
        
        self.mass = mass  # 1.3
        self.radius = self.rect.width / 2
        self.points = ((-self.radius, -self.radius),
                       (self.radius, -self.radius),
                       (self.radius, self.radius),
                       (-self.radius, self.radius))
        self.moment = pymunk.moment_for_poly(self.mass, self.points)
        self.body = pymunk.Body(mass=self.mass, moment=self.moment)
        self.body.position = self.from_pygame(self.coords)
        
        self.shape = pymunk.Poly(self.body, self.points)
        self.shape.friction = 0
        self.VELOCITY = velocity  # 40000

    def add_to_space(self, space):
        space.add(self.body, self.shape)
        return self.shape
    
    def update(self):
        self.coords = self.to_pygame(self.body.position)
        if abs(self.body.angle) > D45:
            if self.body.angle < 0:
                self.body.angle += D45 * 2
            else:
                self.body.angle -= D45 * 2
                 
        self.rect.x, self.rect.y = self.coords - Vec2d(
            self.rect.width / 2, self.rect.height - self.radius)

