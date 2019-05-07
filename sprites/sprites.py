# -*- coding:UTF-8 -*-

import numpy as np
from numpy import cos, sin
from pygame import Rect
from pygame.sprite import Sprite


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


class Player(BaseSprite):
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
