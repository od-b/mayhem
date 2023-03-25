from typing import Callable     # type hint for function pointers
from random import randint

import pygame as pg
from pygame import Color, Rect, Surface, draw
from pygame.math import Vector2 as Vec2
from pygame.sprite import Sprite
from math import sqrt


class Block(Sprite):
    ''' Static object with none or a constant, set velocity/mass.

        Parameters
        ---
        config: dict with expected keys
            see ['special_sprites']['UNIQUE_CONTROLLABLES'][...]
        size: tuple[int, int]
        position: Vec2
            spawn position
        angle: float
        trigger_func: None | Callable
            optional function pointer to be called on update
            see trigger_func_param for an optional parameter
    '''

    def __init__(self,
                 config: dict,
                 alt_color_pool: list[Color] | None,
                 size: tuple[int, int],
                 position: Vec2,
                 trigger_func: None | Callable
                 ):

        Sprite.__init__(self)
        
        # store main attributes
        self.MASS = float(config['mass'])
        self.texture: Surface | None = config['texture']
        self.position = position
        self.SIZE = size
        self.TRIGGER_FUNC = trigger_func
        ''' (optional) function to be called on update. 
            * The function return value is never read
            * Pass attributes to be modified as parameters instead.
        '''
        
        # determine if a trigger func is passed
        if (self.TRIGGER_FUNC != None):
            self.TRIGGER_FUNC_param: any = None
            ''' parameter to be passed for the trigger_func.
                does nothing if trigger_func is not defined.
                * defaults to None
                * set manually through set_trigger_parameter
            '''
        
        # create surface, either as an image or color
        if (self.texture == None):
            # no texture provided, create a simple colored surface
            if (alt_color_pool):
                # if a special pallette is passed, use it
                self.color_pool = alt_color_pool
            else:
                # otherwise default to the config pallette
                self.color_pool: list[Color] = config['color_pool']

            # pick a random color from the color pool
            self.color = Color(self.color_pool[randint(0, len(self.color_pool)-1)])

            # create surface and fill using color
            IMG = pg.Surface(self.SIZE).convert()
            IMG.fill(self.color)
            # IMG.set_alpha(None, pg.RLEACCEL)
            ''' > The optional flags argument can be set to pygame.RLEACCEL to 
                > provide better performance on non accelerated displays. 
                > An RLEACCEL Surface will be slower to modify, but quicker to blit as a source.
                https://www.pygame.org/docs/ref/surface.html#pygame.Surface.set_alpha
            '''
            self.image = IMG
        else:
            raise ValueError('not yet implemented. Set texture to none')

        # create rect from the surface
        self.rect = self.image.get_rect()
        self.rect.topleft = self.position
        
        # create a mask for fast collision detection
        self.mask = pg.mask.from_surface(self.image)
    
    def set_trigger_parameter(self, param):
        self.TRIGGER_FUNC_param = param

    def update(self):
        if (self.TRIGGER_FUNC != None):
            self.TRIGGER_FUNC(self.TRIGGER_FUNC_param)


