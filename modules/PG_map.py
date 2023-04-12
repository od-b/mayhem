from random import randint
from typing import Callable

# installed library imports
import pygame as pg
from pygame import Color, Surface, Rect, display
from pygame.math import Vector2 as Vec2
from pygame.draw import line as draw_line, lines as draw_lines, rect as draw_rect
from pygame.sprite import Sprite, Group, GroupSingle, spritecollide, spritecollideany, collide_mask
from pygame.mask import Mask

# from pygame.image import save as image_save
# image_save(self.surface, "screenshot.png")

## general classes
from .exceptions import ConfigError, LoopError
## pygame specific classes
from .PG_timer import PG_Timer
from .PG_block import Block
from .PG_player import Player
from .PG_coin import Coin
from .PG_ui_containers import UI_Sprite_Container
from .PG_ui_bar import UI_Auto_Icon_Bar_Horizontal
from .PG_common import partition_spritesheet


DEBUG_PLAYER_VISUALS = False
DEBUG_CHEAT_MODE = True

class PG_Map:
    def __init__(self, cf_global: dict, cf_map: dict, timer: PG_Timer, surface: Surface):
        self.cf_global  = cf_global
        self.cf_map     = cf_map
        self.surface    = surface
        ''' map-designated display subsurface '''
        self.timer      = timer
        ''' reference to the app timer '''

        ### CONSTANTS ####
        self.cf_game_sprites: dict  = cf_map['game_sprites']
        self.cf_ui_sprites: dict    = cf_map['ui_sprites']

        self.cf_player: dict        = self.cf_game_sprites['player']
        self.cf_blocks: dict        = self.cf_game_sprites['blocks']
        self.cf_ui_containers: dict = self.cf_ui_sprites['containers']
        self.cf_ui_bars: dict       = self.cf_ui_sprites['bars']

        # globals
        self.LOOP_LIMIT      = int(self.cf_global['loop_limit'])
        self.DEBUG_COLOR     = Color(self.cf_global['debug_color'])
        self.DEBUG_COLOR_2   = Color(self.cf_global['debug_color_2'])

        # from cf_map settings
        self.name            = str(cf_map['name'])
        self.rect            = self.surface.get_rect()
        self.fill_color      = Color(cf_map['fill_color'])
        self.overlap_color   = Color(cf_map['overlap_color'])
        self.N_OBSTACLES     = int(cf_map['n_obstacles'])
        self.N_COINS         = int(cf_map['n_coins'])

        #### SPRITE GROUPS & LISTS ####
        # groups for setup / spawn purposes
        self.obstacle_block_group = Group()
        ''' group specifically containing the randomly placed obstacle core blocks '''
        self.map_edge_block_group = Group()
        ''' group specifically containing the map surface outline blocks '''
        self.terrain_group = Group()
        ''' blocks and potentially other terrain sprites '''
        self.spawn_collide_group = Group()
        ''' group used as a combined no-go spawn position for various sprites '''

        # main groups
        self.player_group = GroupSingle()
        ''' player sprite group. If a new sprite is added, the old is removed. '''
        self.block_group = Group()
        ''' combined group of constant, map-anchored rectangular sprites '''
        self.coin_group = Group()
        self.ui_container_group = Group()
    
        # create a list to hold all created bars. can be needed for search after .kill()
        self.UI_STATUS_BARS: list[UI_Auto_Icon_Bar_Horizontal] = []
        
        #### VARIABLES ####
        self.collected_coins = []
        self.looping   = False
        self.paused    = False
        self.completed = False
        self.quit_called = False

    #### NON-RECURRING SETUP METHODS // HELPER FUNCTIONS ####

    def set_up_all(self, start_loop: bool):
        ''' bundle of function calls to set up the map '''
        self.set_update_intervals()
        self.store_player_controls()
        self.set_up_ui_containers()

        # sprite creation
        self.spawn_terrain_blocks()
        self.spawn_coins()
        self.spawn_player()

        # UI creation
        self.create_all_ui_bars()

        if (start_loop):
            self.looping = True
            self.timer.new_segment(self.name, False)

    def set_up_ui_containers(self):
        # set up bar container
        cf_bar_container = self.cf_ui_containers['bar_container']
        self.BAR_CONTAINER = UI_Sprite_Container(
            cf_bar_container['cf_bg'],
            cf_bar_container['position'],
            cf_bar_container['size'],
            cf_bar_container['child_anchor'],
            cf_bar_container['child_anchor_offset_x'],
            cf_bar_container['child_anchor_offset_y'],
            cf_bar_container['child_align_x'],
            cf_bar_container['child_align_y'],
            cf_bar_container['child_padding_x'],
            cf_bar_container['child_padding_y'],
        )
        self.ui_container_group.add(self.BAR_CONTAINER)
        # prevent coins & player from spawning below the bars:
        self.spawn_collide_group.add(self.BAR_CONTAINER)

    def set_update_intervals(self):
        self.EVENT_UPDATE_TERRAIN = self.timer.create_event_timer(self.cf_map['upd_intervals']['terrain'], 0)
        ''' custom pygame event call to update terrain '''
        self.EVENT_PLAYER_IMG_CYCLE = self.timer.create_event_timer(self.cf_map['upd_intervals']['player_img_cycle'], 0)
        # self.EVENT_COIN_IMG_CYCLE = self.timer.create_event_timer(self.cf_map['upd_intervals']['coin_img_cycle'], 0)

    def store_player_controls(self) -> dict[str, int]:
        self.STEER_UP    = int(self.cf_player['controls']['steer_up'])
        self.STEER_LEFT  = int(self.cf_player['controls']['steer_left'])
        self.STEER_DOWN  = int(self.cf_player['controls']['steer_down'])
        self.STEER_RIGHT = int(self.cf_player['controls']['steer_right'])
        self.THRUST      = int(self.cf_player['controls']['thrust'])

    def spawn_terrain_blocks(self):
        ''' specialized function for the creating the map terrain '''

        # outline the entire game bounds with terrain_blocks:
        terrain_facing = -1
        self.spawn_outline_blocks(
            self.cf_blocks['edge_outline'],
            self.map_edge_block_group, self.rect, terrain_facing, None
        )
        # add map bounds outline blocks to the general map group
        self.block_group.add(self.map_edge_block_group)

        # place obstacle_blocks within the game area
        self.spawn_obstacle_blocks(self.cf_blocks['obstacle'], self.obstacle_block_group)

        # outline the obstacles with smaller rects to create more jagged terrain
        terrain_facing = 1
        for OBSTACLE_BLOCK in self.obstacle_block_group:
            # for each block in obstacle_block_group, outline the block rect
            alt_pallette = [OBSTACLE_BLOCK.color]
            self.spawn_outline_blocks(
                self.cf_blocks['obstacle_outline'],
                self.obstacle_block_group, 
                OBSTACLE_BLOCK.rect, 
                terrain_facing,
                alt_pallette
            )

        # add obstacle blocks and their outline blocks to the general map group
        self.block_group.add(self.obstacle_block_group)
        self.terrain_group.add(self.block_group)
        self.spawn_collide_group.add(self.block_group)

    def spawn_outline_blocks(self, cf_block: dict, group: Group, bounds: Rect,
                              facing: int, alt_pallette: None | list[Color]):

        ''' encapsulate the given rects' bounds with blocks
            * if alt_pallette is None, the block will use the cf_block color list at random
            * otherwise, choose the given color pallette for all blocks

            * facing decides the alignment of the blocks relative to the bounds axis':
            * -1 => inwards
            * 0  => center
            * 1  => outwards
        '''
        
        if (alt_pallette):
            color_pool = alt_pallette
        else:
            color_pool = cf_block['color_pool']

        # constant declarations for readability
        MIN_X = bounds.left
        MAX_X = bounds.right
        MIN_Y = bounds.top
        MAX_Y = bounds.bottom
        PADDING = int(cf_block['padding'])

        # below are four loops that together will outline the entire bounds
        # the loop places blocks in a clockwise path, following each axis
        # until a new bound is encountered, then swapping axis' and continuing
        # the first loop is explicit and commented, while the last three
        # are not, and are also slightly condensed. The logic is allround similar.
        # (they are way too specific to create a working generalized loop function, however)

        # last_block is for storing the last block placed when swapping axis'
        last_block: Block | None = None

        # 1) topleft --> topright
        curr_pos_x = MIN_X
        while curr_pos_x < MAX_X:
            # set random height/width from within the ranges
            width = randint(cf_block['min_width'], cf_block['max_width'])
            height = randint(cf_block['min_height'], cf_block['max_height'])

            # create a tuple to contain the position of the block
            position = (curr_pos_x, int(0))

            # ensure no edge overlap by checking for the last block:
            if (curr_pos_x + width) > MAX_X:
                # if the block will be last, adjust size before creating
                width = (MAX_X - curr_pos_x)

            # assemble the block
            BLOCK = Block(cf_block, self.cf_global, color_pool, (width, height),
                          position, int(self.cf_map['upd_intervals']['terrain']))

            # adjust position according to facing
            match (facing):
                case (-1):
                    BLOCK.rect.top = MIN_Y
                case (0):
                    BLOCK.rect.centery = MIN_Y
                case (1):
                    BLOCK.rect.bottom = MIN_Y

            # add to the given group and update last block
            group.add(BLOCK)
            last_block = BLOCK

            # increment position for placing the next block
            curr_pos_x = (BLOCK.rect.right + PADDING)

        # 2) topright --> bottomright
        curr_pos_y = last_block.rect.bottom
        while curr_pos_y < MAX_Y:
            width = randint(cf_block['min_width'], cf_block['max_width'])
            height = randint(cf_block['min_height'], cf_block['max_height'])
            position = (int(0), curr_pos_y)
            if (curr_pos_y + height) > MAX_Y:
                height = MAX_Y - curr_pos_y

            BLOCK = Block(cf_block, self.cf_global, color_pool, (width, height),
                          position, int(self.cf_map['upd_intervals']['terrain']))

            match (facing):
                case (-1):
                    BLOCK.rect.right = MAX_X
                case (0):
                    BLOCK.rect.centerx = MAX_X
                case (1):
                    BLOCK.rect.left = MAX_X
            last_block = BLOCK
            group.add(BLOCK)
            curr_pos_y = (BLOCK.rect.bottom + PADDING)

        # 3) bottomright --> bottomleft
        curr_pos_x = last_block.rect.left
        while curr_pos_x > MIN_X:
            width = randint(cf_block['min_width'], cf_block['max_width'])
            height = randint(cf_block['min_height'], cf_block['max_height'])
            position = (int(0), int(0))
            if (curr_pos_x - width) < MIN_X:
                width = abs(MIN_X - curr_pos_x)

            BLOCK = Block(cf_block, self.cf_global, color_pool, (width, height),
                          position, int(self.cf_map['upd_intervals']['terrain']))
            BLOCK.rect.right = curr_pos_x

            match (facing):
                case (-1):
                    BLOCK.rect.bottom = MAX_Y
                case (0):
                    BLOCK.rect.centery = MAX_Y
                case (1):
                    BLOCK.rect.top = MAX_Y
            last_block = BLOCK
            group.add(BLOCK)
            curr_pos_x = (BLOCK.rect.left - PADDING)

        # 4) bottomleft --> topright
        curr_pos_y = last_block.rect.top
        while curr_pos_y > MIN_Y:
            width = randint(cf_block['min_width'], cf_block['max_width'])
            height = randint(cf_block['min_height'], cf_block['max_height'])
            position = (int(0), int(0))
            if (curr_pos_y - height) < MIN_Y:
                height = abs(MIN_Y - curr_pos_y)

            BLOCK = Block(cf_block, self.cf_global, color_pool, (width, height),
                          position, int(self.cf_map['upd_intervals']['terrain']))
            BLOCK.rect.bottom = curr_pos_y

            match (facing):
                case (-1):
                    BLOCK.rect.left = MIN_X
                case (0):
                    BLOCK.rect.centerx = MIN_X
                case (1):
                    BLOCK.rect.right = MIN_X
            last_block = BLOCK
            group.add(BLOCK)
            curr_pos_y = (BLOCK.rect.top - PADDING)

    def spawn_obstacle_blocks(self, cf_block: dict, group: Group):
        ''' specialized obstacle spawning algorithm
            * checks for collision with the passed group and self.block_group before placing
        '''

        # padding, taking into account the player size to not completely block paths:
        H_PADDING = int(self.cf_player['surface']['height'] + cf_block['padding'])
        W_PADDING = int(self.cf_player['surface']['width'] + cf_block['padding'])
        color_pool = cf_block['color_pool']

        # initiate the loop
        placed_blocks = 0
        failed_attempts = 0
        while placed_blocks < self.N_OBSTACLES:
            # set random height/width from within the ranges
            width = randint(cf_block['min_width'], cf_block['max_width'])
            height = randint(cf_block['min_height'], cf_block['max_height'])

            # get a random position within the map
            position = self.get_rand_pos(width, height)

            # assemble the block
            BLOCK = Block(cf_block, self.cf_global, color_pool, (width, height),
                          position, int(self.cf_map['upd_intervals']['terrain']))

            # the block is now created, but there's 2 potential problems:
            # 1) the block might overlap other blocks
            # 2) we don't want to lock the player in by bad rng

            # solution: create a copy of the rect and inflate it using the player size + set padding
            inflated_rect = BLOCK.rect.copy().inflate(W_PADDING, H_PADDING)

            # temporarily swap the rect with the one of the block, while saving the original
            # this is to allow for easy and fast spritecollide checking
            original_rect = BLOCK.rect.copy()
            BLOCK.rect = inflated_rect

            # if the block + player rect doesn't collide with any terrain, add it to the group
            if not (spritecollideany(BLOCK, self.block_group) or (spritecollideany(BLOCK, group))):
                # block doesn't collide with anything, swap rect back and add block
                BLOCK.rect = original_rect
                group.add(BLOCK)
                placed_blocks += 1
            else:
                # otherwise, delete the sprite and try again
                del BLOCK
                failed_attempts += 1
                # check if attempt limit is reached
                if (failed_attempts > self.LOOP_LIMIT):
                    msg = f'\
                        Fail limit of {self.LOOP_LIMIT} attempts reached.\
                        Too many or too large obstacles.\n\
                        block padding set too high can also be the cause.\
                        Current obstacle count: {placed_blocks} / {self.N_OBSTACLES}'
                    raise ConfigError(msg, cf_block)

            # make sure the copied temp rect is not saved in memory
            del inflated_rect

    def spawn_player(self):
        ''' create and spawn the player sprite '''
        player_width = int(self.cf_player['surface']['width'])
        player_height = int(self.cf_player['surface']['height'])
        tmp_rect = Rect((0, 0), (player_width, player_height))
        spawn_pos = self.get_rand_pos_no_collide(tmp_rect, player_width, player_height, self.spawn_collide_group)
        del tmp_rect

        # create the player sprite, then update player_group
        self.player = Player(self.cf_player, self.cf_map, self.cf_global, spawn_pos)
        self.player_group.add(self.player)

    def create_all_ui_bars(self):
        HEALTH_BAR = UI_Auto_Icon_Bar_Horizontal(
            self.cf_ui_bars['player_status']['health'],
            self.cf_global,
            (0, 0),
            float(self.player.MAX_HEALTH),
            self.player.get_curr_health,
        )
        FUEL_BAR = UI_Auto_Icon_Bar_Horizontal(
            self.cf_ui_bars['player_status']['fuel'],
            self.cf_global,
            (0, 0),
            float(self.player.MAX_FUEL),
            self.player.get_curr_fuel,
        )
        GHOST_BAR = UI_Auto_Icon_Bar_Horizontal(
            self.cf_ui_bars['player_status']['ghost'],
            self.cf_global,
            (0, 0),
            0.0,
            self.player.get_collision_cooldown_frames_left,
        )
        SHIELD_BAR = UI_Auto_Icon_Bar_Horizontal(
            self.cf_ui_bars['player_status']['shield'],
            self.cf_global,
            (0, 0),
            0.0,
            self.player.get_collision_cooldown_frames_left,
        )
        self.UI_STATUS_BARS.extend([HEALTH_BAR, FUEL_BAR, GHOST_BAR, SHIELD_BAR])

        # auto add all const bars
        self.BAR_CONTAINER.add_children_by_ref_id("CONST", self.UI_STATUS_BARS)

    def spawn_coins(self):
        ''' create and position the coin sprite various places around the screen '''
        cf_coin = self.cf_game_sprites['coin']

        spritesheet_path = cf_coin['spritesheet_path']
        spritesheet_variants = int(cf_coin['image_variants'])
        scalar = float(cf_coin['image_scalar'])

        # all the coins share a single tuple containing their images
        COIN_SPRITESHEET_IMG = pg.image.load(spritesheet_path)
        IMAGES = partition_spritesheet(COIN_SPRITESHEET_IMG, spritesheet_variants, scalar)

        # place the coins according to settings
        min_offset = int(self.cf_map['min_coin_offset'])
        min_spread = int(self.cf_map['min_coin_spread'])
        
        COIN_RECT = IMAGES[0].get_rect()

        # create two rects for placement collision purposes
        offset_rect = COIN_RECT.copy().inflate(min_offset, min_offset)
        spread_rect = COIN_RECT.copy().inflate(min_spread, min_spread)

        # coin positioning procedure
        placed_coins = 0
        failed_attempts = 0
        while (placed_coins != self.N_COINS):
            rand_pos = self.get_rand_pos(min_offset, min_offset)
            offset_rect.center = rand_pos
            spread_rect.center = rand_pos

            terrain_collision = False
            coin_collision = False

            # check terrain collision
            for obj in self.spawn_collide_group:
                if (offset_rect.colliderect(obj.rect)):
                    terrain_collision = True
                    break

            # check coin collision if terrain collision is ok
            if not (terrain_collision):
                for coin in self.coin_group:
                    if (spread_rect.colliderect(coin.rect)):
                        coin_collision = True
                        break

                if not (coin_collision):
                    TUP_IMAGES = (IMAGES, int(spritesheet_variants - 1))
                    self.coin_group.add(Coin(cf_coin, self.cf_global, TUP_IMAGES, rand_pos))
                    placed_coins += 1

            if coin_collision or terrain_collision:
                failed_attempts += 1
                # print(f'failed_attempts = {failed_attempts}')
                if (failed_attempts >= self.LOOP_LIMIT):
                    msg = 'cannot place coins using the corring config'
                    raise LoopError(msg, placed_coins, self.N_COINS, self.LOOP_LIMIT)
        
        self.spawn_collide_group.add(self.coin_group)

    def spawn_turrets(self):
        pass

    #### RECURRING METHODS ####

    def pause(self):
        self.timer.pause()
        self.paused = True
        self.looping = False

    def unpause(self):
        self.timer.unpause()
        self.paused = False
        self.looping = True

    def reset(self):
        self.player.reset_all_attributes()
        for block in self.block_group:
            block.alt_surf_timeleft = 0
        self.coin_group.add(self.collected_coins)
        self.collected_coins = []
        self.timer.new_segment(self.name, False)
        self.looping = True

    def activate_temp_bar(self, ref_id, min_val, max_val):
        if type(ref_id) != list:
            ref_id = [ref_id, "BAR"]
        else:
            ref_id.append("BAR")

        MATCHING_BARS = self.BAR_CONTAINER.add_children_by_ref_id(ref_id, self.UI_STATUS_BARS)
        for BAR in MATCHING_BARS:
            if (min_val):
                BAR.min_val = float(min_val)
            if (max_val):
                BAR.max_val = float(max_val)

    def init_player_death_event(self):
        # if (DEBUG_CHEAT_MODE):
        #     self.player.health = self.player.MAX_HEALTH
        #     self.player.fuel = self.player.MAX_FUEL
        #     self.player.set_idle_image_type()
        #     return

        self.player.fuel = 0.0
        self.player.velocity.y = self.player.TERMINAL_VELO
        self.player.thrust_begin_frames_left = 0
        self.player.thrust_end_frames_left = 0
        self.player.key_thrusting = False
        self.player.collision_recoil_frames_left = 100000
        self.player.collision_cooldown_frames_left = 100000
        self.player.set_special_image_type(self.player.DESTROYED_IMAGES) 
        # TODO: SCORE + START AGAIN POPUP

    def check_player_block_collision(self):
        ''' since collision is based on image masks, call this after draw, but before update
            * if player collides with a block, init the recoil sequence for the player 
        '''
        # ignore collision if player has cooldown frames
        if self.player.collision_cooldown_frames_left:
            # blit the visual overlap
            self.blit_block_player_overlap()
            # collision cooldown frames co-occur with other frames, so check is done at map-level
            self.player.collision_cooldown_frames_left -= 1
            # check if its time to swap the player image back
            if (self.player.collision_cooldown_frames_left == 0):
                if not self.player.key_thrusting:
                    self.player.set_idle_image_type()
        elif spritecollideany(self.player, self.block_group):
            # if player rect collides with any block rects, check detailed mask collision
            collidelist = spritecollide(self.player, self.block_group, False, collided=collide_mask)
            if collidelist:
                # if masks collide, init player recoil phase and get the cd frame count for ghost bar
                cd_frames = self.player.init_phase_collision_recoil()
                if (cd_frames):
                    self.activate_temp_bar('GHOST', 0, cd_frames)
                else:
                    self.init_player_death_event()
                # highlight blocks that player collided with
                for BLOCK in collidelist:
                    BLOCK.init_timed_highlight()

    def check_player_coin_collision(self):
        # check rect collide
        if spritecollideany(self.player, self.coin_group):
            # if rect collide, check mask collide, get & kill collected coins, if any
            collidelist = spritecollide(self.player, self.coin_group, True, collided=collide_mask)
            if (collidelist):
                self.collected_coins.extend(collidelist)
                if (len(self.collected_coins) == self.N_COINS):
                    print("ALL COINS COLLECTED")
                    # TODO: SOMETHING

    #### LOOP ####

    def draw(self):
        self.surface.fill(self.fill_color)

        if (DEBUG_PLAYER_VISUALS):
            self.debug__draw_player_all_info()
        else:
            self.player_group.draw(self.surface)
        self.block_group.draw(self.surface)
        self.coin_group.draw(self.surface)

    def loop(self):
        # if a map was initiated by the menu, launch the main loop
        while (self.looping):
            self.draw()
            self.timer.draw_ui(self.surface)

            # collision checks
            self.check_player_block_collision()
            self.check_player_coin_collision()
            self.check_events()
            self.ui_container_group.update(self.surface)

            display.update()

            self.coin_group.update()
            self.player_group.update()
            self.timer.update()

    def check_events(self):
        for event in pg.event.get():
            # check if the event type matches any relevant types
            match (event.type):
                case self.EVENT_PLAYER_IMG_CYCLE:
                    self.player.cycle_active_image()
                case self.EVENT_UPDATE_TERRAIN:
                    # update blocks, swapping back if highlighted and timer is up
                    self.block_group.update()
                case pg.KEYDOWN:
                    match (event.key):
                        case self.STEER_UP:
                            self.player.key_direction.y -= 1.0
                        case self.STEER_DOWN:
                            self.player.key_direction.y += 1.0
                        case self.STEER_LEFT:
                            self.player.key_direction.x -= 1.0
                        case self.STEER_RIGHT:
                            self.player.key_direction.x += 1.0
                        case self.THRUST:
                            if (self.player.health > 0):
                                self.player.init_phase_thrust_begin()
                        case pg.K_ESCAPE:
                            print("pause called")
                            self.pause()
                        case _:
                            pass
                case pg.KEYUP:
                    # essentially reverts actions upon key up
                    match (event.key):
                        case self.STEER_UP:
                            self.player.key_direction.y += 1.0
                        case self.STEER_DOWN:
                            self.player.key_direction.y -= 1.0
                        case self.STEER_LEFT:
                            self.player.key_direction.x += 1.0
                        case self.STEER_RIGHT:
                            self.player.key_direction.x -= 1.0
                        case self.THRUST:
                            if (self.player.health > 0):
                                self.player.init_phase_thrust_end()
                        case _:
                            pass
                case pg.QUIT:
                    # break both loops and quit program
                    self.looping = False
                    self.paused = False
                    self.quit_called = True
                case _:
                    pass

    #### MASK RELATED METHODS ####

    def largest_mask_component_bounds(self, mask: Mask):
        ''' get the bounding rect of the largest connected component within the mask '''

        bounding_rects: list[Rect] = mask.get_bounding_rects()
        # when called directly, get_bounding_rects calls connected_components(),
        # with a threshhold of only one pixel for each component
        # https://www.pygame.org/docs/ref/mask.html#pygame.mask.Mask.connected_components

        largest_re = bounding_rects[0]

        # typically there's only one rect, but theoretically there could be many.
        if (len(bounding_rects) > 1):
            # UNTESTED CASE
            print('[draw_mask_bounds]: found more than one c-component in mask')

            # iterate over rects and find the largest one
            for re in bounding_rects:
                if ((re.w * re.h) > (largest_re.w * largest_re.h)):
                    largest_re = re

        return largest_re

    def sprite_mask_overlap(self, sprite_1, sprite_2) -> Mask:
        ''' returns a new mask covering the overlapping area of two sprites
            * returns a new mask covering only the overlapping area
        '''
        
        # find the offset between two sprites rects
        offset_x = (sprite_1.rect.x - sprite_2.rect.x)
        offset_y = (sprite_1.rect.y - sprite_2.rect.y)
        offset = (offset_x, offset_y)
        overlap_mask = sprite_2.mask.overlap_mask(sprite_1.mask, offset)

        return overlap_mask

    def collision_center(self, sprite_1, sprite_2):
        ''' for two overlapping sprites, finds the center of mask collision
            * returns the center of this area as a vector2
        '''
        overlap = self.sprite_mask_overlap(sprite_1, sprite_2)
        overlap_rect = overlap.get_rect(topleft=(sprite_2.rect.x, sprite_2.rect.y))
        collidepos = Vec2(overlap_rect.center)

        return collidepos

    def blit_overlap_mask(self, sprite_1, sprite_2):
        dest_pos = (sprite_2.rect.x, sprite_2.rect.y)
        overlap_mask = self.sprite_mask_overlap(sprite_1, sprite_2)
        MASK_SURF = overlap_mask.to_surface(unsetcolor=(0, 0, 0, 0), setcolor=self.overlap_color)
        self.surface.blit(MASK_SURF, dest_pos)

    def blit_block_player_overlap(self):
        # before checking masks, perform a simple collision check using rects
        if (spritecollideany(self.player, self.block_group)):
            # get list of colliding masks
            collidelist = spritecollide(self.player, self.block_group, False, collided=collide_mask)
            for BLOCK in collidelist:
                self.blit_overlap_mask(self.player, BLOCK)

    #### MISC GETTERS ####

    def get_rand_x(self, padding: int):
        ''' get random x-value within map left/right. Padding may be negative. '''
        return randint((self.rect.left + padding), (self.rect.right - padding))

    def get_rand_y(self, padding: int):
        ''' get random y-value within map top/bottom. Padding may be negative. '''
        return randint((self.rect.top + padding), (self.rect.bottom - padding))

    def get_rand_pos(self, padding_x: int, padding_y: int):
        ''' get a random position(x,y) within the map. Padding may be negative. '''
        return (self.get_rand_x(padding_x), self.get_rand_y(padding_y))

    def get_rand_pos_no_collide(self, rect: Rect, pad_x: int, pad_y: int, collidelist: Group | list | Rect):
        ''' get a random position within the map, where the given rect won't collide with the given group.
            x/y padding is added to both rect axis before checks (the original rect will remain unaltered)
            * returns the topleft position of where the rect should be placed.
        '''
        
        # should absolutely have written this before doing placement of blocks/coins.
        # might update them to use this method to conserve a bit of space, but the logic would be the same.

        C_RECT = rect.copy()
        if (pad_x > 0) or (pad_y > 0):
            C_RECT.inflate_ip((2*pad_x), (2*pad_y))

        failed_attempts = 0
        while (failed_attempts < self.LOOP_LIMIT):
            rand_pos = self.get_rand_pos(C_RECT.width, C_RECT.height)
            C_RECT.topleft = rand_pos

            collision_ok = True
            for obj in collidelist:
                if C_RECT.colliderect(obj.rect):
                    collision_ok = False
                    break

            if collision_ok:
                adjusted_pos = ((rand_pos[0]+pad_x), (rand_pos[1]+pad_y))
                del C_RECT
                return adjusted_pos
            else:
                failed_attempts += 1

        # loop didnt return -> no solution was found
        msg = f'cannot find a pos without collision between {rect} and {collidelist}'
        raise LoopError(msg, 0, 1, self.LOOP_LIMIT)

    #### DEBUGGING METHODS ####

    def debug__draw_player_all_info(self):
        # mask debug draws apply to the sprites' temp image, so call before blitting that image
        self.debug__draw_mask_center_mass(self.player)
        self.debug__draw_mask_bounds(self.player)
        self.player_group.draw(self.surface)
        # general debugging calls use the map surface instead, so call them post-draw.
        # (they may extend the image of the sprite, so no way to draw them to the sprite image)
        self.debug__draw_sprite_velocity(self.player, 40.0, 1)
        self.debug__draw_sprite_acceleration(self.player, 40.0, 1)
        self.debug__outline_rect(self.player)

    def debug__draw_sprite_acceleration(self, sprite: Sprite, len: float, width: int):
        ''' visualize sprite acceleration from its position '''
        p1 = Vec2(sprite.position)
        p2 = Vec2(sprite.position + (len * sprite.acceleration))
        draw_line(self.surface, self.DEBUG_COLOR_2, p1, p2, width)

    def debug__draw_sprite_velocity(self, sprite: Sprite, len: float, width: int):
        ''' visualize sprite velocity from its position '''
        p1 = Vec2(sprite.position)
        p2 = Vec2(sprite.position + (len * sprite.velocity))
        draw_line(self.surface, self.DEBUG_COLOR, p1, p2, width)

    def debug__outline_mask(self, sprite: Sprite):
        ''' visualize mask outline by drawing lines along the set pixel points '''
        p_list = sprite.mask.outline()  # get a list of cooordinates from the mask outline
        # print(f'n_points in mask: {len(p_list)}')
        if (p_list):
            draw_lines(sprite.image, self.DEBUG_COLOR, 1, p_list)

    def debug__outline_rect(self, sprite: Sprite):
        ''' draw a border around the sprite bounding rect '''
        draw_rect(self.surface, self.DEBUG_COLOR, sprite.rect, width=1)

    def debug__draw_mask_bounds(self, sprite: Sprite):
        ''' draw the actual bounding rect of the player mask '''
        mask_bounds = self.largest_mask_component_bounds(sprite.mask)
        draw_rect(sprite.image, self.DEBUG_COLOR_2, mask_bounds, width=1)

    def debug__draw_mask_center_mass(self, sprite: Sprite):
        ''' visualize the actual mask bounds by drawing an interesction through it
            * only works if 8 or moore pixels are connected
        '''
        sprite_mask: Mask = sprite.mask
        mask_bounds = self.largest_mask_component_bounds(sprite_mask)
        if mask_bounds == None:
            print('[draw_mask_center_mass]: failed finding connected component')
            return

        mask_center = sprite_mask.centroid()

        line_1_p1 = mask_center
        line_1_p2 = mask_bounds.midtop
        line_2_p1 = mask_center
        line_2_p2 = mask_bounds.midright
        line_3_p1 = mask_center
        line_3_p2 = mask_bounds.midleft
        line_4_p1 = mask_center
        line_4_p2 = mask_bounds.midbottom

        draw_line(self.player.image, self.DEBUG_COLOR_2, line_1_p1, line_1_p2, width=1)
        draw_line(self.player.image, self.DEBUG_COLOR_2, line_2_p1, line_2_p2, width=1)
        draw_line(self.player.image, self.DEBUG_COLOR_2, line_3_p1, line_3_p2, width=1)
        draw_line(self.player.image, self.DEBUG_COLOR_2, line_4_p1, line_4_p2, width=1)

    def __str__(self):
        return f'PG_Map with name="{self.name}, Rect={self.rect}'


''' BENCHMARKS

#### SPRITECOLLIDEANY PRIOR TO MASK CHECKS VS PURE MASK CHECKS ####

    a) checking rects with spritecollideany before mask check
    ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000   31.657   31.657 <string>:1(<module>)
     3938    0.003    0.000    0.209    0.000 PG_map.py:509(check_player_block_collision)
     3938    0.001    0.000    0.013    0.000 PG_map.py:536(check_player_coin_collision)
     
    b) no spritecollideany, only mask checks
    ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000   27.569   27.569 <string>:1(<module>)
     3430    0.003    0.000    0.743    0.000 PG_map.py:509(check_player_block_collision)
     3430    0.002    0.000    0.027    0.000 PG_map.py:537(check_player_coin_collision)
    
    CONCLUSION --> spritecollideany with rect before mask check is **clearly** more efficient
'''
