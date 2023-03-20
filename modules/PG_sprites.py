from typing import Callable     # type hint for function pointers
import pygame as pg
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
                 window: pg.Surface, color: tuple, position: Vec2, size: tuple, image: pg.Surface | None,
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

        # create surface and get its rect
        if not image:
            self.image = pg.Surface(self.size)
        else:
            self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = self.position
        self.image.fill(self.color)

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

        # initalize as pygame sprite
        pg.sprite.Sprite.__init__(self)
        
        # store attributes
        self.window = window
        self.physics = physics
        self.color = pg.Color(color)
        self.position = position
        self.size = size
        self.mass = mass
        self.velocity: Vec2 = velocity
        self.max_velocity = max_velocity
        self.trigger_func = trigger_func
        self.trigger_weight = trigger_weight
        self.angle = angle
        self.max_health = max_health
        self.max_mana = max_mana
        self.health = health
        self.mana = mana

        # max positive y-velocity, taking mass into account
        self.terminal_velocity = (self.max_velocity.y + self.mass + self.physics['gravity'])
        print(self.max_velocity.y)
        print(self.terminal_velocity)

        # create surface and get its rect
        if not image:
            self.image = pg.Surface(self.size)
        else:
            self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = self.position
        self.image.fill(self.color)

    def update_image(self):
        self.image = pg.Surface(self.size)
    
    def fill_image(self, alt_color: tuple | None):
        ''' uses sprite self.color if alt color is set to None '''
        if alt_color:
            self.image.fill(alt_color)
        else:
            self.image.fill(self.color)

    def gravity(self):
        speed = sqrt(pow(self.velocity.x,2) + pow(self.velocity.y,2))
        downforce = speed * self.mass
        return float((downforce / (speed + self.physics['gravity'])) + self.physics['gravity'])

    def limit_velocity(self):
        if (abs(self.velocity.x) > self.max_velocity.x):
            if self.velocity.x > 0:
                self.velocity.x = self.max_velocity.x
            else:
                self.velocity.x = -self.max_velocity.x
        
        if (self.velocity.y < 0) and (abs(self.velocity.y) > self.max_velocity.y):
            self.velocity.y = -self.max_velocity.y
        elif self.velocity.y > self.terminal_velocity:
            self.velocity.y = self.terminal_velocity

    def update(self):
        self.velocity.y += self.gravity()
        self.limit_velocity()
        self.position += self.velocity
        self.rect.topleft = (int(self.position.x), int(self.position.y))
