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
        color_pool: list[Color] | None
            color pool to pick a random color from
            if None, a texture must exist
    '''

    def __init__(self,
            cf_block: dict,
            color_pool: list[Color] | None,
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
            self.color_pool = color_pool
            # otherwise default to the config pallette

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
    def __init__(self, cf_player: dict, cf_map: dict, cf_global: dict, spawn_pos: tuple[int, int]):
        # initalize as pygame sprite
        Sprite.__init__(self)

        # nested dicts
        self.spawn_pos = spawn_pos
        cf_surface: dict = cf_player['surface']
        cf_weights: dict = cf_player['weights']
        
        # store non-player dict settings
        self.FPS_LIMIT     = int(cf_global['fps_limit'])
        # if player has no mass, ignore gravity
        if (cf_weights['mass'] > 0.0):
            self.GRAVITY_C     = float(cf_map['gravity_c'])
            ''' gravity constant '''
            self.GRAVITY_M     = float(cf_map['gravity_m'])
            ''' gravity multiplier '''
        else:
            self.GRAVITY_C = 0.0
            self.GRAVITY_M = 0.0

        # store surface settings
        self.img_src: Surface | None = cf_surface['image']
        self.width         = int(cf_surface['width'])
        self.height        = int(cf_surface['height'])
        self.color         = Color(cf_surface['color'])
        self.thrust_color  = Color(cf_surface['thrust_color'])

        # store constant weights
        self.MAX_HEALTH    = int(cf_weights['max_health'])
        self.MAX_MANA      = int(cf_weights['max_mana'])
        self.MASS          = float(cf_weights['mass'])
        self.VELO_FALLOFF  = float(cf_weights['velocity_falloff'])
        self.HANDLING      = float(cf_weights['handling'])
        self.MAX_VELO      = float(cf_weights['max_velocity'])
        self.TERM_VELO     = self.MAX_VELO + self.MASS

        # special weights during thrust
        self.T_VELO        = float(cf_weights['t_velo'])
        self.T_HANDLING    = float(cf_weights['t_handling'])

        # initialize control and angle-related attributes
        self.CENTER_VECTOR = Vec2(0.0, 0.0)
        ''' used for relative angle calculation '''
        self.thrusting     = False
        ''' whether the thrust key is currently held '''
        self.direction     = Vec2(0.0, 0.0)
        ''' 8-directional vector for reading key controls '''
        self.angle: float  = float(0)
        ''' angle in degrees '''

        # attributes related the post-thrust transition phase
        self.TRANSITION_TIME            = float(cf_weights['t_transition_time'])
        ''' transition time, in seconds '''
        self.TRANSITON_FRAMES           = int(self.TRANSITION_TIME * self.FPS_LIMIT)
        ''' total number of frames used for the transition phase '''
        self.TRANSITION_LERP_DECREASE   = (1.0 / self.TRANSITON_FRAMES)
        ''' equal to to 1% of transition frames '''
        self.transition_frames_left     = int(0)
        ''' num. frames left of transition phase '''
        self.transition_lerp_weight     = float(0)
        ''' weight for linear interpolation during transition '''

        # create main physics-related variables
        self.position      = Vec2(spawn_pos)
        ''' position within the map '''
        self.velocity      = Vec2(0.0, 0.0)
        ''' direction and speed '''
        self.grav_effect   = float(0)
        ''' since angle is calculated from velocity, create another weight to gradually increase gravity '''

        # other
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

            # self.angle = self.CENTER_VECTOR.angle_to(self.velocity)
            # set sprite staple attributes through update_image_angle(); image, rect & mask
            self.update_image_angle()
        else:
            # TODO: support actual images
            self.color = None
            raise ValueError("not yet implemented, don't include an image")

    def get_direction_x(self):
        return self.direction.x

    def get_direction_y(self):
        return self.direction.y

    def get_grav_effect(self):
        return self.grav_effect

    def get_position(self):
        return self.rect.center

    def get_angle(self):
        return self.angle

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

    def begin_thrust(self):
        ''' begin thrust phase, increasing velocity and its limit '''
        self.thrusting = True
    
    def end_thrust(self):
        ''' end thrust phase, starting transition to normal velocity limits '''
        self.thrusting = False
        # set transition frames and the lerp weight to their max
        self.transition_frames_left = self.TRANSITON_FRAMES
        self.transition_lerp_weight = 1.0

    def update(self):

        if (self.thrusting):
            self.grav_effect *= 0.97    # reduce gravity by 3%
            self.velocity += (self.direction * self.T_HANDLING)
            self.velocity.scale_to_length(self.T_VELO)
            self.position += self.velocity
        else:
            self.velocity += (self.direction * self.HANDLING)

            if (self.transition_frames_left > 0):
                self.grav_effect *= 0.99    # reduce gravity by 1%
                # reduce max velocity gradually over the set time period.
                # print(f'frames left: {self.transition_frames_left}')

                # use linear interpolation to find the right value for current max velocity
                # finds the point which is a certain percent of fps closer to regular max velo
                curr_max_velo = pg.math.lerp(self.MAX_VELO, self.T_VELO, (self.transition_lerp_weight))

                # since player has velocity after thrusting, using clamp magnitude is safe without checks
                self.velocity.clamp_magnitude_ip(self.MAX_VELO, curr_max_velo)

                self.transition_frames_left -= 1
                self.transition_lerp_weight -= self.TRANSITION_LERP_DECREASE
            else:
                self.velocity *= self.VELO_FALLOFF
                
                # if (abs(self.velocity.x) > self.MAX_VELO) or (abs(self.velocity.y) > self.MAX_VELO):
                #     self.velocity.clamp_magnitude_ip(self.MAX_VELO)
                    
                self.velocity.x = pg.math.clamp(self.velocity.x, -self.MAX_VELO, self.MAX_VELO)
                self.velocity.y = pg.math.clamp(self.velocity.y, -self.MAX_VELO, self.TERM_VELO)

                if (self.grav_effect < self.TERM_VELO):
                    self.grav_effect = (self.grav_effect + self.GRAVITY_C) * self.GRAVITY_M

            if (self.direction.y == -1) and (self.grav_effect > 0):
                self.position.y += ((self.velocity.y / 2) + (self.grav_effect / 2))
                # use fuel call here
            else:
                self.position.y += (self.velocity.y + self.grav_effect)

            self.position.x += self.velocity.x

        self.angle = self.CENTER_VECTOR.angle_to(self.velocity)

        # update image, position and rect position
        self.update_image_angle()
