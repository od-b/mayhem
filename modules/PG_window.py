# python default library imports
## Callable allows type hinting 'function pointers':
from random import randint

# installed library imports
import pygame as pg
## simplify some imports for readability:
from pygame import display, Color, Rect
from pygame.sprite import Sprite, Group, GroupSingle
from pygame.math import Vector2 as Vec2
from pygame.mask import Mask

## general classes
from modules.exceptions import ConfigError
## pygame specific classes
from modules.PG_sprites import Block, Controllable


class PG_Window:
    ''' wrapper for the main app surfaces

        Parameters
        ---
        cf_window: dict with expected keys
            see cf_window['window']
        ---
        Methods
        ---
        create_map(): 
            parameter: dict with expected keys
                see cf_window['map']
    '''

    def __init__(self, cf_global: dict, cf_window: dict):
        # set up window surface
        self.cf_global = cf_global
        self.cf_window = cf_window

        self.fill_color = Color(cf_window['fill_color'])
        self._vsync = int(cf_window['vsync'])
        self.width = int(cf_window['width'])
        self.height = int(cf_window['height'])
        self.surface = display.set_mode((self.width, self.height), vsync=self._vsync)
        self.caption = str(cf_window['caption'])
        self.fill_surface()
        self.set_caption(None)

        ''' set up the map area of the surface '''

        self.map_width = int(self.width - cf_window['map_bounds']['max_x'] - cf_window['map_bounds']['min_x'])
        self.map_height = int(self.height - cf_window['map_bounds']['max_y'] - cf_window['map_bounds']['min_y'])
        self.map_pos_x = int(cf_window['map_bounds']['min_x'])
        self.map_pos_y = int(cf_window['map_bounds']['min_y'])

        self.map_surface_position = (self.map_pos_x, self.map_pos_y)
        ''' map subsurface topleft[x,y] position, relative to the main surface '''

        self.map_size = (self.map_width, self.map_height)
        ''' map size[w,h] '''

        self.map_rect = Rect((self.map_surface_position),(self.map_size))
        ''' rect describing the to-be-created map subsurface '''
        
        self.map_surface = self.surface.subsurface(self.map_rect)
        ''' subsurface of the main surface dedicated to the map area '''

        self.map: PG_Map | None = None
        ''' object containing sprites and attributes that are map-specific '''

    def create_map(self, cf_map: dict):
        ''' initialize the map from the given map config
            * does not call or initialize any map methods
        '''
        self.map = PG_Map(self.cf_global, cf_map, self)

    def set_caption(self, text: str | None):
        ''' append a text to the window caption
            * set text to none to only use caption
        '''
        if (text):
            display.set_caption(f'{self.caption}: {text}')
        else:
            display.set_caption(self.caption)

    def fill_surface_alt_color(self, color: Color | None):
        ''' uses self.fill_color if color is None '''
        if color:
            self.surface.fill(color)
        else:
            self.fill_surface()
    
    def fill_surface(self):
        self.surface.fill(self.fill_color)

    def __str__(self):
        msg = f'< PG_Window: width={self.width}, height={self.height}'
        if (self._vsync == 0):
            msg += f'vsync = True'
        else:
            msg += f'vsync = False'
        msg += f'\nCurrent map: {self.curr_map} >'
        return msg


