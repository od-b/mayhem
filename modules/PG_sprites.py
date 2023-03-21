from typing import Callable     # type hint for function pointers
import pygame as pg
import pygame.math
from pygame import gfxdraw
from pygame.math import Vector2 as Vec2
from math import sqrt, pow

from .exceptions import LogicError


class Static_Interactive(pg.sprite.Sprite):
    ''' ### Static object with none or predetermined velocity/mass.
        * Supports a custom or generic trigger.
        * Position        = Vec2(x, y)
        * Size            = Vec2(w, h)
        ---
        #### Optional parameters
        * mass            = None | float ∈ [-1.0, 1.0]         : level of applied gravity
        * velocity        = None | Vec2                        : change in position per frame
        * max_velocity    = None | Vec2                        : change in position per frame
        * trigger_func    = None | Callable                    : optional function to call on a trigger, ex. collision
        * trigger_weight  = None | Vec2, x,y ∈ [-1.0, 1.0]     : parameter for the trigger
        ---
        #### Notes: 
        * Float values should be set to None as opposed to 0.0 for performance
        * if velocity == None, position may never be updated.
        * x, y, w and h is stored in .rect
        * may have a trigger_func without trigger_weight, but not vice-versa
    '''
    def __init__(self,
                 window: pg.Surface,
                 color: tuple,
                 position: Vec2,
                 size: tuple,
                 image: pg.Surface | None,
                 mass: None | float,
                 velocity: None | Vec2,
                 max_velocity: None | Vec2,
                 trigger_func: None | Callable,
                 trigger_weight: None | float):

        # verify parameters
        if (trigger_weight != None) and (trigger_func == None):
            raise LogicError("trigger_weight should be None without a trigger_func")
        if (max_velocity != None) and (velocity == None):
            raise LogicError("max_velocity should be None without a velocity vector")
        if (velocity != None) and (mass == None):
            raise LogicError("objects with mass cannot have None velocity. Init with empty Vec2() instead")

        # initalize as pygame sprite
        pg.sprite.Sprite.__init__(self)
        
        # store attributes
        self.window = window
        self.color = pg.Color(color)
        self.position = position
        self.size = size
        self.mass = mass
        self.velocity = velocity
        self.max_velocity = max_velocity
        self.trigger_func = trigger_func
        self.trigger_weight = trigger_weight

        # create surface, either as an image or color
        if not image:
            IMG = pg.Surface(self.size).convert()
            IMG.fill(self.color)
            self.image = IMG
        else:
            self.image = image
            # self.image.set_colorkey()
            # print(self.image.get_colorkey())
            self.image = self.image.convert_alpha()

        self.rect = self.image.get_rect()
        self.rect.topleft = self.position
        
        # create a mask for fast collision detection
        self.mask = pg.mask.from_surface(self.image)

    def update_image(self):
        self.image = pg.Surface(self.size)
    
    def fill_image(self, alt_color: tuple | None):
        ''' uses sprite self.color if alt color is set to None '''
        if alt_color:
            self.image.fill(alt_color)
        else:
            self.image.fill(self.color)

    def update(self):
        pass