class Controllable(Sprite):
    ''''''
    def __init__(self,
                 config: dict,
                 global_physics: dict,
                 initial_pos: Vec2,
                 trigger_func):

        # initalize as pygame sprite
        Sprite.__init__(self)
        
        # constant global physics
        self.G_CONST = float(global_physics['gravity'])
        self.G_DIRECT = float(global_physics['gravity_direct'])

        # constant attributes:
        self.TRIGGER_FUNC: Callable | None = trigger_func
        ''' function to be called on update. 
            * Should not return a value
            * Pass attributes to be modified as parameters instead.
        '''
        self.MAX_HEALTH: int = int(config['weights']['max_health'])
        self.MAX_MANA: int = int(config['weights']['max_mana'])
        self.SIZE: tuple[int, int] = (
            int(config['surface']['width']),
            int(config['surface']['height'])
        )
        # adjust max positive y-velocity, taking mass into account
        self.MASS: float = float(config['weights']['mass'])
        self.IMG_SRC: Surface | None = config['surface']['image']
        self.MAX_VELOCITY: Vec2 = Vec2(
            float(config['weights']['max_velocity']),
            float(
                config['weights']['max_velocity']\
                + (self.MASS * config['weights']['max_velocity'])
            )
        )

        # rate of change of velocity
        self.HANDLING: float = float(config['weights']['handling'])
        self.HALT_HANDLING = self.HANDLING * self.HANDLING
        print(self.HALT_HANDLING)

        # set up variable attributes
        self.position: Vec2 = initial_pos
        self.velocity: Vec2 = Vec2(0.0, 0.0)
        self.angle: float = 0.0
        self.health: int = self.MAX_HEALTH
        self.mana: int = self.MAX_MANA

        # attributes for adjusting movement through keys
        self.dir_x: float = float(0)
        self.dir_y: float = float(0)
        self.halt: int = int(0)
        self.direction = Vec2(0.0, 0.0)
        ''' normalized directional movement vector '''

        if self.TRIGGER_FUNC:
            self.TRIGGER_FUNC_param: any = None
            ''' parameter to be passed for the trigger_func.
                does nothing if trigger_func is not defined.
                * defaults to None
            '''

        # set up surface, aka image
        if not self.IMG_SRC:
            self.color = Color(config['surface']['color'])
            # it's crucial to store the original image and rect for transformation
            # otherwise, pygame will flood the memory in a matter of seconds
            # in short, ensures the original image is rotated, not the mutated one
            IMG = pg.Surface(self.SIZE).convert_alpha()
            # IMG = pg.transform.flip(IMG, False, True)
            self.ORIGINAL_IMAGE = IMG
            self.ORIGINAL_RECT = self.ORIGINAL_IMAGE.get_rect()

            # create a polygon using the rect bounds as reference points
            p1 = Vec2(self.ORIGINAL_RECT.midtop)
            p2 = Vec2(self.ORIGINAL_RECT.bottomright)
            p3 = Vec2(self.ORIGINAL_RECT.bottomleft)

            # draw the polygon to the original image surface
            pg.draw.polygon(self.ORIGINAL_IMAGE, self.color, (p1, p2, p3))

            # set sprite staple attributes through update_image_angle(); image, rect & mask
            self.update_image_angle()
        else:
            # TODO: support actual images
            self.color = None
            raise ValueError("not yet implemented, don't include an image")

    def get_angle(self):
        # return "negative" as actual surface is flipped
        return round(self.angle)

    def get_gravity_factor(self):
        ''' return a positive float based on velocity, mass and global gravity constant '''
        return self.G_CONST * (abs(self.velocity.y) + self.G_CONST)

    def limit_velocity(self):
        ''' check velocity, if needed clamps the velocity between min/max '''
        if (abs(self.velocity.x) > self.MAX_VELOCITY.x):
            if self.velocity.x > 0:
                self.velocity.x = self.MAX_VELOCITY.x
            else:
                self.velocity.x = -self.MAX_VELOCITY.x

        if (self.velocity.y < 0) and (abs(self.velocity.y) > self.MAX_VELOCITY.y):
            self.velocity.y = -self.MAX_VELOCITY.y
        elif self.velocity.y > self.MAX_VELOCITY.y:
            self.velocity.y = self.MAX_VELOCITY.y

    def update_image_angle(self):
        ''' Rotate image to the correct angle. Create new rect and mask. '''

        # get a new image by rotating the original image
        # not referring to the original image will result in catastrophic memory flooding
        # the constant of -45 is to correct for the fact that image is a triangle
        NEW_IMG = pg.transform.rotate(self.ORIGINAL_IMAGE, self.angle)
        # flip y-axis of image
        self.image = pg.transform.flip(NEW_IMG, False, True)

        # get new mask for collision checking
        # > Note A new mask needs to be recreated each time a sprite's image is changed  
        # > (e.g. if a new image is used or the existing image is rotated).  
        #   https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.collide_mask  
        self.mask = pg.mask.from_surface(self.image)

        # set rect to the new images rect bounds
        # get_rect(**kwargs: Any) accepts a position value as parameter
        # RE = self.image.get_rect(center=self.ORIGINAL_RECT.center)
        self.rect = self.mask.get_rect(center=self.ORIGINAL_RECT.center)

    def update(self):
        self.direction.update(self.dir_x, self.dir_y)

        if (self.halt == 1):
            self.velocity -= (self.velocity * self.G_CONST)
            self.velocity += self.direction * (self.HALT_HANDLING)
        else:
            if (abs(self.direction.y) != 1.0):
                self.velocity.y += self.G_DIRECT
                self.velocity.y += self.get_gravity_factor()
            self.velocity += (self.direction * self.HANDLING)

        # increment velocity by a fraction of direction
        self.limit_velocity()
        # reduce velocity by 1% per frame, after limiting
        self.velocity *= 0.99

        # update image, position and rect position
        self.position += self.velocity

        # calculate angle from the normalized position / velocity
        # THE MAGIC NUMBER IS -35 DO NOT ASK BECAUSE I DO NOT
        # probably because the model being rotated is actually a rectangle.
        # self.velocity = self.velocity.rotate(0.02)
        # if (self.direction.y == -1.0) and (abs(self.direction.x) == 0.0) and self.angle in range(-160,160):
        #     self.angle = 180
        # else:
        self.angle = round(self.position.normalize().angle_to(self.velocity.normalize())) - 35.0

        self.update_image_angle()
        self.rect.center = self.position
