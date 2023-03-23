from typing import Callable     # type hint for function pointers
from random import randint

import pygame as pg
from pygame import Color, Rect, Surface, draw
from pygame.math import Vector2 as Vec2
from pygame.sprite import Sprite


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
        self.mass = float(config['mass'])
        self.texture: Surface | None = config['texture']
        self.position = position
        self.size = size
        self.trigger_func = trigger_func
        ''' (optional) function to be called on update. 
            * The function return value is never read
            * Pass attributes to be modified as parameters instead.
        '''
        
        # determine if a trigger func is passed
        if (self.trigger_func != None):
            self.trigger_func_param: any = None
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
            IMG = pg.Surface(self.size).convert()
            IMG.fill(self.color)
            self.image = IMG
        else:
            raise ValueError('not yet implemented. Set texture to none')

        # create rect from the surface
        self.rect = self.image.get_rect()
        self.rect.topleft = self.position
        
        # create a mask for fast collision detection
        self.mask = pg.mask.from_surface(self.image)
    
    def set_trigger_parameter(self, param):
        self.trigger_func_param = param

    def update(self):
        if (self.trigger_func != None):
            self.trigger_func(self.trigger_func_param)


class Controllable(Sprite):
    ''''''
    def __init__(self,
                 config: dict,
                 global_physics: dict,
                 initial_pos: Vec2,
                 initial_angle: float,
                 initial_velocity: Vec2,
                 trigger_func):

        # initalize as pygame sprite
        Sprite.__init__(self)
        
        # "constant" attributes:
        self.trigger_func: Callable | None = trigger_func
        ''' function to be called on update. 
            * Should not return a value
            * Pass attributes to be modified as parameters instead.
        '''
        self.max_health = int(config['weights']['max_health'])
        self.max_mana = int(config['weights']['max_mana'])
        self.size = (
            int(config['surface']['width']),
            int(config['surface']['height'])
        )
        self.max_velocity = Vec2(
            float(config['weights']['max_velocity_x']),
            float(config['weights']['max_velocity_y'])
        )
        self.mass = float(1 - config['weights']['mass'])
        self.image_source: Surface | None = config['surface']['image']
        self.G_CONST = float(global_physics['gravity'])
        self.G_MULTI = float(global_physics['gravity'])

        # set up variable attributes
        self.position = initial_pos
        self.velocity = initial_velocity
        self.angle = initial_angle
        self.health = self.max_health
        self.mana = self.max_mana
        
        # adjust max positive y-velocity, taking mass into account
        # print(f'max_velocity.y: {self.max_velocity.y}')
        self.max_velocity.y += (self.mass / (1 + self.mass - (self.mass * self.G_CONST)))
        # print(f'max_velocity.y: {self.max_velocity.y}')

        # # rate of change of velocity
        # self.acceleration: Vec2 = Vec2(float(0), float(0))
        # self.steering_force: float = float(config['weights']['steering_force'])
        # # attributes for external queuing of velocity and angle. Read on update.
        # self.pending_q_rotate: bool = False
        # self.pending_q_rotate: bool = False
        # ''' rotation to be applied on update '''
        # self.q_rotate = float(0)
        # ''' rotation to be applied on update '''
        # self.q_thrust = float(0)

        if self.trigger_func:
            self.trigger_func_param: any = None
            ''' parameter to be passed for the trigger_func.
                does nothing if trigger_func is not defined.
                * defaults to None
            '''

        # set up surface, aka image
        if not self.image_source:
            self.color = Color(config['surface']['color'])
            # it's crucial to store the original image and rect for transformation
            # otherwise, pygame will flood the memory in a matter of seconds
            # in short, ensures the original image is rotated, not the mutated one
            self.ORIGINAL_IMAGE = pg.Surface(self.size).convert_alpha()
            self.ORIGINAL_RECT = self.ORIGINAL_IMAGE.get_rect()

            # create a polygon using the rect bounds as reference points
            p1 = Vec2(self.ORIGINAL_RECT.midtop)
            p2 = Vec2(self.ORIGINAL_RECT.bottomright)
            p3 = Vec2(self.ORIGINAL_RECT.bottomleft)
            # draw the polygon to the original image surface
            pg.draw.polygon(self.ORIGINAL_IMAGE, self.color, (p1, p2, p3))
        else:
            # TODO: support actual images
            self.color = None
            raise ValueError("not yet implemented, don't include an image")
    
        # set sprite staple attributes: image, rect & mask
        self.image = pg.transform.rotate(self.ORIGINAL_IMAGE, self.angle)
        self.rect = self.ORIGINAL_IMAGE.get_rect(center=self.position).copy()

        # a mask is a bitmap of set pixels in an image, used for fast collision checking
        # https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.collide_mask
        self.mask = pg.mask.from_surface(self.ORIGINAL_IMAGE)

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

    def rotate_clockwise(self, weight: float):
        ''' rotate <weight> degrees counter-clockwise '''
        self.angle -= weight
        # handle overflow:
        if ((self.angle - weight) < -180):
            self.angle *= -1
        self.update_image_angle()

    def rotate_c_clockwise(self, weight: float):
        ''' rotate <weight> degrees counter-clockwise '''
        self.angle += weight
        # handle overflow:
        if ((self.angle + weight) > 180):
            self.angle *= -1
        self.update_image_angle()

    def update_image_angle(self):
        ''' Rotate image to the correct angle. Create new rect and mask. '''

        # get a new image by rotating the original image
        # not referring to the original image will result in catastrophic memory flooding
        self.image = pg.transform.rotate(self.ORIGINAL_IMAGE, self.angle)

        # set rect to the new images rect bounds
        # get_rect(**kwargs: Any) accepts a position value as parameter
        self.rect = self.image.get_rect(center=self.ORIGINAL_RECT.center)

        # get new mask for collision checking
        # > Note A new mask needs to be recreated each time a sprite's image is changed  
        # > (e.g. if a new image is used or the existing image is rotated).  
        #   https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.collide_mask  
        self.mask = pg.mask.from_surface(self.image)

    def update(self):
        self.velocity.y += self.get_gravity_factor()
        # self.velocity = self.velocity.rotate(self.angle)
        # self.rotate_c_clockwise(1.0)
        # self.update_image_angle()
        self.limit_velocity()
        self.position += self.velocity
        self.rect.center = self.position
