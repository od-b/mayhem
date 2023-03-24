# python default library imports
## Callable allows type hinting 'function pointers':
from typing import Callable
from random import randint

# installed library imports
import pygame as pg
## simplify some imports for readability:
from pygame import Color
from pygame.sprite import Sprite, Group, GroupSingle
from pygame.math import Vector2 as Vec2
from pygame.mask import Mask

# local dir imports
## config dict
from constants.config import CONFIG as GLOBAL_CF
## general classes
from modules.exceptions import VersionError, ConfigError
## pygame specific classes
from modules.PG_window import PG_Window
from modules.PG_timer import PG_Timer
from modules.PG_ui import Container, Text_Box
from modules.PG_sprites import Block, Controllable


class PG_App:
    ''' Singleton app class.
        Takes in a config dict specifying various predefined constants / weights
        * Contains most objects relevant to the app
        * Initializes and sets up pygame objects from the given config
        * Handles game loop and specialized setup-functions

        * Conventions defined for the scope of this class:
        * Methods that start with _ are helper methods, or only called once
            E.g.; if the method spawns blocks, config should be a dict from ['map']['BLOCKS'].
        * Methods that start with 'create_' will return the object. 'spawn_' functions are void
        * Methods that take in 'config' as a parameter will refer to the relevant subdict of self.cf.
            The expected config is listed in the method docstring.
    '''

    def __init__(self, cf: dict[str, any]):
        self.cf = cf
        ''' reference to the 'CONFIG' dict from ./constants/config.py '''
        
        # store some important config sections for readability purposes
        self.LOOP_LIM = self.cf['general']['loop_limit']
        ''' does not affect self.loop() See info @ config : ['general']['loop_limit'] '''
        self.config_textbox_default = self.cf['ui']['TEXTBOXES']['default']
        ''' default configuration of the ui textboxes '''
        self.config_player = self.cf['sprites']['UNIQUE']['player']
        ''' the player sprite config. Needed several places to ensure game functions properly. '''
        self.window = PG_Window(cf['window'], cf['map'])
        ''' object containing main surface window and bounds '''
        self.timer = PG_Timer(self.cf['timer']['fps_limit'], self.cf['timer']['accurate_timing'])
        ''' pygame specific timer object '''
        self.global_physics: dict[str, float] = self.cf['physics']
        ''' global physics weights '''

        # combined groups
        self.block_group = Group()
        ''' combined group of constant, map-anchored rectangular sprites '''
        self.container_group = Group()
        ''' group of ui containers. Contains their own groups of children '''

        # specific groups
        self.obstacle_group = Group()
        ''' group specifically containing the randomly placed obstacle core blocks '''
        self.map_edge_group = Group()
        ''' group specifically containing the map surface outline blocks '''
        self.player_group = GroupSingle()
        ''' player sprite group. If a new sprite is added, the old is removed. '''

        # set up the map
        self.set_up_map()   # populates obstacle_group, map_edge_group and block_group

        # spawn the player sprite
        self.player: Controllable
        ''' holds a direct pointer to the Controllable player sprite '''
        self.spawn_player((0, 0), None)

        # not sure if this is needed, but i want to be on the safe side:
        # define movement key constants to ensure dict access doesn't impact performance
        PLAYER_CONTROLS = self.cf['sprites']['UNIQUE']['player']['controls']
        self.STEER_UP = int(PLAYER_CONTROLS['steer_up'])
        self.STEER_LEFT = int(PLAYER_CONTROLS['steer_left'])
        self.STEER_DOWN = int(PLAYER_CONTROLS['steer_down'])
        self.STEER_RIGHT = int(PLAYER_CONTROLS['steer_right'])
        self.HALT = int(PLAYER_CONTROLS['halt'])
        self.LOCK = int(PLAYER_CONTROLS['lock'])
        # pg.key.set_repeat(self.timer.fps_limit, self.timer.fps_limit)
        
        self.set_up_ui(self.cf['ui']['CONTAINERS']['default'])
    
    def set_up_ui(self, config: dict):
        # create bottom info panel container
        # set width to the size of the map
        # set size and pos to match the available padded bottom space
        width = int(self.window.map_rect.width)
        height = int(self.window.height - self.window.map_rect.height - self.window.map_bounds['min_y'])

        if (height < 40):
            print("not enough vertical padding to fit the UI. Increase ['map']['padded_bounds'].")
            return

        pos_x = int(self.window.map_bounds['min_x'])
        pos_y = int(self.window.map_rect.height + self.window.map_bounds['min_y'])
        print(height)

        BOTTOM_PANEL = Container(
            self.window.surface,
            (width, height),
            (pos_x, pos_y),
            "center",
            "center",
            Color(config['color']),
            Color(config['border_color']),
            int(config['border_width']),
        )
        self.container_group.add(BOTTOM_PANEL)

    def set_up_map(self):
        ''' spawn various static sprites around the map. Add to the given group '''

        # outline the entire game bounds with terrain_blocks:
        terrain_facing = -1
        self.spawn_rect_outline(
            self.cf['sprites']['BLOCKS']['terrain'],
            None, None, self.map_edge_group,
            self.window.map_rect, terrain_facing, None
        )
        # add map bounds outline blocks to the general map group
        self.block_group.add(self.map_edge_group)

        # place obstacle_blocks within the game area
        self.spawn_static_obstacles(
            self.cf['sprites']['BLOCKS']['obstacle'],
            None, None, self.obstacle_group,
            self.cf['map']['n_obstacles'],
        )

        # outline the obstacles with smaller rects to create more jagged terrain
        terrain_facing = 0
        for BLOCK in self.obstacle_group:
            # for each block in obstacle_group, outline the block rect
            color_pool = [BLOCK.color]
            self.spawn_rect_outline(
                self.cf['sprites']['BLOCKS']['obstacle_outline'],
                None, None, self.obstacle_group, 
                BLOCK.rect, terrain_facing, color_pool
            )
        
        # add obstacle blocks and their outline blocks to the general map group
        self.block_group.add(self.obstacle_group)

    def get_current_player_angle(self):
        return self.player.get_angle()

    def spawn_player(self, pos: tuple, trigger_func: Callable | None):
        ''' create and spawn a player sprite
            * if a player already exists, replaces and removes it
            * updates the self.player reference
        '''
        # remove any references to the old player, if it exists
        if (self.player_group.sprite):
            self.player_group.sprite.kill()
            del self.player_group.sprite

        # convert the position tuple to a vector
        pos = Vec2(pos)
        # create the player sprite, then update player_group
        self.player = Controllable(self.config_player, self.global_physics, pos, trigger_func)
        self.player_group.add(self.player)

    def spawn_rect_outline(self, config: dict, trigger_func: Callable | None,
                              trigger_weight, group: Group, bounds: pg.Rect,
                              facing: int, special_color_pool: None | list[Color]):

        ''' encapsulate the given rects' bounds with blocks
            * config: ['sprites']['BLOCKS'][...]
            * if iverride_color is None, uses the config color list at random
            * otherwise, choose the given color for all blocks
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
            width = randint(config['min_width'], config['max_width'])
            height = randint(config['min_height'], config['max_height'])

            # create a vector to contain the position of the block
            position = Vec2(curr_pos_x, 0.0)

            # ensure no edge overlap by checking for the last block:
            if (curr_pos_x + width) > MAX_X:
                # if the block will be last, adjust size before creating
                width = (MAX_X - curr_pos_x)

            # assemble the block
            BLOCK = Block(config, special_color_pool, (width, height), position, trigger_func)
            
            # set trigger weight if applicable
            if (trigger_weight and trigger_func):
                BLOCK.set_trigger_parameter(trigger_weight)

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
            curr_pos_x = BLOCK.rect.right + config['padding']

        # 2) topright --> bottomright
        curr_pos_y = last_block.rect.bottom
        while curr_pos_y < MAX_Y:
            width = randint(config['min_width'], config['max_width'])
            height = randint(config['min_height'], config['max_height'])
            position = Vec2(0.0, curr_pos_y)
            if (curr_pos_y + height) > MAX_Y:
                height = MAX_Y - curr_pos_y

            BLOCK = Block(config, special_color_pool, (width, height), position, trigger_func)
            if (trigger_weight and trigger_func):
                BLOCK.set_trigger_parameter(trigger_weight)

            match (facing):
                case (-1):
                    BLOCK.rect.right = MAX_X
                case (0):
                    BLOCK.rect.centerx = MAX_X
                case (1):
                    BLOCK.rect.left = MAX_X
            last_block = BLOCK
            group.add(BLOCK)
            curr_pos_y = BLOCK.rect.bottom + config['padding']

        # 3) bottomright --> bottomleft
        curr_pos_x = last_block.rect.left
        while curr_pos_x > MIN_X:
            width = randint(config['min_width'], config['max_width'])
            height = randint(config['min_height'], config['max_height'])
            position = Vec2()
            if (curr_pos_x - width) < MIN_X:
                width = abs(MIN_X - curr_pos_x)

            BLOCK = Block(config, special_color_pool, (width, height), position, trigger_func)
            if (trigger_weight and trigger_func):
                BLOCK.set_trigger_parameter(trigger_weight)
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
            curr_pos_x = BLOCK.rect.left - config['padding']

        # 4) bottomleft --> topright
        curr_pos_y = last_block.rect.top
        while curr_pos_y > MIN_Y:
            width = randint(config['min_width'], config['max_width'])
            height = randint(config['min_height'], config['max_height'])
            position = Vec2()
            if (curr_pos_y - height) < MIN_Y:
                height = abs(MIN_Y - curr_pos_y)

            BLOCK = Block(config, special_color_pool, (width, height), position, trigger_func)
            if (trigger_weight and trigger_func):
                BLOCK.set_trigger_parameter(trigger_weight)
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
            curr_pos_y = BLOCK.rect.top - config['padding']

    def spawn_static_obstacles(self, config: dict, trigger_func: Callable | None, trigger_weight,
                               group: Group, n_obstacles: int):

        ''' obstacle spawning algorithm
            * config: ['sprites']['BLOCKS'][...]
            * checks for collision with the passed group and self.block_group before placing
        '''

        # padding, taking into account the player size to not completely block paths:
        H_PADDING = int(self.config_player['surface']['height'] + config['padding'])
        W_PADDING = int(self.config_player['surface']['width'] + config['padding'])

        # initiate the loop
        placed_blocks = 0
        failed_attempts = 0
        while placed_blocks < n_obstacles:
            # set random height/width from within the ranges
            width = randint(config['min_width'], config['max_width'])
            height = randint(config['min_height'], config['max_height'])
            position = Vec2(
                self.window.get_rand_x_inbound(width),
                self.window.get_rand_y_inbound(height)
            )
            # assemble the block
            BLOCK = Block(config, None, (width, height), position, trigger_func)

            # set trigger weight if applicable
            if (trigger_weight and trigger_func):
                BLOCK.set_trigger_parameter(trigger_weight)

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
                if (failed_attempts > self.LOOP_LIM):
                    msg = f'\
                        Fail limit of {self.LOOP_LIM} attempts reached.\
                        Too many or too large obstacles.\n\
                        block padding set too high can also be the cause.\
                        Current obstacle count: {placed_blocks} / {n_obstacles}'
                    raise ConfigError(msg, config)

            # make sure the copied temp rect is not saved in memory
            del inflated_rect

    def debug__print_player_velocity(self):
        if (self.player.velocity.y == self.player.max_velocity.y):
            print("terminal velocity reached @ \n")
            print(f'ms: {self.timer.total_time}')
            print(f'secs: {self.timer.active_segment.get_duration_formatted()}')

    def debug__sprite_mask_outline(self, sprite: Sprite):
        ''' visualize mask outline by drawing lines along the set pixel points '''
    
        # get a list of cooordinates from the mask outline
        p_list = sprite.mask.outline()
        color = self.cf['general']['debug_color']
        pg.draw.lines(sprite.image, color, 1, p_list)

    def debug__mask_outline(self, mask: Mask):
        ''' visualize mask outline by drawing lines along the set pixel points '''

        # get a list of cooordinates from the mask outline
        p_list = mask.outline()
        color = self.cf['general']['debug_color']
        pg.draw.lines(self.window.surface, color, 1, p_list)

    def loop_events(self):
        # loop through events
        for event in pg.event.get():
            # check if event type matches any triggers
            match (event.type):
                case pg.QUIT:
                    self.app_running = False
                case pg.MOUSEBUTTONDOWN:
                    print(pg.mouse.get_pos())
                case pg.KEYDOWN:
                    # match keydown event to an action, or pass
                    match (event.key):
                        case self.STEER_UP:
                            self.player.dir_y -= 1.0
                            self.player.update_direction()
                        case self.STEER_DOWN:
                            self.player.dir_y += 1.0
                            self.player.update_direction()
                        case self.STEER_LEFT:
                            self.player.dir_x -= 1.0
                            self.player.update_direction()
                        case self.STEER_RIGHT:
                            self.player.dir_x += 1.0
                            self.player.update_direction()
                        case self.HALT:
                            self.player.ascent += 1.0
                        case self.LOCK:
                            self.player.ascent -= 1.0
                        case _:
                            pass
                case pg.KEYUP:
                    # match keydown event to an action, or pass
                    match (event.key):
                        case self.STEER_UP:
                            self.player.dir_y += 1.0
                            self.player.update_direction()
                        case self.STEER_DOWN:
                            self.player.dir_y -= 1.0
                            self.player.update_direction()
                        case self.STEER_LEFT:
                            self.player.dir_x += 1.0
                            self.player.update_direction()
                        case self.STEER_RIGHT:
                            self.player.dir_x -= 1.0
                            self.player.update_direction()
                        case self.HALT:
                            self.player.ascent -= 1.0
                        case self.LOCK:
                            self.player.ascent += 1.0
                        case _:
                            pass
                case _:
                    pass

    def loop(self):
        ''' main loop for drawing, checking events and updating the game '''

        # init the timer as the loop is about to start
        self.timer.start_first_segment(None)
        self.app_running = True

        while (self.app_running):
            # fill the main surface, then the game bounds
            self.window.fill_map_surface()

            # draw map blocks
            self.block_group.draw(self.window.map_surface)

            # draw the player
            self.player_group.draw(self.window.map_surface)

            # draw the ui

            # for BLOCK in self.obstacle_group:
            #     self.debug__sprite_mask_outline(BLOCK)
            # for BLOCK in self.block_group:
            #     self.debug__sprite_mask_outline(BLOCK)
            # self.debug__sprite_mask_outline(self.player)

            # refresh the display, applying drawing etc.
            pg.display.update()

            # loop through events
            self.loop_events()

            # now that events are read, update sprites before next frame
            self.player_group.update()

            # update the timer. Also limits the framerate if set
            self.timer.update()


if __name__ == '__main__':
    # initialize pygame and verify the version before anything else
    pg.init()

    if (pg.__version__ != GLOBAL_CF['general']['req_pygame_version']):
        raise VersionError("Pygame", pg.__version__,
            GLOBAL_CF['general']['req_pygame_version']
        )

    # load the game
    GAME = PG_App(GLOBAL_CF)
    GAME.loop()
