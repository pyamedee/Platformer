# -*- coding:UTF-8 -*-

import numpy as np
from numpy import cos, sin
from pygame import Rect
from pygame.sprite import Sprite
import pymunk
from math import pi

D45 = pi / 4


class BaseSprite(Sprite):

    def __init__(self, coords, image):
        super().__init__()
        self.image = image
        self.rect = image.get_rect()
        self.rect.move_ip(tuple(coords))

    def update(self, dx, dy):
        self.rect.move_ip(dx, dy)


class Structure(BaseSprite):
    pass


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


class Player(pygame.sprite.Sprite):
    def __init__(self, coords, image):
        super().__init__()
        self.image = image
        
        self.rect = self.image.get_rect().move(coords)

        self.to_pygame = self.from_pygame = self.mass = self.radius = self.points = self.moment = self.body = None
        self.shape = self.VELOCITY = None

    def init_body(self, to_pygame_callback, mass, velocity):
        
        self.to_pygame = to_pygame_callback
        
        self.mass = mass  # 1.3
        self.radius = self.rect.width / 2
        self.points = ((-self.radius, -self.radius),
                       (self.radius, -self.radius),
                       (self.radius, self.radius),
                       (-self.radius, self.radius))
        self.moment = pymunk.moment_for_poly(self.mass, self.points)
        self.body = pymunk.Body(mass=self.mass, moment=self.moment)
        self.body.position = self.from_pygame(coords)
        
        self.shape = pymunk.Poly(self.body, self.points)
        self.shape.friction = 0
        self.VELOCITY = velocity  # 40000

    def add_to_space(self, space):
        space.add(self.body, self.shape)
        return self.shape
    
    def update(self):
        if abs(self.body.angle) > D45:
            if self.body.angle < 0:
                self.body.angle += D45 * 2
            else:
                self.body.angle -= D45 * 2
                 
        self.rect.x, self.rect.y = self.to_pygame(self.body.position) - Vec2d(
            self.rect.width / 2, self.rect.height - self.radius)

