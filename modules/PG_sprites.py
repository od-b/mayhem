from random import randint

import pygame as pg
from pygame import Color, Surface
from pygame.math import Vector2 as Vec2
from pygame.sprite import Sprite
from math import cos, sin, radians


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
        self.MASS = float(cf_block['mass'])
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

        self.GRAVITY   = float(cf_map['gravity'])
        self.GRAVITY_C = float(cf_map['gravity_c'])
        # nested dicts
        cf_surface: dict = cf_player['surface']
        cf_weights: dict = cf_player['weights']
        
        # store dict settings
        self.img_src: Surface | None = cf_player['surface']['image']
        self.width         = int(cf_surface['width'])
        self.height        = int(cf_surface['height'])
        self.color         = Color(cf_surface['color'])
        self.thrust_color  = Color(cf_surface['thrust_color'])

        self.MAX_HEALTH    = int(cf_weights['max_health'])
        self.MAX_MANA      = int(cf_weights['max_mana'])
        self.MASS          = float(cf_weights['mass'])
        self.VELO_FALLOFF  = float(cf_weights['velocity_falloff'])
        self.THRUST_FORCE  = float(cf_weights['thrust_force'])
        self.HANDLING      = float(cf_weights['handling'])
        self.MAX_VELO      = float(cf_weights['max_velocity'])
        self.T_MAX_VELO    = self.MAX_VELO + float(cf_weights['t_max_velocity'])

        # increased positive y-velocity, to simulate gravity
        self.TERM_VELO     = self.MAX_VELO + self.MASS
        self.T_TERM_VELO   = self.T_MAX_VELO + self.MASS

        # set up vectors
        self.position      = Vec2(initial_pos)
        self.velocity      = Vec2(0.0, 0.0)
        self.direction     = Vec2(0.0, 0.0)
        self.EMPTY_VECTOR  = Vec2(0.0, 0.0)
        ''' used for angle calculation '''

        # set up variables
        self.thrust: bool  = False
        self.thrust_remaining = int(0)
        self.angle: float  = float(0)
        self.health: int   = self.MAX_HEALTH
        self.mana: int     = self.MAX_MANA

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
            # rotating to -90 means there's no need to flip later.
            self.ORIGINAL_IMAGE = pg.transform.rotate(IMG, -90)
            self.height = IMG_RECT.h
            self.width = IMG_RECT.w

            # set sprite staple attributes through update_image_angle(); image, rect & mask
            self.angle = self.EMPTY_VECTOR.angle_to(self.velocity)
            self.update_image_angle()
        else:
            # TODO: support actual images
            self.color = None
            raise ValueError("not yet implemented, don't include an image")

    def get_direction_x(self):
        return self.direction.x

    def get_direction_y(self):
        return self.direction.y

    def get_position(self):
        return self.rect.center

    def get_angle(self):
        return self.angle

    def draw_thruster(self, len: float, width: int):
        p1 = Vec2(self.position)
        p2 = Vec2(self.position - (len * self.velocity))
        pg.draw.line(self.surface, self.thrust_color, p1, p2, width)

    def calc_gravity_factor(self):
        ''' return a positive float based on velocity, mass and global gravity constant '''
        return (self.GRAVITY * (abs(self.velocity.y) + self.GRAVITY)) + self.GRAVITY_C

    def update_image_angle(self):
        ''' Rotate image to the correct angle. Create new rect and mask. '''

        # get a new image by rotating the original image
        # not referring to the original image will result in catastrophic memory flooding
        self.image = pg.transform.rotate(self.ORIGINAL_IMAGE, -self.angle)

        # get new mask for collision checking
        # > Note A new mask needs to be recreated each time a sprite's image is changed  
        # > (e.g. if a new image is used or the existing image is rotated).  
        #   https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.collide_mask  
        self.mask = pg.mask.from_surface(self.image)

        # set rect to the new images rect bounds
        # get_rect(**kwargs: Any) accepts a position value as parameter
        self.rect = self.image.get_rect(center=self.position)

    def update(self):
        # # update y-velocity by gravity
        # update velocity based on steering and falloff
        if (self.thrust):
            self.velocity *= self.THRUST_FORCE
            self.velocity.x = pg.math.clamp(self.velocity.x, -self.T_MAX_VELO, self.T_MAX_VELO)
            self.velocity.y = pg.math.clamp(self.velocity.y, -self.T_MAX_VELO, self.T_TERM_VELO)
        else:
            self.velocity.y += self.calc_gravity_factor()
            self.velocity *= self.VELO_FALLOFF
            self.velocity.x = pg.math.clamp(self.velocity.x, -self.MAX_VELO, self.MAX_VELO)
            self.velocity.y = pg.math.clamp(self.velocity.y, -self.MAX_VELO, self.TERM_VELO)

        self.velocity += (self.direction * self.HANDLING)
        self.position += self.velocity
        self.angle = self.EMPTY_VECTOR.angle_to(self.velocity)

        # update image, position and rect position
        self.update_image_angle()
