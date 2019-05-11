# -*- coding:Utf-8 -*-

import sys, time, math
import pymunk
import pymunk.pygame_util
import pygame
from pygame.locals import *
from pygame.color import THECOLORS
from pymunk.vec2d import Vec2d

pygame.init()

D45 = math.pi / 4

def to_pygame(v):
    raise NotImplementedError
from_pygame = to_pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, coords):
        super().__init__()
        self.image = pygame.surface.Surface((50, 80))
        self.image.fill(THECOLORS['black'])
        
        self.rect = self.image.get_rect().move(coords)
        
        self.mass = 1.3
        self.radius = self.rect.width / 2
        self.points = ((-self.radius, -self.radius), (self.radius, -self.radius), (self.radius, self.radius), (-self.radius, self.radius))
        self.moment = pymunk.moment_for_poly(self.mass, self.points)
        self.body = pymunk.Body(mass=self.mass, moment=self.moment)
        self.body.position = from_pygame(coords)
        
        self.shape = pymunk.Poly(self.body, self.points)
        self.shape.friction = 0
        self.VELOCITY = 40000
        self.STRUGGLING_LIMIT = 200
        self.STRUGGLING_RECUPERATION_TIME = 30
        
    def add_to_space(self, space):
        space.add(self.body, self.shape)
        return self.shape
    
    def update(self):
        if abs(self.body.angle) > D45:
            if self.body.angle < 0:
                self.body.angle += D45 * 2
            else:
                self.body.angle -= D45 * 2
                 
        self.rect.x, self.rect.y = to_pygame(self.body.position) - Vec2d(self.rect.width / 2, self.rect.height - self.radius)


class Lines(pygame.sprite.Sprite):
    def __init__(self, body_coords, *lines):
        super().__init__()
        
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = body_coords
        
        self.lines = list()
        for line in lines:
            shape = pymunk.Segment(self.body, line['a'], line['b'], line['thickness'])
            if line.get('iswall', False):
                shape.iswall = True
            self.lines.append(shape)
            
    def add_to_space(self, space):
        space.add(self.body, self.lines)
        return self.lines
    
    def update(self, surface):
        for line in self.lines:
            a = to_pygame(line.a + self.body.position)
            b = to_pygame(line.b + self.body.position)
            pygame.draw.line(surface, THECOLORS['gray'], a, b, int(line.radius))

class Line(pygame.sprite.Sprite):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    body.position = 0, 0
    
    def __init__(self, a, b, thickness, iswall=False):
        super().__init__()
        
        self.shape = pymunk.Segment(type(self).body, a, b, thickness)
        self.shape.friction = 1
        if iswall:
            self.shape.iswall = True
        self.a = to_pygame(a)
        self.b = to_pygame(b)
    
    def clear(self, surface):
        pygame.draw.line(surface, THECOLORS['white'], self.a, self.b, int(self.shape.radius))
        
    def draw(self, surface):
        pygame.draw.line(surface, THECOLORS['gray'], self.a, self.b, int(self.shape.radius))
        
    def update(self, surface):
        self.clear(surface)
        self.a = to_pygame(self.shape.a)
        self.b = to_pygame(self.shape.b)
        self.draw(surface)
    
