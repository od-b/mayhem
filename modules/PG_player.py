from pygame import Color, Surface, transform, mask, math as pg_math
from pygame.math import Vector2 as Vec2, lerp
from pygame.sprite import Sprite
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
        cf_colors:     dict = cf_surface['colors']
        cf_weights:    dict = cf_player['weights']
        cf_gameplay:   dict = cf_player['gameplay']
        cf_phases:     dict = cf_player['phase_durations']
        
        # store relevant map settings
        self.MAP_GRAV_C      = float(cf_map['gravity_c'])
        ''' map gravity constant '''
        self.MAP_GRAV_M      = float(cf_map['gravity_m'])
        ''' map gravity multiplier '''

        # store surface settings
        self.SURF_WIDTH          = int(cf_surface['width'])
        self.SURF_HEIGHT         = int(cf_surface['height'])

        #### CONSTANTS ####

        # gameplay weights
        self.MAX_HEALTH     = int(cf_gameplay['max_health'])
        self.MAX_MANA       = int(cf_gameplay['max_mana'])

        # acceleration weights
        self.ACCEL_REDUCT    = float(cf_weights['acceleration_multiplier'])
        self.MAX_ACCEL      = float(cf_weights['max_acceleration'])
        self.THRUST_MAX_ACCEL   = float(cf_weights['thrust_acceleration'])

        # velocity weights
        self.MAX_VELO       = float(cf_weights['max_velocity'])
        self.MAX_GRAV      = float(cf_weights['terminal_velocity'])

        # steering weights
        self.HANDLING            = float(cf_weights['handling'])
        self.THRUST_HANDLING_M   = float(cf_weights['thrust_handling_m'] * self.HANDLING)

        # phase weights / durations. for time related settings, calculate the frames needed
        self.THRUST_BEGIN_FRAMES        = int(cf_phases['thrust_begin'] * self.FPS)
        ''' n frames to set for the thrust end transition phase '''
        self.THRUST_END_FRAMES          = int(cf_phases['thrust_end'] * self.FPS)
        ''' n frames to set for the thrust end transition phase '''
        self.COLLISION_COOLDOWN_FRAMES  = int(cf_phases['collision_cooldown'] * self.FPS)
        ''' n frames to set for the crash cooldown phase '''
        self.COLLISION_RECOIL_MULTI     = float(cf_phases['collision_recoil'] * self.FPS)
        ''' relational multiplier between crash velocity, FPS and recoil frames '''
        self.THRUST_END_LERP_DECREASE   = float(1.0 / self.THRUST_END_FRAMES)
        ''' weight used for linear interpolation during post thrust transition '''

        # misc constants
        self.MASS = float(cf_weights['mass'])
        ''' multiplier used when applying gravity to velocity '''
        self.COLLISION_FORCE = float(cf_weights['collision_recoil_force'])
        ''' how drastic the recoil of collision will be '''
        self.VEC_CENTER  = Vec2(0.0, 0.0)
        ''' used for relative angle calculation '''

        #### VARIABLES ####

        # variables used during phase transitions
        self.thrust_end_frames_left         = int(0)
        self.thrust_end_curr_lerp_weight    = 1.0
        self.thrust_begin_curr_lerp_weight  = 0.0
        self.thrust_begin_accel_length      = 0.0
        self.thrust_begin_frames_left       = int(0)
        self.collision_recoil_frames_left   = int(0)
        self.collision_cooldown_frames_left = int(0)

        # initialize control and angle-related attributes
        self.thrusting      = False
        ''' whether the thrust key is currently held '''
        self.direction      = Vec2(0.0, 0.0)
        ''' 8-directional vector for reading key controls '''
        self.angle          = 0.0
        ''' angle in degrees '''

        # create main physics-related variables
        self.position       = Vec2(spawn_pos)
        ''' position within the map '''
        self.acceleration   = Vec2(0.001, 0.00001)
        ''' determines direction and directional change of velocity '''
        self.velocity       = Vec2(0.0, 0.0)
        ''' direction and speed ''' 
        self.grav_force    = 0.0
        ''' accumulation of gravity '''
        self.temp_max_accel = 0.0
        ''' temporary max acceleration '''

        # other
        self.health: int    = self.MAX_HEALTH
        self.mana: int      = self.MAX_MANA
        
        # store image variants as constants
        self.DEFAULT_IMAGE = self.set_up_image(cf_colors['default'])
        self.COLLISION_CD_IMAGE = self.set_up_image(cf_colors['collision_cooldown'])

        self.curr_image_src = self.DEFAULT_IMAGE
        ''' which of the loaded images is currently in use '''

        self.PHASE_DEBUG_PRINT = False
        # set .image, .rect and .mask through the update function
        self.update_image()

    def set_up_image(self, color: Color):
        ''' get the the original image used for later transformation
            * ensures the original image is rotated, not the rotated one.
                if this is not done, two things will happen:
                1) The image will become larger after each rotation at an exponential rate
                   this will cause the program to crash when the image takes up too much memory.
                2) The image quality will deteriorate after each rotation
        '''
        # create a surface
        SURF = Surface((self.SURF_WIDTH, self.SURF_HEIGHT)).convert_alpha()

        # fill the surface with transparent pixels
        SURF.fill((0,0,0,0))
        SURF_RECT = SURF.get_rect()

        # create a polygon using the surface bounds as reference points
        p1 = SURF_RECT.midtop
        p2 = SURF_RECT.bottomright
        p3 = SURF_RECT.bottomleft
        draw_polygon(SURF, color, (p1, p2, p3))

        # rotating to -90 means there's no need to flip later. (pg inverted y-axis)
        IMG = transform.rotate(SURF, -90)
        return IMG

    def update_image(self):
        ''' update self.image, transforming it to the current angle. Update self .rect, .mask. '''

        # get a new image by rotating the original image
        self.image = transform.rotate(self.curr_image_src, -self.angle)

        # get new mask for collision checking purposes
        #   > "A new mask needs to be recreated each time a sprite's image is changed  
        #   > (e.g. if a new image is used or the existing image is rotated)."
        #   https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.collide_mask  
        self.mask = mask.from_surface(self.image)

        # set rect to the new images rect bounds. used for blitting through group draw
        self.rect = self.image.get_rect(center=self.position)

    def init_phase_thrust_begin(self):
        ''' call to begin thrust phase, gradually increasing acceleration and its limit
            * uses the current acceleration to calculate the needed frames
            * phase intent: smooth transition from normal to thrust acceleration
        '''
        self.thrusting = True
        self.thrust_begin_curr_lerp_weight = 0.0

        # calculate the frames appropriate to scale up to max thrust acceleration,
        # depending on the current acceleration and set thrust begin frames
        self.thrust_begin_accel_length = self.acceleration.length()
        weighted_diff = (self.THRUST_MAX_ACCEL - self.thrust_begin_accel_length) / 1.0
        self.thrust_begin_frames_left = int(self.THRUST_BEGIN_FRAMES * weighted_diff)
        self.thrust_begin_lerp_increase = 1.0 / self.thrust_begin_frames_left

        if (self.PHASE_DEBUG_PRINT):
            print(f'thrust_begin_lerp_increase={self.thrust_begin_lerp_increase}')
            print(f'self.thrust_begin_frames_left: {self.thrust_begin_frames_left}')

    def init_phase_thrust_end(self):
        ''' call to end thrust phase, starting transition to normal acceleration limits
            * phase intent: smooth transition from thrust to normal acceleration
        '''
        self.thrusting = False
        self.thrust_begin_frames_left = 0
        # set transition frames and the lerp weight to their max
        self.thrust_end_frames_left = self.THRUST_END_FRAMES
        self.thrust_end_curr_lerp_weight = 1.0
        self.temp_max_accel = self.acceleration.length()

    def init_phase_collision_recoil(self):
        ''' call to begin recoil phase. Rather naive solution, inverting velocity by a multiplier
            * if the player has thrust end frames left, cancel them early
            * if the player is currently thrusting, reset to thrust begin to start a new gradual transition
            * if the collision point is below the player (velo = down), reset componding grav effect
            * intent:
            *   push player away from terrain upon a collion
            *   punish the player by limiting controls, acceleration and velocity, as well as resetting the thrust phase
        '''

        # in case of very low velocity impacts, increase velocity slightly
        if (abs(self.velocity.x < 0.1)):
            if (self.velocity.x > 0):
                self.velocity.x = 0.1
            else:
                self.velocity.x = -0.1

        if (abs(self.velocity.y < 0.1)):
            if (self.velocity.y > 0):
                self.velocity.y = 0.1
            else:
                self.velocity.y = -0.1

        # scale recoil frames to how fast the sprite was going
        self.collision_recoil_frames_left = round(self.velocity.length() * self.COLLISION_RECOIL_MULTI)
        self.collision_cooldown_frames_left = self.COLLISION_COOLDOWN_FRAMES + self.collision_recoil_frames_left

        # invert velocity, reduce acceleration
        self.velocity *= -self.COLLISION_FORCE
        self.acceleration *= self.COLLISION_FORCE

        # if the object we crashed into is below is, "reset" the compounding gravity effect
        if (self.velocity.y == -1):
            self.grav_force *= 0.01
        self.curr_image_src = self.COLLISION_CD_IMAGE

        # end any thrust end frames that might be active
        self.thrust_end_frames_left = 0

        # reset thrust phase if currently in a thrust phase
        if (self.thrusting):
            self.init_phase_thrust_begin()

    def default_frame(self):
        ''' update acceleration, velocity and compounding gravity '''
        self.acceleration += (self.direction * self.HANDLING)
        self.acceleration.update(
            pg_math.clamp(self.acceleration.x, -self.MAX_ACCEL, self.MAX_ACCEL),
            pg_math.clamp(self.acceleration.y, -self.MAX_ACCEL, self.MAX_ACCEL)
        )
        self.acceleration *= self.ACCEL_REDUCT

        # increase compounding gravity and add constant
        self.grav_force = lerp(self.grav_force, self.MAX_GRAV, self.MAP_GRAV_M) + self.MAP_GRAV_C

        # update velocity. apply the current gravity effect.
        self.velocity.update(self.acceleration)
        self.velocity.y += (self.MASS * self.grav_force)

        if (self.direction.y == -1.0) and (self.grav_force >= self.MAX_GRAV):
            # this is not a great solution, but, it *almost* completely counteracts upwards accel without thrust
            # TODO: TEST WITH A VARIETY OF MASS; or find a better solution
            self.velocity.y -= (0.2 * self.grav_force) * (self.acceleration.y / self.MASS)

    def apply_thrust_begin_frame(self):
        ''' gradually increase to thrust acceleration over the set frames '''
        self.thrust_begin_frames_left -= 1

        # reduce max acceleration gradually over the set frames
        self.acceleration += (self.direction * self.THRUST_HANDLING_M)

        # use linear interpolation to find the right value for current max acceleration
        # finds the point which is a certain percent of fps closer to max thrust accel
        new_accel = lerp(self.thrust_begin_accel_length, self.THRUST_MAX_ACCEL, (self.thrust_begin_curr_lerp_weight))
        self.thrust_begin_curr_lerp_weight += self.thrust_begin_lerp_increase

        if (self.PHASE_DEBUG_PRINT):
            if (self.thrust_begin_frames_left < 5):
                print(f'thrust_begin_frames_left={self.thrust_begin_frames_left}; new_accel={new_accel}')
                print(f'thrust_begin_curr_lerp_weight={self.thrust_begin_curr_lerp_weight}')
                if (self.thrust_begin_frames_left == 0):
                    print(f'[thrust_begin_summary] start: {self.thrust_begin_accel_length}; now={new_accel}')

        # scale up acceleration
        self.acceleration.scale_to_length(new_accel)

        # apply gravity
        self.grav_force *= 0.99

        # update velocity. apply the current gravity effect.
        self.velocity.update(self.acceleration)
        self.velocity.y += (self.MASS * self.grav_force)

    def thrust_frame(self):
        ''' applies acceleration directly to velocity at increased handling and force.'''
        self.acceleration += (self.direction * self.THRUST_HANDLING_M)
        self.acceleration.scale_to_length(self.THRUST_MAX_ACCEL)
        self.grav_force *= 0.99
        self.velocity.update(self.acceleration)
        self.velocity.y += (self.MASS * self.grav_force)
        # self.velocity.y = pg_math.clamp(self.velocity.y, -self.MAX_VELO, self.MAX_GRAV)

    def apply_thrust_end_frame(self):
        ''' gradually reduce the max acceleration. apply gravity. 
            * intent: smooth acceleration from thrust level to normal
        '''
        self.thrust_end_frames_left -= 1

        # reduce max acceleration gradually over the set frames
        self.acceleration += (self.direction * self.HANDLING)

        # use linear interpolation to find the right value for current max acceleration
        # finds the point which is a certain percent of fps closer to regular max accel
        self.temp_max_accel = lerp(self.MAX_ACCEL, self.THRUST_MAX_ACCEL, (self.thrust_end_curr_lerp_weight))
        self.acceleration.clamp_magnitude_ip(0.1, self.temp_max_accel)
        self.thrust_end_curr_lerp_weight -= self.THRUST_END_LERP_DECREASE


        # increase compounding gravity
        self.grav_force = lerp((self.grav_force + self.MAP_GRAV_C), self.MAX_GRAV, self.MAP_GRAV_M)

        # update velocity. apply the current gravity effect.
        self.velocity.update(self.acceleration)
        self.velocity.y += (self.MASS * self.grav_force)

    def update(self):
        if (self.collision_cooldown_frames_left):
            # collision cooldown frames co-occur with other frames
            self.collision_cooldown_frames_left -= 1
            if (self.collision_cooldown_frames_left == 0):
                self.curr_image_src = self.DEFAULT_IMAGE

        if (self.collision_recoil_frames_left):
            self.collision_recoil_frames_left -= 1
            self.grav_force *= 0.99
        elif (self.thrust_begin_frames_left):
            self.apply_thrust_begin_frame()
        elif (self.thrusting):
            self.thrust_frame()
        elif (self.thrust_end_frames_left):
            self.apply_thrust_end_frame()
        else:
            self.default_frame()

        self.position += self.velocity
        self.angle = self.VEC_CENTER.angle_to(self.acceleration)
        # update image, position and rect position
        self.update_image()

    #### FORMATTED STRING GETTERS ####

    def get_str_dir_x(self):
        return f'{self.direction.x():.2f}'

    def get_str_dir_y(self):
        return f'{self.direction.y():.2f}'

    def get_str_angle(self):
        return f'{self.angle():.1f}'

    def get_str_gravity(self):
        return f'{self.grav_force():.3f}'

    #### ORDINARY GETTERS ####

    def get_max_grav_effect(self):
        return self.MAX_GRAV

    def get_grav_effect(self):
        return self.grav_force


''' TODO
* physics:
    - improve how gravity is distributed when not thrusting and accelerating north

* gameplay:
    - reduce health -> 
    - reduce mana ->

* visualizing information:
    - cooldown phase -> swap to an alt image with 50% transparancy for the duration
    - animate thrust -> 
    - 
'''