class Controllable(pg.sprite.Sprite):
    ''' ### Controllable object
        * Supports a custom or generic trigger.
        * position        = Vec2(x, y)
        * size            = Vec2(w, h)
        * velocity        = Vec2                               : initial velocity
        * angle           = float                              : initial angle in radians
        * mass            = None | float ∈ [0.0, 1.0]          : level of applied gravity
        ---
        #### Optional parameters
        * max_velocity    = None | Vec2                        : change in position per frame
        * trigger_func    = None | Callable                    : optional function to call on a trigger, ex. collision
        * trigger_weight  = None | Vec2, x,y ∈ [-1.0, 1.0]     : parameter for the trigger
        ---
        #### Notes: 
        * x, y, w and h is stored in .rect
        * may have a trigger_func without trigger_weight, but not vice-versa
    '''
    def __init__(self,
                 window: pg.Surface,
                 physics: dict, 
                 color: tuple, 
                 position: Vec2, 
                 size: tuple,
                 image: pg.Surface | None,
                 mass: float,
                 velocity: Vec2,
                 max_velocity: None | Vec2,
                 trigger_func: None | Callable,
                 trigger_weight: None | float,
                 angle: float,
                 max_health: int,
                 max_mana: int,
                 health: int,
                 mana: int):

        # verify parameters
        if (trigger_weight != None) and (trigger_func == None):
            raise LogicError("trigger_weight should be None without a trigger_func")
        if (image != None) and (color != None):
            raise LogicError("sprites should have a color OR an image")

        # initalize as pygame sprite
        pg.sprite.Sprite.__init__(self)
        
        # store attributes
        self.window = window
        self.color = color

        self.trigger_func = trigger_func
        self.trigger_weight = trigger_weight

        self.max_health = max_health
        self.max_mana = max_mana
        self.health = health
        self.mana = mana

        self.physics = physics
        self.position = position
        self.size = size
        self.mass = float(1 - mass)
        self.velocity = velocity
        self.max_velocity = max_velocity
        self.angle = angle

        self.G_CONST = float(self.physics['gravity'])
        self.G_MULTI = float(self.physics['gravity'])

        # max positive y-velocity, taking mass into account
        print(f'max_velocity.y: {self.max_velocity.y}')
        
        self.max_velocity.y += (self.mass / (1 + self.mass - (self.mass * self.G_CONST)))

        print(f'max_velocity.y: {self.max_velocity.y}')
        self.image = self._set_up_image_surface(image)

        # get the surface
        self.rect: pg.Rect
        self.rect.topleft = self.position

    def _set_up_image_surface(self, image: pg.Surface | None):
        ''' create image surface, or store the passed surface as image
            * if an image is not provided, draws an illustration as the surface
        '''

        # if an image is not provided, draw an illustration
        if not image:
            IMG = pg.Surface(self.size)
            self.rect = IMG.get_rect()
            p1 = Vec2(self.rect.midtop)
            p2 = Vec2(self.rect.bottomright)
            p3 = Vec2(self.rect.bottomleft)

            pg.draw.polygon(
                IMG,
                self.color,
                (p1, p2, p3)
            )
            # IMG = pg.transform.flip(IMG, True, False)
            self.angle = Vec2(self.rect.center).angle_to(p1)
            IMG = pg.transform.rotate(IMG, -self.angle)
            self.rect = IMG.get_rect()
            self.rect.center = self.position
        else:
            # TODO: choose an image instead
            IMG = pg.Surface(self.size)
            pass

        return IMG.convert_alpha()

    def update_image(self):
        self.image = pg.Surface(self.size)
    
    def fill_image(self, alt_color: tuple | None):
        ''' uses sprite self.color if alt color is set to None '''
        if alt_color:
            self.image.fill(alt_color)
        else:
            self.image.fill(self.color)

    def get_gravity_factor(self):
        ''' return a positive float based on velocity, mass and global gravity constant '''
        vel_y = (abs(self.velocity.y) + self.G_CONST)
        return self.G_MULTI * (vel_y / self.mass)

    def limit_velocity(self):
        ''' check velocity, if needed clamps the velocity between min/max '''
        if (abs(self.velocity.x) > self.max_velocity.x):
            if self.velocity.x > 0:
                self.velocity.x = self.max_velocity.x
            else:
                self.velocity.x = -self.max_velocity.x
        
        if (self.velocity.y < 0) and (abs(self.velocity.y) > self.max_velocity.y):
            self.velocity.y = -self.max_velocity.y
        elif self.velocity.y > self.max_velocity.y:
            self.velocity.y = self.max_velocity.y

    def key_event(self, key):
        keys = pg.key.get_pressed()
        if keys[pg.K_a]:
            pass
        elif keys[pg.K_d]:
            pass
        if keys[pg.K_SPACE]:
            pass

    def get_angle(self):
        return round(self.angle, 2)
    
    def rotate_image(self):
        new_img = pg.transform.rotate(self.image, self.angle)
        self.image = new_img
        new_img_rect = self.image.get_rect()
        new_img_rect.center = self.position
        self.rect = new_img_rect

    def update(self):
        self.velocity.y += self.get_gravity_factor()
        # self.velocity = self.velocity.rotate(self.angle)
        self.limit_velocity()
        self.position += self.velocity.elementwise()
        self.rect.center = self.position