class App:
    
    
    def __init__(self, framerate=60, resolution=(800, 600), flags=0, spups=5):
        
        global to_pygame, from_pygame
        to_pygame = self.to_pygame
        from_pygame = self.from_pygame
        
        self.a = 0
        
        self.spups = spups
        
        self.fps = framerate
        self.dt = 1. / self.fps / spups
        print(self.dt)
        self.clock = pygame.time.Clock()
        
        self.screen = pygame.display.set_mode(resolution, flags)
        self.screen_rect = self.screen.get_rect()
        self.bg = pygame.surface.Surface((self.screen_rect.width, self.screen_rect.height))
        self.bg.fill(THECOLORS['white'])
        self.screen.blit(self.bg, self.screen_rect)

        self.running = True
        self.physics_enabled = True
        
        self.space = pymunk.Space()
        self.space.gravity = (0., -1000.)

        self.player = Player((500, 43))
        self.player_group = pygame.sprite.GroupSingle()
        self.player_group.add(self.player)
        
        self.lines = pygame.sprite.Group()
        self.lines.add(Line((0, 50), (600, 350), 4))
        self.lines.add(Line((600, 350), (800, 350), 4))
        self.lines.add(Line((-100000, 0), (-100000, 600), 4, True))
        self.lines.add(Line((800, 100), (800, 600), 4, True))
        self.lines.add(Line((0, 50), (-100000, 0), 4))
        
        self.space.add(Line.body, tuple(line.shape for line in self.lines.sprites()))
        self.player.add_to_space(self.space)
    
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)
        self.debug_draw = False

    def to_pygame(self, p):
        c = list(pymunk.pygame_util.to_pygame(p, self.screen))
        c[0] += self.a
        return c
    
    def from_pygame(self, p):
        c = list(pymunk.pygame_util.to_pygame(p, self.screen))
        c[0] -= self.a
        return c
    
    def loop(self):
        direction = 0
        move = False
        dm = 1
        while_stopping = False
        i = 0
        stopped = False
        falling = True
        can_jump = False
        
        def jump(arbiter):
            nonlocal can_jump
            shapes = arbiter.shapes
            for shape in shapes:
                if isinstance(shape, pymunk.Segment) and hasattr(shape, 'iswall') and shape.iswall:
                    return
            can_jump = True
        
        while self.running:
            self.clock.tick(self.fps)
                        
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    return 0
                elif event.type == KEYDOWN:
                    
                    if event.key == K_RIGHT:
                        if not while_stopping:
                            direction = 1
                            move = True
                    elif event.key == K_LEFT:
                        if not while_stopping:
                            direction = -1
                            move = True
                    elif event.key == K_UP:
                        self.player.body.each_arbiter(jump)
                        if can_jump:
                            position = self.player.body.position
                            self.player.body.apply_impulse_at_world_point(Vec2d(0, 600), position)
                    elif event.key == K_o:
                        print(stopped)
                    elif event.key == K_p:
                        self.debug_draw ^= True
                        self.screen.fill(THECOLORS['white'])
                    elif event.key == K_n:
                        self.physics_enabled ^= True
                    elif event.key == K_c:
                        coords = self.player.body.position
                    elif event.key == K_SPACE:
                        self.player.body.angle = 0
                        self.player.body.position = coords
                    elif event.key == K_b:
                        t1 = time.perf_counter()
                    elif event.key == K_v:
                        print('time', time.perf_counter() - t1)
                    
                    
                elif event.type == KEYUP and event.key in (K_LEFT, K_RIGHT):
                    move = False
                    while_stopping = True
                
            
            can_jump = False
            v = self.player.body.velocity
            
            if move and (not while_stopping):
                self.player.shape.friction = 0.2
                stopped = False
                f = 0
                i = 1
                modif = bool(KMOD_LCTRL & pygame.key.get_mods()) + 1
                
                print(self.player.body.position, v)
                div = math.sqrt(v.dot(v)) / 4 + 1
                self.player.body.apply_force_at_local_point(Vec2d(self.player.VELOCITY / div * direction / modif * self.spups, 0), (0, 0))
                
            elif while_stopping:
                if i > 30:
                    falling = True
                if round(v.x) * direction <= 0:
                    stopped = True
                    while_stopping = False
                else:
                    i += 1
                    self.player.body.apply_force_at_local_point(Vec2d(-self.player.VELOCITY * self.spups / 15 * direction, 0), (0, 0))
                dm =  1
            if falling:
                print('falling')
            if falling and round(v.x) == 0:
                falling = False
                
            if stopped:
                self.player.body.velocity -= Vec2d(v.x, 0)
            
            if self.physics_enabled:
                for _ in range(self.spups):
                    self.space.step(self.dt)
            
            if self.debug_draw:
                self.screen.fill(THECOLORS['white'])
                self.space.debug_draw(self.draw_options)
            
            self.a = -self.player.body.position.x + self.screen_rect.width / 2
            
            self.player_group.update()
            self.player_group.clear(self.screen, self.bg)
            self.player_group.draw(self.screen)

            self.lines.update(self.screen)
            pygame.display.set_caption(str(self.clock.get_fps()))
            pygame.display.flip()
            
            
if __name__ == '__main__':
    app = App(resolution=(800, 600), framerate=60, flags=0, spups=8)
    sys.exit(app.loop())
