from pygame import Surface, transform, mask, math as pg_math
from pygame.math import Vector2 as Vec2, lerp, clamp
from pygame.sprite import Sprite

from .PG_common import load_sprites_tuple


class Player(Sprite):
    ''' 
        The init ONLY sets up constants. all variables are set through .reset_all_attributes()
        this allows the map to determine an appropriate spawn position depending on size,
        as well as providing an extremely easy way to reset to a default state if desired.

        For readability purposes, ALL constants in this class are defined in caps, 
        and are strictly never modified.
        
        ---
        Setup
        ---
        1) Create the player object. constants and spritesheets are set up.
            The methods get_idle_bounds and spawn are now callable.
            Calling other methods prior to spawning will result in a crash.
        2) Call .spawn() when ready
    '''
    def __init__(self, cf_player: dict, cf_map: dict, cf_global: dict):
        Sprite.__init__(self)

        cf_physics:  dict = cf_player['physics']
        cf_gameplay: dict = cf_player['gameplay']
        cf_phases:   dict = cf_player['phase_durations']
        cf_spritesheets: dict = cf_player['spritesheets']

        # self.MAP_HAS_GRAVITY = cf_map['has_gravity']
        self.FPS = int(cf_global['fps_limit'])
        ''' global fps limit '''

        ### raw constants ###
        # gameplay
        self.FUEL_CONSUMPTION   = float(cf_gameplay['fuel_consumption'])
        self.MAX_HEALTH         = float(cf_gameplay['max_health'])
        self.MAX_FUEL           = float(cf_gameplay['max_fuel'])
        self.MIN_COLL_HP_LOSS   = float(cf_gameplay['min_collision_health_loss'])
        self.MAX_COLL_HP_LOSS   = float(cf_gameplay['max_collision_health_loss'])
        # acceleration & velocity
        self.HANDLING           = float(cf_physics['handling'])
        self.MAX_ACCEL          = float(cf_physics['max_acceleration'])
        self.THRUST_MAGNITUDE   = float(cf_physics['thrust_magnitude'])
        self.MAX_VELO           = float(cf_physics['max_velocity'])
        self.COLLISION_RECOIL_W = float(cf_physics['collision_recoil_w'])
        self.MASS               = float(cf_physics['mass'])
        ''' how drastic the recoil of collision will be '''
        
        self.GRAV_C = float(self.MASS * cf_map['gravity_c'])

        ### secondary /dependant constants ###
        self.THRUST_HANDLING_M  = float(cf_physics['thrust_handling_m'] * self.HANDLING)

        # phases / durations; for time related settings, calculate the frames needed
        self.THRUST_BEGIN_FRAMES_M      = int(cf_phases['thrust_begin'] * self.FPS)
        ''' n frames to set for the thrust end transition phase '''
        self.THRUST_END_FRAMES          = int(cf_phases['thrust_end'] * self.FPS)
        ''' n frames to set for the thrust end transition phase '''
        self.COLLISION_COOLDOWN_FRAMES  = int(cf_phases['collision_cooldown'] * self.FPS)
        ''' n frames to set for the crash cooldown phase '''
        self.COLLISION_FRAMES_M         = float(cf_phases['collision_recoil_m'] * self.FPS)
        ''' relational multiplier between crash velocity, FPS and recoil frames '''

        # misc constants
        self.THRUST_END_LERP_DECREASE   = float(1.0 / self.THRUST_END_FRAMES)
        ''' weight used for linear interpolation during post thrust transition '''
        self.VEC_CENTER  = Vec2(0.0, 0.0)
        ''' used for relative angle calculation '''

        self.PHASE_DEBUG_PRINT = False

        scalar = cf_spritesheets['image_scalar']
        cf_idle: dict = cf_spritesheets['idle']
        cf_shield: dict = cf_spritesheets['shield']
        cf_destroyed: dict = cf_spritesheets['destroyed']
        cf_thrust_a: dict = cf_spritesheets['thrust_a']
        cf_thrust_b: dict = cf_spritesheets['thrust_b']
        cf_thrust_c: dict = cf_spritesheets['thrust_c']

        self.IDLE_IMAGES      = load_sprites_tuple(cf_idle['path'], cf_idle['n_images'], scalar, None)
        self.SHIELD_IMAGES    = load_sprites_tuple(cf_shield['path'], cf_shield['n_images'], scalar, None)
        self.DESTROYED_IMAGES = load_sprites_tuple(cf_destroyed['path'], cf_destroyed['n_images'], scalar, None)
        self.THRUST_A_IMAGES  = load_sprites_tuple(cf_thrust_a['path'], cf_thrust_a['n_images'], scalar, None)
        self.THRUST_B_IMAGES  = load_sprites_tuple(cf_thrust_b['path'], cf_thrust_b['n_images'], scalar, None)
        self.THRUST_C_IMAGES  = load_sprites_tuple(cf_thrust_c['path'], cf_thrust_c['n_images'], scalar, None)

    def get_idle_bounds(self):
        return self.IDLE_IMAGES[0][0].get_rect().copy()

    def spawn(self, position: tuple[int, int]):
        # store the position as spawn position
        self.SPAWN_POS = position

        # initialize all attributes through the reset function
        self.reset_all_attributes()

        # initialize image, rect and mask through the update function
        self.update_image()

    def reset_all_attributes(self):
        ''' reset (or set) all variable attributes used across all player methods '''
        # phase transitions
        self.thrust_begin_frames_left:         int = int(0)
        self.thrust_end_frames_left:           int = int(0)
        self.thrust_end_curr_lerp_weight:    float = 1.0
        self.thrust_begin_curr_lerp_weight:  float = 0.0
        self.thrust_begin_accel_length:      float = 0.0
        self.collision_recoil_frames_left:     int = int(0)
        self.collision_cooldown_frames_left:   int = int(0)

        # attributes related to player key-actions
        self.key_thrusting:  bool = False
        ''' whether the thrust key is currently held '''
        self.key_direction:  Vec2 = Vec2(0.0, 0.0)
        ''' 8-directional vector for reading key controls '''

        # initialize physics and angle - related attributes
        self.position:       Vec2 = Vec2(self.SPAWN_POS)
        ''' position within the map '''
        self.acceleration:   Vec2 = Vec2(0.001, 0.00001)
        ''' determines direction and directional change of velocity '''
        self.velocity:       Vec2 = Vec2(0.0, 0.0)
        ''' direction and speed '''
        self.angle:          float = 0.0
        ''' angle in degrees '''
        self.temp_max_accel: float = 0.0
        ''' temporary max acceleration '''
        self.cumulative_grav_c = float(0)
        ''' cumulative gravity constant '''

        self.health = self.MAX_HEALTH
        self.fuel   = self.MAX_FUEL

        self.special_image_active = False
        self.curr_image_type: tuple[tuple[Surface, ...], int] = self.IDLE_IMAGES
        self.curr_image_index = 0
        self.curr_image: Surface = self.curr_image_type[0][self.curr_image_index]

    def cycle_active_image(self):
        if (self.curr_image_index >= self.curr_image_type[1]):
            self.curr_image_index = 0
        else:
            self.curr_image_index += 1
        self.curr_image = self.curr_image_type[0][self.curr_image_index]

    def set_special_image_type(self, image_type: tuple[tuple[Surface, ...], int]):
        self.special_image_active = True
        self.curr_image_type = image_type
        self.cycle_active_image()

    def set_idle_image_type(self):
        self.special_image_active = False
        self.curr_image_type = self.IDLE_IMAGES
        self.curr_image_index = 0
        self.curr_image = self.curr_image_type[0][self.curr_image_index]

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

        # TODO: fix impact weight health scaling by a bit

        impact_velo = self.velocity.length()
        self.collision_recoil_frames_left = round(impact_velo * self.COLLISION_FRAMES_M)
        self.collision_cooldown_frames_left = self.COLLISION_COOLDOWN_FRAMES + self.collision_recoil_frames_left

        # invert velocity, reduce acceleration
        self.velocity *= -self.COLLISION_RECOIL_W
        self.acceleration *= self.COLLISION_RECOIL_W

        # if the object we crashed into is below is, "reset" the compounding gravity effect
        if (self.velocity.y < 0):
            self.cumulative_grav_c  *= 0.01
        else:
            self.cumulative_grav_c  *= 0.2

        # calculate health loss based on velocity and the set weights
        health_loss: float
        if (impact_velo >= self.THRUST_MAGNITUDE):
            health_loss = self.MAX_COLL_HP_LOSS
        else:
            loss_weight = (impact_velo / self.THRUST_MAGNITUDE)
            health_loss = lerp(self.MIN_COLL_HP_LOSS, self.MAX_COLL_HP_LOSS, loss_weight)

        # end any thrust end frames that might be active
        self.thrust_end_frames_left = 0

        # reset thrust phase if currently in a thrust phase

        # print(f'health_loss={health_loss}')
        self.health -= health_loss
        if (self.health <= 0.0):
            return None

        if (self.key_thrusting):
            self.init_phase_thrust_begin()

        self.set_special_image_type(self.SHIELD_IMAGES)
        return self.collision_cooldown_frames_left

    def init_phase_thrust_begin(self):
        ''' call to begin thrust phase, gradually increasing acceleration and its limit
            * uses the current acceleration to calculate the needed frames
            * phase intent: smooth transition from normal to thrust acceleration
        '''
        self.key_thrusting = True
        self.thrust_begin_curr_lerp_weight = 0.0

        # calculate the frames appropriate to scale up to max thrust acceleration,
        # depending on the current acceleration and set thrust begin frames

        self.thrust_begin_accel_length = self.acceleration.length()
        weighted_diff = (self.THRUST_MAGNITUDE - self.thrust_begin_accel_length) / 1.0
        self.thrust_begin_frames_left = int(self.THRUST_BEGIN_FRAMES_M * weighted_diff)

        if (self.thrust_begin_frames_left == 0):
            self.thrust_begin_frames_left = int(1)
        self.thrust_begin_lerp_increase = 1.0 / self.thrust_begin_frames_left

        self.set_special_image_type(self.THRUST_A_IMAGES)

        # if (self.PHASE_DEBUG_PRINT):
        #     print(f'thrust_begin_lerp_increase={self.thrust_begin_lerp_increase}')
        #     print(f'self.thrust_begin_frames_left: {self.thrust_begin_frames_left}')

    def init_phase_thrust_end(self):
        ''' call to end thrust phase, starting transition to normal acceleration limits
            * phase intent: smooth transition from thrust to normal acceleration
        '''
        self.key_thrusting = False
        self.thrust_begin_frames_left = 0
        # set transition frames and the lerp weight to their max
        self.thrust_end_frames_left = self.THRUST_END_FRAMES
        self.thrust_end_curr_lerp_weight = 1.0
        self.temp_max_accel = self.acceleration.length()
        self.set_special_image_type(self.THRUST_C_IMAGES)

    def set_velocity_with_gravity(self, multiplier):
        self.velocity.update(self.acceleration)

        # update velocity. apply the current gravity effect.
        self.velocity.y += (multiplier * self.cumulative_grav_c)

    def apply_thrust_begin_frame(self):
        ''' gradually increase to thrust acceleration over the set frames '''
        self.thrust_begin_frames_left -= 1

        # reduce max acceleration gradually over the set frames
        self.acceleration += (self.key_direction * self.THRUST_HANDLING_M)

        # use linear interpolation to find the right value for current max acceleration
        # finds the point which is a certain percent of fps closer to max thrust accel
        new_accel = lerp(self.thrust_begin_accel_length, self.THRUST_MAGNITUDE, (self.thrust_begin_curr_lerp_weight))
        self.thrust_begin_curr_lerp_weight += self.thrust_begin_lerp_increase

        # if (self.PHASE_DEBUG_PRINT):
        #     if (self.thrust_begin_frames_left < 5):
        #         print(f'thrust_begin_frames_left={self.thrust_begin_frames_left}; new_accel={new_accel}')
        #         print(f'thrust_begin_curr_lerp_weight={self.thrust_begin_curr_lerp_weight}')
        #         if (self.thrust_begin_frames_left == 0):
        #             print(f'[thrust_begin_summary] start: {self.thrust_begin_accel_length}; now={new_accel}')

        # scale up acceleration
        self.acceleration.scale_to_length(new_accel)

        # apply gravity
        self.cumulative_grav_c *= 0.99

        # update velocity. apply the current gravity effect.
        self.set_velocity_with_gravity(0.75)

        if (self.thrust_begin_frames_left == 0):
            self.set_special_image_type(self.THRUST_B_IMAGES)

    def thrust_frame(self):
        ''' applies acceleration directly to velocity at increased handling and force.'''
        self.acceleration += (self.key_direction * self.THRUST_HANDLING_M)
        self.acceleration.scale_to_length(self.THRUST_MAGNITUDE)
        self.cumulative_grav_c *= 0.98
        self.set_velocity_with_gravity(0.4)

    def apply_thrust_end_frame(self):
        ''' gradually reduce the max acceleration. apply gravity. 
            * intent: smooth acceleration from thrust level to normal
        '''
        self.thrust_end_frames_left -= 1

        # reduce max acceleration gradually over the set frames
        self.acceleration += (self.key_direction * self.HANDLING)

        # use linear interpolation to find the right value for current max acceleration
        # finds the point which is a certain percent of fps closer to regular max accel
        self.temp_max_accel = lerp(self.MAX_ACCEL, self.THRUST_MAGNITUDE, (self.thrust_end_curr_lerp_weight))
        self.acceleration.clamp_magnitude_ip(0.1, self.temp_max_accel)
        self.thrust_end_curr_lerp_weight -= self.THRUST_END_LERP_DECREASE

        # increase compounding gravity
        self.cumulative_grav_c += self.GRAV_C
        self.set_velocity_with_gravity(0.9)

        if (self.thrust_end_frames_left == 0):
            self.set_idle_image_type()

    def default_frame(self):
        ''' update acceleration, velocity and compounding gravity '''
        self.acceleration += (self.key_direction * self.HANDLING)
        self.acceleration.update(
            pg_math.clamp(self.acceleration.x, -self.MAX_ACCEL, self.MAX_ACCEL),
            pg_math.clamp(self.acceleration.y, -self.MAX_ACCEL, self.MAX_ACCEL)
        )
        self.cumulative_grav_c += self.GRAV_C

        self.set_velocity_with_gravity(1.0)

    def update_image(self):
        ''' update self.image, transforming it to the current angle. Recreate self .rect, .mask. '''

        # get a new image by rotating the original image
        self.image = transform.rotate(self.curr_image, -self.angle)

        # get new mask for collision checking purposes
        #   > "A new mask needs to be recreated each time a sprite's image is changed  
        #   > (e.g. if a new image is used or the existing image is rotated)."
        #   https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.collide_mask  
        self.mask = mask.from_surface(self.image)

        # set rect to the new images rect bounds. used for blitting through group draw
        self.rect = self.image.get_rect(center=self.position)

    def update(self):
        # note: map handles collision cooldown frames
        if (self.collision_recoil_frames_left):
            self.collision_recoil_frames_left -= 1
            # essentially; block any other events during collision recoil
        elif (self.key_thrusting) and (self.fuel > 0.0):
            # use some fuel
            self.fuel -= self.FUEL_CONSUMPTION
            if (self.thrust_begin_frames_left):
                self.apply_thrust_begin_frame()
            else:
                self.thrust_frame()
        elif (self.thrust_end_frames_left):
            self.apply_thrust_end_frame()
        else:
            self.default_frame()

        self.position += self.velocity
        # update image, position and rect position
        self.angle = self.VEC_CENTER.angle_to(self.acceleration)
        self.update_image()

    def init_death_event(self):
        self.fuel = 0.0
        self.velocity.y = (self.MAX_VELO * 1.5)
        self.thrust_begin_frames_left = 0
        self.thrust_end_frames_left = 0
        self.key_thrusting = False
        self.collision_recoil_frames_left = 100000
        self.collision_cooldown_frames_left = 100000
        self.set_special_image_type(self.DESTROYED_IMAGES) 

    #### FORMATTED STRING GETTERS ####

    def get_str_dir_x(self):
        return f'{self.key_direction.x():.2f}'

    def get_str_dir_y(self):
        return f'{self.key_direction.y():.2f}'

    def get_str_angle(self):
        return f'{self.angle():.1f}'

    #### ORDINARY GETTERS ####

    def get_collision_cooldown_frames_left(self):
        return self.collision_cooldown_frames_left

    def get_curr_health(self):
        return self.health

    def get_curr_fuel(self):
        return self.fuel


