# -*- coding:UTF-8 -*-

from pygame.sprite import Sprite
from numpy import sin, cos


class Structure(Sprite):
    
    def __init__(self, coords, image):
        super(Structure, self).__init__()

        self.image = image
        self.rect = image.get_rect()
        self.rect.move_ip(*coords)

    def update(self, dx, dy):
        self.rect.move_ip(dx, dy)


