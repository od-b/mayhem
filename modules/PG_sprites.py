from typing import Callable     # type hint for function pointers
import pygame as pg
from pygame.math import Vector2 as Vec2

from modules.exceptions import LogicError

class Static_Interactive(pg.sprite.Sprite):
    ''' ### Static object with none or constant velocity/mass.
        * Supports a custom or generic trigger.
        * Position        = Vec2(x, y)
        * Size            = Vec2(w, h)
        ---
        #### Optional parameters
        * mass            = None | Vec2(x,y), x,y ∈ [-1.0, 1.0]   : level of applied gravity
        * velocity        = None | Vec2                           : change in position per frame
        * max_velocity    = None | Vec2                           : change in position per frame
        * trigger_func    = None | Callable                       : optional function to call on a trigger, ex. collision
        * trigger_weight  = None | Vec2(x,y), x,y ∈ [-1.0, 1.0]   : parameter for the trigger
        ---
        #### Notes: 
        * Float values should be set to None as opposed to 0.0 for performance
        * if velocity == None, position may never be updated.
        * x, y, w and h is stored in .rect
        * may have a trigger_func without trigger_weight, but not vice-versa
    '''
    def __init__(self,
                 window: pg.Surface, color: tuple, position: Vec2, size: Vec2,
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
        
        # set up self
        self.window = window
        self.color = pg.Color(color)
        self.position = position
        self.size = size
        self.velocity = velocity
        self.max_velocity = max_velocity
        self.mass = mass
        self.trigger_func = trigger_func
        self.trigger_weight = trigger_weight
        self.surface = pg.Surface(size)
        self.rect = self.image.get_rect()

    def create_rect(self):
        ''' create rect from self.surface '''
    
    def fill_surface(self):
        self.surface.fill(self.color)

    def update(self):
        pass
