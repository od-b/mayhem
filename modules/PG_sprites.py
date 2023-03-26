# from typing import Callable     # type hint for function pointers
from random import randint

import pygame as pg
from pygame import Color, Surface
from pygame.math import Vector2 as Vec2
from pygame.sprite import Sprite


class Block(Sprite):
    ''' Static object with none or a constant, set velocity/mass.

        Parameters
        ---
        config: dict with expected keys
            see ['special_sprites']['UNIQUE_CONTROLLABLES'][...]
        size: tuple[int, int]
        position: tuple[int, int]
        alt_pallette: list[Color] | None
            whether to use to pallette from cf_block or another list
    '''

    def __init__(self,
                 cf_block: dict,
                 alt_pallette: list[Color] | None,
                 size: tuple[int, int],
                 position: tuple[int, int]
                 ):

        Sprite.__init__(self)

        # store main attributes
        self.mass = float(cf_block['mass'])
        self.position = position
        self.size = size

        # create surface, either as an image or color
        if (cf_block['texture'] == None):
            # no texture provided, create a simple colored surface
            if (alt_pallette):
                # if a special pallette is passed, use it
                self.color_pool = alt_pallette
            else:
                # otherwise default to the config pallette
                self.color_pool: list[Color] = cf_block['color_pool']

            # pick a random color from the color pool
            self.color = Color(self.color_pool[randint(0, len(self.color_pool)-1)])

            # create surface and fill using color
            IMG = pg.Surface(self.size).convert()
            IMG.fill(self.color)
            # IMG.set_alpha(None, pg.RLEACCEL)
            ''' > The optional flags argument can be set to pygame.RLEACCEL to 
                > provide better performance on non accelerated displays. 
                > An RLEACCEL Surface will be slower to modify, but quicker to blit as a source.
                https://www.pygame.org/docs/ref/surface.html#pygame.Surface.set_alpha
            '''
            self.image = IMG
        else:
            # self.texture_src = cf_block['texture']
            # self.texture: ....
            raise ValueError('not yet implemented. Set texture to none')

        # create rect from the surface
        self.rect = self.image.get_rect()
        self.rect.topleft = self.position

        # create a mask for fast collision detection
        self.mask = pg.mask.from_surface(self.image)

    def update(self):
        pass


class Controllable(Sprite):
    def __init__(self, cf_player: dict, cf_map: dict, initial_pos: tuple[int, int]):
        # initalize as pygame sprite
        Sprite.__init__(self)

        self.initial_pos = initial_pos

        self.gravity = float(cf_map['gravity'])
        self.gravity_c = float(cf_map['gravity_c'])
        # nested dicts
        cf_surface: dict = cf_player['surface']
        cf_weights: dict = cf_player['weights']
        
        # store dict settings
        self.width = int(cf_surface['width'])
        self.height = int(cf_surface['height'])
        self.max_health = int(cf_weights['max_health'])
        self.max_mana = int(cf_weights['max_mana'])
        self.mass = float(cf_weights['mass'])
        self.color = Color(cf_surface['color'])
        self.max_velocity = float(cf_weights['max_velocity'])
        self.handling = float(cf_weights['handling'])
        self.velo_falloff = float(1.0 - cf_weights['velocity_falloff'])
        self.img_src: Surface | None = cf_player['surface']['image']

        # set up vectors
        self.position: Vec2 = initial_pos
        self.velocity: Vec2 = Vec2(0.0, 0.0)
        self.direction = Vec2(0.0, 0.0)

        # set up variables
        self.angle = float(0)
        self.health = self.max_health
        self.mana = self.max_mana
        self.halt = int(0)

        # set up surface, aka image
        if not self.img_src:
            IMG = pg.Surface((self.width, self.height)).convert_alpha()
            # fill the image with transparent pixels
            IMG.fill((0,0,0,0))
            IMG_RECT = IMG.get_rect()

            # create a polygon using the rect bounds as reference points
            p1 = Vec2(IMG_RECT.midtop)
            p2 = Vec2(IMG_RECT.bottomright)
            p3 = Vec2(IMG_RECT.bottomleft)

            # draw the polygon to the original image surface
            pg.draw.polygon(IMG, self.color, (p1, p2, p3))

            # store the original image for transformation
            # otherwise, pygame will flood the memory in a matter of seconds
            # put short; ensures the original image is rotated, not the rotated one
            self.ORIGINAL_IMAGE = IMG
            self.height = IMG_RECT.h
            self.width = IMG_RECT.w

            # set sprite staple attributes through update_image_angle(); image, rect & mask
            self.update_image_angle()
        else:
            # TODO: support actual images
            self.color = None
            raise ValueError("not yet implemented, don't include an image")

    def get_position(self):
        return self.position

    def get_angle(self):
        return round(self.angle)

    def calc_gravity_factor(self):
        ''' return a positive float based on velocity, mass and global gravity constant '''
        return ((self.gravity * (abs(self.velocity.y) + self.gravity)) + self.gravity_c)

    def update_image_angle(self):
        ''' Rotate image to the correct angle. Create new rect and mask. '''

        # get a new image by rotating the original image
        # not referring to the original image will result in catastrophic memory flooding
        # the constant of -45 is to correct for the fact that image is a triangle
        # NEW_IMG = pg.transform.rotate(self.ORIGINAL_IMAGE, self.angle)
        # flip y-axis of image
        # self.image = pg.transform.flip(NEW_IMG, False, True)
        self.image = pg.transform.rotate(self.ORIGINAL_IMAGE, self.angle)

        # get new mask for collision checking
        # > Note A new mask needs to be recreated each time a sprite's image is changed  
        # > (e.g. if a new image is used or the existing image is rotated).  
        #   https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.collide_mask  
        self.mask = pg.mask.from_surface(self.image)

        # set rect to the new images rect bounds
        # get_rect(**kwargs: Any) accepts a position value as parameter
        self.rect = self.mask.get_rect(center=self.position)

    def update(self):
        # # update y-velocity by gravity
        self.velocity.y += self.calc_gravity_factor()
        # update velocity based on steering and falloff
        self.velocity = (self.velocity * self.velo_falloff) + self.direction

        # update image, position and rect position
        if (self.velocity.x != 0) or (self.velocity.y != 0):
            # make sure velocity is within limits
            self.velocity.clamp_magnitude_ip(self.max_velocity)

            self.position = self.position + self.velocity
            self.angle = -self.position.normalize().angle_to(-self.velocity) + 28.0
            # self.angle = self.position.normalize().angle_to(self.velocity) - 28.0
            self.update_image_angle()