''' DEPRECATED METHODS + RELEVANT IMPORTS
    # from pygame.gfxdraw import aapolygon as gfxdraw_aapolygon, aatrigon as gfxdraw_aatrigon
    # from pygame.transform import scale
    from pygame import Color, image, Rect, SRCALPHA
    from pygame.draw import polygon as draw_polygon

    def set_up_polygon_image(self, color: Color):
        #### get the the original image used for later transformation
        #### * ensures the original image is rotated, not the rotated one.
        ####     if this is not done, two things will happen:
        ####     1) The image will become larger after each rotation at an exponential rate
        ####        this will cause the program to crash when the image takes up too much memory.
        ####     2) The image quality will deteriorate after each rotation
        ####

        # create a surface
        SURF = Surface((self.IMAGE_WIDTH, self.IMAGE_HEIGHT)).convert_alpha()

        # fill the surface with transparent pixels
        SURF.fill(Color(0, 0, 0, 0))

        # create a polygon using the surface bounds as reference points
        SURF_RECT = SURF.get_rect()
        p1 = SURF_RECT.midtop
        p2 = SURF_RECT.bottomright
        p3 = SURF_RECT.bottomleft
        draw_polygon(SURF, Color(color), (p1, p2, p3))

        # rotating to -90 means there's no need to flip later. (pg inverted y-axis)
        IMG = transform.rotate(SURF, -90.0)
        return IMG
'''