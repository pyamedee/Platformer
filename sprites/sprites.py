# -*- coding:UTF-8 -*-

import numpy as np
from numpy import cos, sin
from pyglet.sprite import Sprite
import pymunk
from math import pi
from pymunk.vec2d import Vec2d

D45 = pi / 4


class Structure(Sprite):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    body.position = 0, 0

    def __init__(self, id_, image, *args, **kwargs):
        super().__init__(image, *args, **kwargs)

        self.id = id_

        self.radius = self.image.width
        self.base_coords = self.x, self.y

        self.a = self.b = None
        self.shapes = set()

    def add_poly(self, points, thickness, iswall=False):
        shape = pymunk.Poly(type(self).body, points + self.position, radius=thickness)
        shape.friction = 1
        shape.iswall = iswall
        shape.is_structure = True
        self.shapes.add(shape)

    def add_segment(self, a, b, thickness, iswall=False):
        shape = pymunk.Segment(type(self).body, a + self.position, b + self.position, thickness)
        shape.friction = 1
        shape.iswall = iswall
        shape.is_structure = True
        self.shapes.add(shape)

    def add_to_space(self, space):
        self.shapes = frozenset(self.shapes)
        space.add(self.body, self.shapes)
        return self.shapes

    def update(self, a):
        self.x, self.y = self.base_coords + a
        # - Vec2d(
        # self.rect.width / 2, self.rect.height - self.radius)


# class Player0(BaseSprite):
#     def __init__(self, coords, image):
#         super(Player, self).__init__(coords, image)
#         self.isfalling = False
#         self.bottom_rect = None
#         self.place(self.rect.left, self.rect.top)
#         self.vector = np.zeros(2, dtype=np.int)
#
#     def place(self, left, top):
#         self.rect = Rect(left, top, self.rect.width, self.rect.height)
#         t = self.rect.width * 8 // 25
#         self.bottom_rect = Rect(left + t, self.rect.bottom, self.rect.width - 2 * t, 5)
#
#     def update(self, dx, dy):
#         super(Player, self).update(dx, dy)
#         self.bottom_rect.move_ip(dx, dy)


class Player(Sprite):
    def __init__(self, image, *args, **kwargs):
        super().__init__(image, *args, **kwargs)

        self.is_moving = False
        self.is_stumbling = False
        self.on_ground = False
        self.is_stopping = False
        self.stopped = True
        self.is_jumping = False

        self.bf = 1
        self.direction = 1

        self.mass = self.radius = self.points = self.moment = self.body = None
        self.shape = self.VELOCITY = None

    def init_body(self, mass, velocity):
        
        self.mass = mass  # 1.3
        self.radius = self.image.width / 3
        self.points = ((-self.radius, -self.radius),
                       (self.radius, -self.radius),
                       (self.radius, self.radius),
                       (-self.radius, self.radius))

        self.moment = pymunk.moment_for_poly(self.mass, self.points)
        self.body = pymunk.Body(mass=self.mass, moment=self.moment)
        self.body.position = self.x, self.y
        
        self.shape = pymunk.Poly(self.body, self.points)
        self.shape.friction = 0.2
        self.VELOCITY = velocity  # 40000

    def add_to_space(self, space):
        space.add(self.body, self.shape)
        return self.shape
    
    def update(self, x=None, y=None, a=(0, 0)):
        coords = self.body.position
        if x is not None:
            coords[0] = x
        if y is not None:
            coords[1] = y
        if x is y is None:
            coords += a
        if abs(self.body.angle) > D45:
            if self.body.angle < 0:
                self.body.angle += D45 * 2
            else:
                self.body.angle -= D45 * 2
                 
        self.x, self.y = coords - (self.image.width / 2, self.radius)