class PG_Map:
    ''' current map setup used by the the window '''
    def __init__(self, cf_global: dict, cf_map: dict, window: PG_Window):
        self.LOOP_LIMIT = cf_global['loop_limit']
        self.window = window

        # store dict settings
        self.cf_map = cf_map
        self.name = str(cf_map['name'])
        self.available_time = int(cf_map['available_time'])
        self.fill_color = Color(cf_map['fill_color'])
        self.n_obstacles = int(cf_map['n_obstacles'])
        self.gravity = float(cf_map['gravity'])
        self.gravity_c = float(cf_map['gravity_c'])

        # store nested dict settings
        self.cf_player: dict = cf_map['player']
        self.cf_blocks: dict = cf_map['blocks']

        # create subsurface on window.surface
        self.rect = self.window.map_surface.get_rect()
        ''' rect of the map surface '''

        # combined groups
        self.block_group = Group()
        ''' combined group of constant, map-anchored rectangular sprites '''
        # specific groups
        self.obstacle_group = Group()
        ''' group specifically containing the randomly placed obstacle core blocks '''
        self.map_edge_group = Group()
        ''' group specifically containing the map surface outline blocks '''
        self.player_group = GroupSingle()
        ''' player sprite group. If a new sprite is added, the old is removed. '''

        self.window.set_caption(self.name)

    def get_player_controls(self) -> dict[str, int]:
        ''' return a dict containing the player control keys '''
        return self.cf_player['controls']

    def spawn_player(self, pos: tuple[int, int]):
        ''' create and spawn a player sprite
            * if a player already exists, replaces and removes it
            * updates the self.player reference
        '''
        # create the player sprite, then update player_group
        self.player = Controllable(self.cf_player, self.cf_map, pos)
        self.player_group.add(self.player)

    def set_up_terrain(self):
        ''' specialized, run-once function for the creating the map. '''

        # outline the entire game bounds with terrain_blocks:
        terrain_facing = -1
        self.spawn_rect_outline(
            self.cf_blocks['edge_outline'],
            self.map_edge_group,
            self.rect, terrain_facing, None
        )
        # add map bounds outline blocks to the general map group
        self.block_group.add(self.map_edge_group)

        # place obstacle_blocks within the game area
        self.spawn_static_obstacles(self.cf_blocks['obstacle'], self.obstacle_group)

        # outline the obstacles with smaller rects to create more jagged terrain
        terrain_facing = 0
        for BLOCK in self.obstacle_group:
            # for each block in obstacle_group, outline the block rect
            alt_pallette = [BLOCK.color]
            self.spawn_rect_outline(
                self.cf_blocks['obstacle_outline'],
                self.obstacle_group, 
                BLOCK.rect, 
                terrain_facing,
                alt_pallette
            )

        # add obstacle blocks and their outline blocks to the general map group
        self.block_group.add(self.obstacle_group)

    def spawn_rect_outline(self, cf_block: dict, group: Group, bounds: pg.Rect,
                              facing: int, alt_pallette: None | list[Color]):

        ''' encapsulate the given rects' bounds with blocks
            * if alt_pallette is None, uses the cf_block color list at random
            * otherwise, choose the given color pallette for all blocks

            * facing decides the alignment of the blocks relative to the bounds axis':
            * -1 => inwards
            * 0  => center
            * 1  => outwards
        '''

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
            BLOCK = Block(cf_block, alt_pallette, (width, height), position)

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

            BLOCK = Block(cf_block, alt_pallette, (width, height), position)

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

            BLOCK = Block(cf_block, alt_pallette, (width, height), position)
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

            BLOCK = Block(cf_block, alt_pallette, (width, height), position)
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

    def spawn_static_obstacles(self, cf_block: dict, group: Group):
        ''' obstacle spawning algorithm
            * checks for collision with the passed group and self.block_group before placing
        '''

        # padding, taking into account the player size to not completely block paths:
        H_PADDING = int(self.cf_player['surface']['height'] + cf_block['padding'])
        W_PADDING = int(self.cf_player['surface']['width'] + cf_block['padding'])

        # initiate the loop
        placed_blocks = 0
        failed_attempts = 0
        while placed_blocks < self.n_obstacles:
            # set random height/width from within the ranges
            width = randint(cf_block['min_width'], cf_block['max_width'])
            height = randint(cf_block['min_height'], cf_block['max_height'])
            
            # get a random position within the map
            position = (self.get_rand_x(width), self.get_rand_y(height))

            # assemble the block
            BLOCK = Block(cf_block, None, (width, height), position)

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
            if ((pg.sprite.spritecollideany(BLOCK, self.block_group) == None)
                     and (pg.sprite.spritecollideany(BLOCK, group) == None)):
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

    def get_rand_x(self, padding: int):
        ''' get random x-value within left/right. Padding may be negative.
        '''
        return randint((self.rect.left + padding), (self.rect.right - padding))

    def get_rand_y(self, padding: int):
        ''' get random y-value within top/bottom. Padding may be negative.
        '''
        return randint((self.rect.top + padding), (self.rect.bottom - padding))

    def get_rand_pos(self, padding_x: int, padding_y: int):
        ''' get a random position(x,y) within the map. Padding may be negative.
        '''
        return (self.get_rand_x(padding_x), self.get_rand_y(padding_y))

    def fill_surface(self):
        ''' fills/resets the window map surface '''
        self.window.map_surface.fill(self.fill_color)

    def draw_blocks(self):
        ''' draws the static terrain block group to the windows map surface '''
        self.block_group.draw(self.window.map_surface)

    def draw_player(self):
        ''' draws the player to the windows map surface '''
        self.player_group.draw(self.window.map_surface)

    def update(self):
        pass

    def draw(self):
        self.draw_player()
        self.draw_blocks()

    def __str__(self):
        msg = f'< Map with name="{self.name}"\n'
        msg += f'topleft[x,y] = {self.rect.topleft}\n'
        msg += f'size[w,h] = [{self.rect.w}, {self.rect.h} >\n'
        return msg
