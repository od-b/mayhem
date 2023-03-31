import pygame as pg
from pygame import Color, Surface, Rect
from pygame.math import Vector2 as Vec2, lerp
from pygame.sprite import Sprite, Group, spritecollide, spritecollideany, collide_mask
from pygame.draw import polygon as draw_polygon
# from pygame.gfxdraw import aapolygon as gfxdraw_aapolygon, aatrigon as gfxdraw_aatrigon


class Player(Sprite):
    def __init__(self, cf_player: dict, cf_map: dict, cf_global: dict, spawn_pos: tuple[int, int]):
        # initalize as pygame sprite
        Sprite.__init__(self)

        # store needed data from cf_global
        self.FPS = int(cf_global['fps_limit'])
        ''' global fps limit '''
        

        # declare nested dicts for readability purposes
        # note that these are not stored in self, and are only read during init
        cf_surface:    dict = cf_player['surface']
        cf_weights:    dict = cf_player['weights']
        cf_gameplay:   dict = cf_player['gameplay']
        cf_phases:     dict = cf_player['phase_durations']

        # store surface settings
        self.color          = Color(cf_surface['color'])
        self.width          = int(cf_surface['width'])
        self.height         = int(cf_surface['height'])

        #### CONSTANTS ####

        # gameplay weights
        self.MAX_HEALTH     = int(cf_gameplay['max_health'])
        self.MAX_MANA       = int(cf_gameplay['max_mana'])

        # acceleration weights. T_ is during thrust
        self.ACCEL_MULTI    = float(cf_weights['acceleration_multiplier'])
        self.MAX_ACCEL      = float(cf_weights['max_acceleration'])
        self.THRUST_ACCEL   = float(cf_weights['thrust_acceleration'])

        # velocity weights
        self.MAX_VELO       = float(cf_weights['max_velocity'])
        self.TERM_VELO      = float(cf_weights['terminal_velocity'])

        # steering weights
        self.HANDLING       = float(cf_weights['handling'])
        self.T_HANDLING     = float(cf_weights['thrust_handling'])

        # using the set timers from cf_phases, calculate the frames needed
        self.THRUST_END_FRAMES        = int(cf_phases['thrust_end'] / 1000) * self.FPS
        ''' n frames to set for the thrust end transition phase '''
        self.CRASH_COOLDOWN_FRAMES    = int(cf_phases['collision_cooldown'] / 1000) * self.FPS
        ''' n frames to set for the crash cooldown phase '''
        self.THRUST_END_LERP_DECREASE = (1.0 / self.THRUST_END_FRAMES)
        ''' weight used for linear interpolation during post thrust transition '''

        # variables used during phase transitions
        self.thrust_end_frames_left         = int(0)
        self.thrust_end_curr_lerp_weight    = 1.0
        self.crash_frames_left              = int(0)
        self.crash_cooldown_frames_left     = int(0)


        # physics related constant weights
        self.GRAVITY_C      = float(cf_map['gravity_c'])
        ''' map gravity constant '''
        self.GRAVITY_M      = float(cf_map['gravity_m'])
        ''' map gravity multiplier '''
        if (cf_weights['mass'] == 0):
            self.MASS = None
        else:
            self.MASS           = float(cf_weights['mass'])
            ''' weight used when applying gravity '''
        self.CENTER_VECTOR  = Vec2(0.0, 0.0)
        ''' used for relative angle calculation '''

        # initialize control and angle-related attributes
        self.thrusting      = False
        ''' whether the thrust key is currently held '''
        self.direction      = Vec2(0.0, 0.0)
        ''' 8-directional vector for reading key controls '''
        self.angle: float   = float(0)
        ''' angle in degrees '''

        # create main physics-related variables
        self.position       = Vec2(spawn_pos)
        ''' position within the map '''
        self.acceleration   = Vec2(0.0, 0.0)
        ''' determines direction and directional change of velocity '''
        self.velocity       = Vec2(0.0, 0.0)
        ''' direction and speed ''' 
        self.grav_effect    = float(0)
        ''' accumulation of gravity '''
        self.temp_max_accel = 0.0
        ''' temporary max acceleration '''

        # other
        self.health: int    = self.MAX_HEALTH
        self.mana: int      = self.MAX_MANA

        self.ORIGINAL_IMAGE = self.create_original_image(self.color)
        # self.ALT_IMAGE = self.create_original_image(Color())
        ''' original image used for transformation '''

        # set .image, .rect and .mask through the update function
        self.update_image()

    def create_original_image(self, color: Color):
        ''' get the the original image used for later transformation
            * ensures the original image is rotated, not the rotated one.
                if this is not done, two things will happen:
                1) The image will become larger after each rotation at an exponential rate
                   this will cause the program to crash when the image takes up too much memory.
                2) The image quality will deteriorate after each rotation
        '''
        # create a surface
        SURF = pg.Surface((self.width, self.height)).convert_alpha()

        # fill the surface with transparent pixels
        SURF.fill((0,0,0,0))
        SURF_RECT = SURF.get_rect()

        # create a polygon using the surface bounds as reference points
        p1 = SURF_RECT.midtop
        p2 = SURF_RECT.bottomright
        p3 = SURF_RECT.bottomleft
        draw_polygon(SURF, color, (p1, p2, p3))

        # rotating to -90 means there's no need to flip later. (pg inverted y-axis)
        IMG = pg.transform.rotate(SURF, -90)
        return IMG

    def update_image(self):
        ''' Create image transformed to the current angle. Create new rect and mask. '''

        # get a new image by rotating the original image
        self.image = pg.transform.rotate(self.ORIGINAL_IMAGE, -self.angle)

        # get new mask for collision checking purposes
        #   > "A new mask needs to be recreated each time a sprite's image is changed  
        #   > (e.g. if a new image is used or the existing image is rotated)."
        #   https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.collide_mask  
        self.mask = pg.mask.from_surface(self.image)

        # set rect to the new images rect bounds. used for blitting through group draw
        self.rect = self.image.get_rect(center=self.position)

    def begin_thrust(self):
        ''' begin thrust phase, increasing acceleration and its limit '''
        self.thrusting = True

    def end_thrust(self):
        ''' end thrust phase, starting transition to normal acceleration limits '''
        self.thrusting = False
        # set transition frames and the lerp weight to their max
        self.thrust_end_frames_left = self.THRUST_END_FRAMES
        self.thrust_end_curr_lerp_weight = 1.0
        self.temp_max_accel = self.THRUST_ACCEL

    def set_accel_thrusting(self):
        ''' reduce gravity effect, increase accceleration. update position. '''
        self.acceleration += (self.direction * self.T_HANDLING)
        self.acceleration.scale_to_length(self.THRUST_ACCEL)

    def set_accel_thrust_ending(self):
        ''' reduce max acceleration gradually over the set frames '''
        self.acceleration.clamp_magnitude_ip(0.1, self.temp_max_accel)
        self.acceleration += (self.direction * self.HANDLING)

        # use linear interpolation to find the right value for current max acceleration
        # finds the point which is a certain percent of fps closer to regular max accel
        self.temp_max_accel = lerp(self.MAX_ACCEL, self.THRUST_ACCEL, (self.thrust_end_curr_lerp_weight))
        self.thrust_end_curr_lerp_weight -= self.THRUST_END_LERP_DECREASE

        # since player has acceleration after thrusting, using clamp magnitude is safe without checks

    def set_accel_default(self):
        self.acceleration += (self.direction * self.HANDLING)
        self.acceleration.x = pg.math.clamp(self.acceleration.x, -self.MAX_ACCEL, self.MAX_ACCEL)
        self.acceleration.y = pg.math.clamp(self.acceleration.y, -self.MAX_ACCEL, self.MAX_ACCEL)
        self.acceleration *= self.ACCEL_MULTI

    def set_velocity_with_grav_effect(self):
        self.velocity = self.acceleration.copy()
        if (self.MASS):
            self.velocity.y += (self.MASS * self.grav_effect)
            if (self.direction.y == -1.0) and (self.grav_effect >= self.MAX_ACCEL):
                # this is not a great solution, but apply some additional gravity if accel up
                self.velocity.y -= (self.acceleration.y / self.MASS)
            self.velocity.y = pg.math.clamp(self.velocity.y, -self.MAX_VELO, self.TERM_VELO)

    def init_collision_recoil(self):
        ''' try to push the player back where it came from by inverting velocity '''
        self.collision_in_progress = True
        self.crash_frames_left = int(self.FPS/4)
        self.thrust_end_frames_left = 0

        if (abs(self.velocity.x < 0.1)):
            if (self.velocity.x > 0):
                self.velocity.x += 0.1
            else:
                self.velocity.x -= 0.1

        if (abs(self.velocity.y < 0.1)):
            if (self.velocity.y > 0):
                self.velocity.y += 0.1
            else:
                self.velocity.y -= 0.1

        self.velocity *= -1.0
        self.position += 2 * self.velocity
        self.velocity *= 0.8

    def update(self, map):
        if (self.crash_frames_left):
            self.velocity *= 0.97
            self.acceleration *= 0.97
            self.grav_effect *= 0.97
            self.crash_frames_left -= 1
            if (self.crash_frames_left == 0):
                # initiate crash cooldown phase. This attribute is checked and/or
                # reduced by the map before allowing new crash frames on collision
                self.crash_cooldown_frames_left = self.CRASH_COOLDOWN_FRAMES
        # elif (self.crash_cooldown_frames_left):
        #     pass
        elif (self.thrusting):
            self.set_accel_thrusting()
            self.grav_effect *= 0.97
            self.velocity = self.acceleration.copy()
        elif (self.thrust_end_frames_left > 0):
            self.set_accel_thrust_ending()
            self.grav_effect *= 0.99
            self.set_velocity_with_grav_effect()
            self.thrust_end_frames_left -= 1
        else:
            self.set_accel_default()
            if (self.grav_effect < self.MAX_ACCEL):
                self.grav_effect = (self.grav_effect + self.GRAVITY_C) * self.GRAVITY_M
            self.set_velocity_with_grav_effect()

        self.position += self.velocity

        self.angle = self.CENTER_VECTOR.angle_to(self.acceleration)

        # update image, position and rect position
        self.update_image()


    # external getters
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
