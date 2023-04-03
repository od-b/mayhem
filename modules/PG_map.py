from random import randint
from typing import Callable

# installed library imports
import pygame as pg
from pygame import Color, Surface, Rect, display, event
from pygame.math import Vector2 as Vec2
from pygame.draw import line as draw_line, lines as draw_lines, rect as draw_rect
from pygame.sprite import Sprite, Group, GroupSingle, spritecollide, spritecollideany, collide_mask
from pygame.mask import Mask

# from pygame.image import save as image_save
# image_save(self.surface, "screenshot.png")

## general classes
from .general.exceptions import ConfigError
## pygame specific classes
from .PG_window import PG_Window
from .PG_player import Player
from .PG_block import Block
from .PG_timer import PG_Timer
from .PG_ui_container import UI_Container
from .PG_ui_bar import UI_Bar, UI_Auto_Bar_Horizontal, UI_Icon_Bar_Horizontal, UI_Auto_Icon_Bar_Horizontal


class PG_Map:
    ''' current map setup used by the the app '''
    def __init__(self, PARENT, cf_map: dict, subsurface: Surface):
        self.PARENT = PARENT
        self.cf_map: dict = cf_map
        self.surface = subsurface

        # store needed parent attributes
        self.timer: PG_Timer        = PARENT.timer
        self.cf_global: dict        = PARENT.cf_global

        self.cf_intervals: dict     = cf_map['upd_interval']
        self.cf_player: dict        = cf_map['player']
        self.cf_blocks: dict        = cf_map['blocks']
        self.cf_ui_containers: dict = cf_map['ui_containers']
        self.cf_ui_bars: dict       = cf_map['ui_bars']

        # globals
        self.LOOP_LIMIT         = int(self.cf_global['loop_limit'])
        self.DEBUG_COLOR        = Color(self.cf_global['debug_color'])
        self.DEBUG_COLOR_2      = Color(self.cf_global['debug_color_2'])

        # store dict settings
        self.name               = str(cf_map['name'])
        self.available_time     = int(cf_map['available_time'])
        self.fill_color         = Color(cf_map['fill_color'])
        self.n_obstacles        = int(cf_map['n_obstacles'])
        self.gravity_m          = float(cf_map['gravity_m'])
        self.gravity_c          = float(cf_map['gravity_c'])

        # misc
        self.mask_overlap_color = self.fill_color
        self.rect = self.surface.get_rect()
        self.debug_player_visuals = False
        self.looping = False

        #### SPRITE GROUPS ####

        self.block_group = Group()
        ''' combined group of constant, map-anchored rectangular sprites '''
        self.obstacle_group = Group()   # NOT SURE IF NEEDED, LEAVING FOR NOW
        ''' group specifically containing the randomly placed obstacle core blocks '''
        self.map_edge_group = Group()   # NOT SURE IF NEEDED, LEAVING FOR NOW
        ''' group specifically containing the map surface outline blocks '''
        self.player_group = GroupSingle()
        ''' player sprite group. If a new sprite is added, the old is removed. '''
    
        self.ui_container_group = Group()
        self.temp_ui_group = Group()

        self.UI_AUTO_BARS: list[UI_Auto_Icon_Bar_Horizontal] = []
        self.BAR_CONTAINER = UI_Container(
            self.cf_ui_containers['bar_container'],
            (int(self.rect.left + 26), int(self.rect.top + 14)),
            None,
            "bottom",
            "top_bottom"
        )
        self.ui_container_group.add(self.BAR_CONTAINER)

    def set_up_all(self, start_loop: bool):
        self.set_update_intervals()
        self.store_player_controls()
        self.set_up_terrain()
        self.spawn_player((400, 400))
        self.set_up_ui_bars()
        self.BAR_CONTAINER.add_children([self.HEALTH_BAR, self.FUEL_BAR])

        if (start_loop):
            self.looping = True
            self.timer.new_segment(self.name, False)

    def set_update_intervals(self):
        self.EVENT_UPDATE_TERRAIN = self.timer.create_event_timer(self.cf_map['upd_interval']['terrain'], 0)
        ''' custom pygame event call to update terrain '''

    def store_player_controls(self) -> dict[str, int]:
        self.STEER_UP    = int(self.cf_player['controls']['steer_up'])
        self.STEER_LEFT  = int(self.cf_player['controls']['steer_left'])
        self.STEER_DOWN  = int(self.cf_player['controls']['steer_down'])
        self.STEER_RIGHT = int(self.cf_player['controls']['steer_right'])
        self.THRUST      = int(self.cf_player['controls']['thrust'])

    def set_up_terrain(self):
        ''' specialized function for the creating the map terrain '''

        # outline the entire game bounds with terrain_blocks:
        terrain_facing = -1
        self.spawn_block_outline(
            self.cf_blocks['edge_outline'],
            self.map_edge_group,
            self.rect, terrain_facing, None
        )
        # add map bounds outline blocks to the general map group
        self.block_group.add(self.map_edge_group)

        # place obstacle_blocks within the game area
        self.spawn_obstacle_blocks(self.cf_blocks['obstacle'], self.obstacle_group)

        # outline the obstacles with smaller rects to create more jagged terrain
        terrain_facing = 1
        for BLOCK in self.obstacle_group:
            # for each block in obstacle_group, outline the block rect
            alt_pallette = [BLOCK.color]
            self.spawn_block_outline(
                self.cf_blocks['obstacle_outline'],
                self.obstacle_group, 
                BLOCK.rect, 
                terrain_facing,
                alt_pallette
            )

        # add obstacle blocks and their outline blocks to the general map group
        self.block_group.add(self.obstacle_group)

    def spawn_player(self, spawn_pos: tuple[int, int]):
        ''' create and spawn a player sprite
            * if a player already exists, replaces and removes it
            * updates the self.player reference
        '''
        # create the player sprite, then update player_group
        self.player = Player(self.cf_player, self.cf_map, self.cf_global, spawn_pos)
        self.player_group.add(self.player)

    def spawn_block_outline(self, cf_block: dict, group: Group, bounds: Rect,
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
                          position, int(self.cf_map['upd_interval']['terrain']))

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
                          position, int(self.cf_map['upd_interval']['terrain']))

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
                          position, int(self.cf_map['upd_interval']['terrain']))
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
                          position, int(self.cf_map['upd_interval']['terrain']))
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
        while placed_blocks < self.n_obstacles:
            # set random height/width from within the ranges
            width = randint(cf_block['min_width'], cf_block['max_width'])
            height = randint(cf_block['min_height'], cf_block['max_height'])
            
            # get a random position within the map
            position = self.get_rand_pos(width, height)

            # assemble the block
            BLOCK = Block(cf_block, self.cf_global, color_pool, (width, height),
                          position, int(self.cf_map['upd_interval']['terrain']))

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
                # otherwise, free (delete) the sprite and try again
                del BLOCK
                failed_attempts += 1
                # check if attempt limit is reached
                if (failed_attempts > self.LOOP_LIMIT):
                    msg = f'\
                        Fail limit of {self.LOOP_LIMIT} attempts reached.\
                        Too many or too large obstacles.\n\
                        block padding set too high can also be the cause.\
                        Current obstacle count: {placed_blocks} / {self.n_obstacles}'
                    raise ConfigError(msg, cf_block)

            # make sure the copied temp rect is not saved in memory
            del inflated_rect

    def check_player_block_collision(self):
        ''' since collision is based on image masks, call this after draw, but before update
            * if player collides with a block, init the recoil sequence for the player 
        '''
        # case 0: ignore collision if player has no mass or cooldown frames
        if self.player.collision_cooldown_frames_left:
            # blit the visual overlap
            self.blit_block_player_overlap()
        elif spritecollideany(self.player, self.block_group):
            # if player rect collides with any block rects, check detailed mask collision
            collidelist = spritecollide(self.player, self.block_group, False, collided=collide_mask)
            if collidelist:
                # if masks collide, init player recoil phase
                self.player.init_phase_collision_recoil()
                # highlight blocks that player collided with
                for BLOCK in collidelist:
                    BLOCK.init_timed_highlight()

    def create_horizontal_icon_bar(self, cf_key: str, getter_func: Callable, max: float | int):
        CF = self.cf_ui_bars[cf_key]
        cf_bar = CF['cf_bar']
        ref_id = CF['ref_id']
        size = CF['size']
        icon_path = CF['icon']
        icon_offset = CF['icon_offset']
        copy_super_bg = CF['copy_super_bg']
        remove_when_empty = CF['remove_when_empty']

        BAR = UI_Auto_Icon_Bar_Horizontal(
            cf_bar,
            self.cf_global,
            ref_id,
            (0, 0),
            size,
            icon_path,
            icon_offset,
            copy_super_bg,
            float(max),
            getter_func,
            remove_when_empty
        )
        self.UI_AUTO_BARS.append(BAR)
        return BAR

    def set_up_ui_bars(self):
        self.HEALTH_BAR = self.create_horizontal_icon_bar(
            'health',
            self.player.get_curr_health,
            self.player.MAX_HEALTH,
        )
        self.FUEL_BAR = self.create_horizontal_icon_bar(
            'fuel',
            self.player.get_curr_fuel,
            self.player.MAX_FUEL,
        )
        self.SHIELD_BAR = self.create_horizontal_icon_bar(
            'shield',
            self.player.get_curr_fuel,
            self.player.MAX_FUEL,
        )

    def loop(self):
        # if a map was initiated by the menu, launch the main loop
        while (self.looping):
            self.surface.fill(self.fill_color)

            if (self.debug_player_visuals):
                self.debug__draw_player_all_info()
            else:
                self.player_group.draw(self.surface)
            self.block_group.draw(self.surface)

            self.check_player_block_collision()
            self.check_events()

            # self.test_group.update()
            # self.test_group.draw(self.surface)
            self.ui_container_group.update(self.surface)

            display.update()
            self.player.health -= 0.01
            self.player.fuel -= 0.01

            self.player_group.update()
            self.timer.update()

    def check_events(self):
        for ev in pg.event.get():
            # check if event type matches any triggers
            match (ev.type):
                case pg.KEYDOWN:
                    match (ev.key):
                        case self.STEER_UP:
                            self.player.direction.y -= 1.0
                        case self.STEER_DOWN:
                            self.player.direction.y += 1.0
                        case self.STEER_LEFT:
                            self.player.direction.x -= 1.0
                        case self.STEER_RIGHT:
                            self.player.direction.x += 1.0
                        case self.THRUST:
                            self.player.init_phase_thrust_begin()
                        case _:
                            pass
                case pg.KEYUP:
                    # essentially reverts actions upon key up
                    match (ev.key):
                        case self.STEER_UP:
                            self.player.direction.y += 1.0
                        case self.STEER_DOWN:
                            self.player.direction.y -= 1.0
                        case self.STEER_LEFT:
                            self.player.direction.x += 1.0
                        case self.STEER_RIGHT:
                            self.player.direction.x -= 1.0
                        case self.THRUST:
                            self.player.init_phase_thrust_end()
                        case _:
                            pass
                case pg.QUIT:
                    self.looping = False
                    self.PARENT.looping = False
                # case self.EVENT_UPDATE_UI_CORE:
                #     self.ui_core_group.update()
                case self.EVENT_UPDATE_TERRAIN:
                    self.block_group.update()
                case _:
                    pass


    #### MASK RELATED STUFF ####

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
        MASK_SURF = overlap_mask.to_surface(unsetcolor=(0, 0, 0, 0), setcolor=self.mask_overlap_color)
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
        msg = f'< Map with name="{self.name}"\n'
        msg += f'topleft[x,y] = {self.rect.topleft}\n'
        msg += f'size[w,h] = [{self.rect.w}, {self.rect.h} >\n'
        return msg
