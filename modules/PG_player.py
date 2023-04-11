from pygame import Color, Surface, transform, mask, image, Rect, SRCALPHA, math as pg_math
from pygame.transform import scale
from pygame.math import Vector2 as Vec2, lerp
from pygame.sprite import Sprite
from pygame.draw import polygon as draw_polygon
# from pygame.gfxdraw import aapolygon as gfxdraw_aapolygon, aatrigon as gfxdraw_aatrigon

from .PG_common import load_sprites


class Player(Sprite):
    def __init__(self, cf_player: dict, cf_map: dict, cf_global: dict, spawn_pos: tuple[int, int]):
        # initalize as pygame sprite
        Sprite.__init__(self)

        #### NESTED DICTS ####
        # note that these are not stored in self, and are only read during init
        cf_surface:  dict = cf_player['surface']
        cf_physics:  dict = cf_player['physics']
        cf_gameplay: dict = cf_player['gameplay']
        cf_phases:   dict = cf_player['phase_durations']

        #### CONSTANTS ####
        self.SPAWN_POS          = spawn_pos
        self.FPS                = int(cf_global['fps_limit'])
        ''' global fps limit '''
        self.MAP_GRAV_C         = float(cf_map['gravity_c'])
        ''' map gravity constant '''
        self.MAP_GRAV_W         = float(cf_map['gravity_w'])
        ''' map gravity multiplier '''
        self.FUEL_CONSUMPTION   = float(cf_map['player_fuel_consumption'])

        # surface settings
        self.IMAGE_WIDTH        = int(cf_surface['width'])
        self.IMAGE_HEIGHT       = int(cf_surface['height'])
        # gameplay
        self.MAX_HEALTH         = float(cf_gameplay['max_health'])
        self.MAX_FUEL           = float(cf_gameplay['max_fuel'])
        self.MIN_COLL_HP_LOSS   = float(cf_gameplay['min_collision_health_loss'])
        self.MAX_COLL_HP_LOSS   = float(cf_gameplay['max_collision_health_loss'])

        # acceleration
        self.MAX_ACCEL          = float(cf_physics['max_acceleration'])
        self.THRUST_MAGNITUDE   = float(cf_physics['thrust_magnitude'])
        # velocity
        self.MAX_VELO           = float(cf_physics['max_velocity'])
        self.TERMINAL_VELO      = float(cf_physics['terminal_velocity'])
        # steering
        self.HANDLING           = float(cf_physics['handling'])
        self.THRUST_HANDLING_M  = float(cf_physics['thrust_handling_m'] * self.HANDLING)
        self.COLLISION_RECOIL_W = float(cf_physics['collision_recoil_w'])
        ''' how drastic the recoil of collision will be '''

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
        self.MASS = float(cf_physics['mass'])
        ''' multiplier used when applying gravity to velocity '''
        self.VEC_CENTER  = Vec2(0.0, 0.0)
        ''' used for relative angle calculation '''
        
        self.cf_spritesheets: dict = cf_surface['spritesheets']

        # if not self.cf_spritesheets:
        #     self.IDLE_IMAGES = self.set_up_polygon_image(cf_surface['colors']['default'])
        # else:
        self.set_up_sprite_images()

        # initialize all attributes through the reset function
        self.reset_all_attributes()

        # initialize image, rect and mask through the update function
        self.update_image()

        self.PHASE_DEBUG_PRINT = False

    def set_up_sprite_images(self):
        scalar = self.cf_spritesheets['image_scalar']

        cf_idle: dict = self.cf_spritesheets['idle']
        cf_shield: dict = self.cf_spritesheets['shield']
        cf_destroyed: dict = self.cf_spritesheets['destroyed']
        cf_thrust_a: dict = self.cf_spritesheets['thrust_a']
        cf_thrust_b: dict = self.cf_spritesheets['thrust_b']
        cf_thrust_c: dict = self.cf_spritesheets['thrust_c']

        _N_IDLE_IMAGES = int(cf_idle['n_images'])
        _N_SHIELD_IMAGES = int(cf_shield['n_images'])
        _N_DESTROYED_IMAGES = int(cf_destroyed['n_images'])
        _N_THRUST_A_IMAGES = int(cf_thrust_a['n_images'])
        _N_THRUST_B_IMAGES = int(cf_thrust_b['n_images'])
        _N_THRUST_C_IMAGES = int(cf_thrust_c['n_images'])

        _IDLE_IMAGES = load_sprites(cf_idle['path'], _N_IDLE_IMAGES, scalar)
        _SHIELD_IMAGES = load_sprites(cf_shield['path'], _N_SHIELD_IMAGES, scalar)
        _DESTROYED_IMAGES = load_sprites(cf_destroyed['path'], _N_DESTROYED_IMAGES, scalar)
        _THRUST_A_IMAGES = load_sprites(cf_thrust_a['path'], _N_THRUST_A_IMAGES, scalar)
        _THRUST_B_IMAGES = load_sprites(cf_thrust_b['path'], _N_THRUST_B_IMAGES, scalar)
        _THRUST_C_IMAGES = load_sprites(cf_thrust_c['path'], _N_THRUST_C_IMAGES, scalar)

        # store the tuples nested in tuples, along with the max allowed index
        self.IDLE_IMAGES        = (_IDLE_IMAGES, int(_N_IDLE_IMAGES - 1))
        self.SHIELD_IMAGES      = (_SHIELD_IMAGES, int(_N_SHIELD_IMAGES - 1))
        self.DESTROYED_IMAGES   = (_DESTROYED_IMAGES, int(_N_DESTROYED_IMAGES - 1))
        self.THRUST_A_IMAGES    = (_THRUST_A_IMAGES, int(_N_THRUST_A_IMAGES - 1))
        self.THRUST_B_IMAGES    = (_THRUST_B_IMAGES, int(_N_THRUST_B_IMAGES - 1))
        self.THRUST_C_IMAGES    = (_THRUST_C_IMAGES, int(_N_THRUST_C_IMAGES - 1))

        self.special_image_set = False
        self.curr_image_index = 0
        self.curr_image_type: tuple[tuple[Surface, ...], int] = self.IDLE_IMAGES
        self.curr_image: Surface = self.curr_image_type[0][self.curr_image_index]

    def cycle_active_image(self):
        if (self.curr_image_index >= self.curr_image_type[1]):
            self.curr_image_index = 0
        else:
            self.curr_image_index += 1
        self.curr_image = self.curr_image_type[0][self.curr_image_index]

    def set_special_image_type(self, image_type: tuple[tuple[Surface, ...], int]):
        self.curr_image_type = image_type
        self.special_image_set = True
        self.cycle_active_image()

    def set_idle_image_type(self):
        self.special_image_set = False
        self.curr_image_index = 0
        self.curr_image_type = self.IDLE_IMAGES
        self.curr_image = self.curr_image_type[0][self.curr_image_index]

    def reset_all_attributes(self):
        ''' reset (or set) all attributes used across all methods '''
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
        self.grav_force:     float = 0.0
        ''' accumulation of gravity '''
        self.temp_max_accel: float = 0.0
        ''' temporary max acceleration '''

        self.health = self.MAX_HEALTH
        self.fuel   = self.MAX_FUEL
        self.set_idle_image_type()

    def set_up_polygon_image(self, color: Color):
        ''' get the the original image used for later transformation
            * ensures the original image is rotated, not the rotated one.
                if this is not done, two things will happen:
                1) The image will become larger after each rotation at an exponential rate
                   this will cause the program to crash when the image takes up too much memory.
                2) The image quality will deteriorate after each rotation
        '''
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
        # scale recoil frames to how fast the sprite was going
        # if (self.velocity.y > 0):
        #     grav_w = self.grav_force / self.TERMINAL_VELO
        #     reduct_w = lerp(self.velocity.y, self.MAX_VELO, grav_w)
        #     self.velocity.y *= reduct_w
        # print(f'grav_force: {self.grav_force}')
        # print(f'velocity.y: {self.velocity.y}')
        impact_velo = self.velocity.length()
        # print(f'impact_velo: {impact_velo}')
        self.collision_recoil_frames_left = round(impact_velo * self.COLLISION_FRAMES_M)
        self.collision_cooldown_frames_left = self.COLLISION_COOLDOWN_FRAMES + self.collision_recoil_frames_left

        # invert velocity, reduce acceleration
        self.velocity *= -self.COLLISION_RECOIL_W
        self.acceleration *= self.COLLISION_RECOIL_W

        # if the object we crashed into is below is, "reset" the compounding gravity effect
        if (self.velocity.y < 0):
            self.grav_force *= 0.01
        else:
            self.grav_force *= 0.8

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
        self.grav_force *= 0.99

        # update velocity. apply the current gravity effect.
        self.velocity.update(self.acceleration)
        self.velocity.y += (self.MASS * self.grav_force)

        if (self.thrust_begin_frames_left == 0):
            self.set_special_image_type(self.THRUST_B_IMAGES)

    def thrust_frame(self):
        ''' applies acceleration directly to velocity at increased handling and force.'''
        self.acceleration += (self.key_direction * self.THRUST_HANDLING_M)
        self.acceleration.scale_to_length(self.THRUST_MAGNITUDE)
        self.grav_force *= 0.99
        self.velocity.update(self.acceleration)
        self.velocity.y += (self.MASS * self.grav_force)
        # self.velocity.y = pg_math.clamp(self.velocity.y, -self.MAX_VELO, self.TERMINAL_VELO)

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
        self.grav_force = lerp((self.grav_force + self.MAP_GRAV_C), self.TERMINAL_VELO, self.MAP_GRAV_W)

        # update velocity. apply the current gravity effect.
        self.velocity.update(self.acceleration)
        self.velocity.y += (self.MASS * self.grav_force)
        
        if (self.thrust_end_frames_left == 0):
            self.set_idle_image_type()


    def default_frame(self):
        ''' update acceleration, velocity and compounding gravity '''
        self.acceleration += (self.key_direction * self.HANDLING)
        self.acceleration.update(
            pg_math.clamp(self.acceleration.x, -self.MAX_ACCEL, self.MAX_ACCEL),
            pg_math.clamp(self.acceleration.y, -self.MAX_ACCEL, self.MAX_ACCEL)
        )
        # self.acceleration *= self.ACCEL_FALLOFF

        # increase compounding gravity and add constant
        self.grav_force = lerp(self.grav_force, self.TERMINAL_VELO, self.MAP_GRAV_W) + self.MAP_GRAV_C

        # update velocity. apply the current gravity effect.
        self.velocity.update(self.acceleration)
        self.velocity.y += (self.MASS * self.grav_force)

        if (self.key_direction.y == -1.0) and (self.grav_force >= self.TERMINAL_VELO):
            # this is not a great solution, but, it *almost* completely counteracts upwards accel without thrust
            # TODO: TEST WITH A VARIETY OF MASS; or find a better solution
            self.velocity.y -= (0.2 * self.grav_force) * (self.acceleration.y / self.MASS)

    def update_image(self):
        ''' update self.image, transforming it to the current angle. Update self .rect, .mask. '''

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

    #### FORMATTED STRING GETTERS ####

    def get_str_dir_x(self):
        return f'{self.key_direction.x():.2f}'

    def get_str_dir_y(self):
        return f'{self.key_direction.y():.2f}'

    def get_str_angle(self):
        return f'{self.angle():.1f}'

    def get_str_gravity(self):
        return f'{self.grav_force():.3f}'

    #### ORDINARY GETTERS ####

    def get_collision_cooldown_frames_left(self):
        return self.collision_cooldown_frames_left

    def get_curr_health(self):
        return self.health

    def get_curr_fuel(self):
        return self.fuel

    def get_max_grav_effect(self):
        return self.TERMINAL_VELO

    def get_grav_effect(self):
        return self.grav_force


''' TODO

* visualizing information:
    - animate thrust -> 
    - 
'''
