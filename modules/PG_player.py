import pygame as pg
from pygame import Color, Surface, Rect
from pygame.math import Vector2 as Vec2, lerp
from pygame.sprite import Sprite
from pygame.draw import polygon as draw_polygon
# from pygame.gfxdraw import aapolygon as gfxdraw_aapolygon, aatrigon as gfxdraw_aatrigon


class Player(Sprite):
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
        self.ACCEL_FALLOFF  = float(cf_weights['accel_falloff'])
        self.HANDLING      = float(cf_weights['handling'])
        self.MAX_ACCEL      = float(cf_weights['max_accel'])
        self.MAX_GRAV_ACCEL     = self.MAX_ACCEL + self.MASS

        # special weights during thrust
        self.T_ACCEL        = float(cf_weights['t_accel'])
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
        
        # attributes related to collision
        self.crash_frames = int(0)
        self.recoil_target: Vec2 = Vec2(0.0, 0.0)
        self.recoil_lerp_weight = float(0)
        
        self.old_pos = Vec2(spawn_pos)
        ''' last position within the map '''

        # create main physics-related variables
        self.position      = Vec2(spawn_pos)
        ''' position within the map '''
        self.acceleration  = Vec2(0.0, 0.0)
        ''' determines angle and rate of change to velocity '''
        self.velocity  = Vec2(0.0, 0.0)
        ''' direction and speed ''' 
        self.grav_effect   = float(0)

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
            # gfxdraw_aatrigon(
            #     IMG, 
            #     int(p1.x), int(p1.y),
            #     int(p2.x), int(p2.y),
            #     int(p3.x), int(p3.y),
            #     self.color
            # )
            # gfxdraw_aapolygon(IMG, (p1, p2, p3), self.color)
            draw_polygon(IMG, self.color, (p1, p2, p3))

            # store the original image for transformation
            # otherwise, pygame will flood the memory in a matter of seconds
            # put short; ensures the original image is rotated, not the rotated one
            # rotating to -90 means there's no need to flip later.
            self.ORIGINAL_IMAGE = pg.transform.rotate(IMG, -90)

            # self.angle = self.CENTER_VECTOR.angle_to(self.acceleration)
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

    def begin_thrust(self):
        ''' begin thrust phase, increasing acceleration and its limit '''
        self.thrusting = True
    
    def end_thrust(self):
        ''' end thrust phase, starting transition to normal acceleration limits '''
        self.thrusting = False
        # set transition frames and the lerp weight to their max
        self.transition_frames_left = self.TRANSITON_FRAMES
        self.transition_lerp_weight = 1.0

    def get_real_bounds(self):
        ''' get the actual rect around the player, using mask bounding rect '''
        bounds: Rect = self.mask.get_bounding_rects()[0]
        return bounds

    def init_collision_recoil(self, collidepos: Vec2):
        self.crash_frames = self.FPS_LIMIT
        self.transition_frames_left = 0

        real_self_rect = self.get_real_bounds()

        print(f'real_self_rect: {real_self_rect}')
        print(f'real_self_center: {real_self_rect.center}')
        # print(f'mask_bounds: {mask_bounds}')
        # print(f'collidepos: {collidepos}')

        distance_to_collidepos = self.position.distance_to(collidepos)
        # print(f'distance to collidepos_2: {distance_to_collidepos}')

        # collidepos_angle = self.acceleration.normalize().angle_to(collidepos.normalize())
        # print(f'angle to collidepos: {collidepos_angle}')
        self.acceleration *= 0.5

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

    def update_case_crash(self):
        self.crash_frames -= 1
        # self.position += (self.recoil_target_pos)

    def update_case_thrusting(self):
        ''' reduce gravity effect, increase accceleration. update position. '''
        self.grav_effect *= 0.97    # reduce gravity by 3%
        self.acceleration += (self.direction * self.T_HANDLING)
        self.acceleration.scale_to_length(self.T_ACCEL)

    def update_case_transition_end(self):
        ''' reduce max acceleration gradually over the set time period. '''
        self.acceleration += (self.direction * self.HANDLING)
        self.grav_effect *= 0.99    # reduce gravity by 1%

        # use linear interpolation to find the right value for current max acceleration
        # finds the point which is a certain percent of fps closer to regular max accel
        new_max_accel = lerp(self.MAX_ACCEL, self.T_ACCEL, (self.transition_lerp_weight))

        # since player has acceleration after thrusting, using clamp magnitude is safe without checks
        self.acceleration.clamp_magnitude_ip(self.MAX_ACCEL, new_max_accel)

        self.transition_frames_left -= 1
        self.transition_lerp_weight -= self.TRANSITION_LERP_DECREASE

    def update_case_default(self):
        ''' clamp acceleration, increase gravity '''
        self.acceleration += (self.direction * self.HANDLING)
        self.acceleration *= self.ACCEL_FALLOFF
        self.acceleration.x = pg.math.clamp(self.acceleration.x, -self.MAX_ACCEL, self.MAX_ACCEL)
        self.acceleration.y = pg.math.clamp(self.acceleration.y, -self.MAX_ACCEL, self.MAX_GRAV_ACCEL)

        if (self.grav_effect < self.MAX_GRAV_ACCEL):
            self.grav_effect = (self.grav_effect + self.GRAVITY_C) * self.GRAVITY_M

    def update(self):
        if (self.crash_frames):
            self.update_case_crash()
        elif (self.thrusting):
            # reduce gravity effect, increase accceleration. update position.
            self.update_case_thrusting()
        elif (self.transition_frames_left > 0):
            # reduce max acceleration gradually
            self.update_case_transition_end()
        else:
            # self.position.y += 0.5

            # clamp acceleration, increase gravity
            self.update_case_default()

        self.position += self.acceleration
        self.angle = self.CENTER_VECTOR.angle_to(self.acceleration)

        # update image, position and rect position
        self.update_image_angle()


    # if (self.direction.y == -1) and (self.grav_effect > 0):
    #     self.position.y += ((self.acceleration.y / 2) + (self.grav_effect / 2))
    # else:
    #     self.position.y += (self.acceleration.y + self.grav_effect)
    # self.position.y += (self.acceleration.y + self.grav_effect)


    # if ((abs(self.position.x) - abs(self.old_pos.x)) > 1.0):
    #     self.old_pos = self.position
    #     # self.old_pos.x = self.position.x
    # elif ((abs(self.position.y) - abs(self.old_pos.y)) > 1.0):
    #     # self.old_pos.y = self.position.y
    #     self.old_pos = self.position
    # print(f'1) last pos: {self.old_pos}')
    # print(f'2) current pos: {self.position}')


    # def init_collision_recoil(self):
    #     # self.TRANSITON_FRAMES           = int(self.TRANSITION_TIME * self.FPS_LIMIT)
    #     # self.TRANSITION_LERP_DECREASE   = (1.0 / self.TRANSITON_FRAMES)
    #     dist_to_last_pos = self.position.distance_to(self.last_position)
    #     print(f'dist_to_last_pos: {dist_to_last_pos}')

    #     self.recoil_target = self.last_position
    #     print(f'recoil_target_raw: {self.recoil_target}')

    #     self.recoil_target.scale_to_length((dist_to_last_pos * dist_to_last_pos))
    #     print(f'recoil_target_scaled: {self.recoil_target}')

    #     recoil_length = self.position.distance_to(self.recoil_target)
    #     print(f'recoil_length: {recoil_length}')

    #     # self.crash_frames = int(recoil_strength * self.FPS_LIMIT)
    #     self.crash_frames = self.FPS_LIMIT

    #     self.recoil_lerp_decrease = (1.0 / self.crash_frames)
    #     self.recoil_lerp_weight = 1.0