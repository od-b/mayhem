# python default library imports
## Callable allows type hinting 'function pointers':
from typing import Callable
from random import randint

# installed library imports
import pygame as pg
from pygame import Color
from pygame.sprite import Group
from pygame.sprite import Sprite
## import and simplify as Vec2 instead of writing 'pygame.math.Vector2(...)' every damn time:
from pygame.math import Vector2 as Vec2

# local dir imports
## config dict
from constants.config import CONFIG as GLOBAL_CF
## general classes
from modules.exceptions import VersionError, ConfigError
## pygame specific classes
from modules.PG_window import PG_Window
from modules.PG_shapes import PG_Rect
from modules.PG_timer import PG_Timer
from modules.PG_ui import PG_Text_Box, PG_Text_Box_Child
from modules.PG_sprites import Static_Interactive, Controllable


class PG_App:
    ''' Singleton app class.
        Takes in a config dict specifying various predefined constants / weights
        * Contains most objects relevant to the app
        * Initializes and sets up pygame objects from the given config
        * Handles game loop and specialized setup-functions

        * Conventions defined for the scope of this class:
        * Methods that start with _ are helper methods, or only called once
            E.g.; if the method spawns blocks, config should be a dict from ['environment']['BLOCKS'].
        * Methods that start with 'create_' will return the object. 'spawn_' functions are void
        * Methods that take in 'config' as a parameter will refer to the relevant subdict of self.cf.
            The expected config is listed in the method docstring.
    '''

    def __init__(self, cf: dict[str, any]):
        self.cf = cf
        ''' reference to the 'CONFIG' dict from ./constants/config.py '''

        self.window = PG_Window(
            str(self.cf['window']['caption']),
            int(self.cf['window']['width']),
            int(self.cf['window']['height']),
            self.cf['window']['bounds_padding'],
            Color(self.cf['window']['fill_color']),
            Color(self.cf['window']['bounds_fill_color']),
            self.cf['window']['vsync']
        )
        ''' object containing main surface window and bounds '''

        self.timer = PG_Timer(
            self.cf['timer']['fps_limit'],
            self.cf['timer']['accurate_timing']
        )
        ''' pygame specific timer object '''

        self.global_physics: dict[str, float] = self.cf['physics']
        ''' global physics weights '''

        # specific groups
        self.obstacle_group = Group()
        ''' group specifically containing the obstacles '''
        self.bounds_group = Group()
        ''' group specifically containing the map outline sprites '''

        # combined groups
        self.update_group = Group()
        ''' combined group group of sprites that are to be updated '''
        self.map_group = Group()
        ''' combined group of constant, anchored sprites '''
        self.active_group = Group()
        ''' combined group group of misc. sprites, including the player(s) '''

        # create the player sprite, then add to relevant groups
        self.player = self.create_controllable_sprite(
            self.cf['special_sprites']['UNIQUE_CONTROLLABLES']['player'],
            None, None
        )
        self.active_group.add(self.player)
        self.update_group.add(self.player)

        # create the terrain:
        self.set_up_map()
        self.UI = self.create_ui_constants()
        ''' constant tuple of ui objects to be updated in the order of addition '''

        self.UI_temp: list[PG_Text_Box | PG_Text_Box_Child] = []
        ''' list of ui objects with a temporary lifespan, eg; popups, info messages '''

    def get_rand_elem(self, list: list):
        ''' generic function. get random elem from a given, non-empty list '''
        return list[randint(1, len(list)-1)]

    def create_ui_constants(self) -> tuple[PG_Text_Box | PG_Text_Box_Child, ...]:
        ''' set up UI constants: objects that will exist until the app is exited '''

        # create a list to allow appending
        elems = []
        DEFAULT_CONFIG = self.cf['ui']['TEXTBOXES']['default']

        # create the 'root' UI element. Pass (0, 0) as top left pos, seeing as
        # we don't know it's pixel size before rendering and want to place it bottom left
        UI_TIME = self.create_tbox_core(DEFAULT_CONFIG, "Time: ", 0, 0, False, self.timer.get_duration)

        # after its rendered, set the position to bottom left (adjusted for default padding)
        UI_TIME.re.bottomleft = (
            self.cf['ui']['container_padding'],
            (self.window.height - self.cf['ui']['container_padding']))
        elems.append(UI_TIME)

        # create the fps frame anchored to the right of UI_TIME
        UI_FPS = self.create_tbox_child(DEFAULT_CONFIG, "FPS: ", UI_TIME, 'right', self.timer.get_fps_int)
        elems.append(UI_FPS)

        PLAYER_ANGLE = self.create_tbox_child(DEFAULT_CONFIG, "Angle: ", UI_FPS, 'right', self.player.get_angle)
        elems.append(PLAYER_ANGLE)

        # return the list as a tuple
        return tuple(elems)

    def set_up_map(self):
        ''' spawn various static sprites around the map. Add to the given group '''

        # outline the entire game bounds with terrain_blocks:
        terrain_facing = -1
        self.spawn_axis_outline(
            self.cf['environment']['BLOCKS']['terrain'], None, None,
            self.bounds_group, self.window.bounds_rect.re, terrain_facing, None
        )
        self.map_group.add(self.bounds_group)

        # place obstacle_blocks within the game area
        self.spawn_static_obstacles(
            self.cf['environment']['BLOCKS']['obstacle'],
            self.cf['environment']['n_obstacles'],
            self.obstacle_group
        )

        # outline the obstacles with smaller rects to create more jagged terrain
        terrain_facing = 0
        for BLOCK in self.obstacle_group:
            self.spawn_axis_outline(
                self.cf['environment']['BLOCKS']['obstacle_outline'], None, None,
                self.obstacle_group, BLOCK.rect, terrain_facing, BLOCK.color
            )
        self.map_group.add(self.obstacle_group)

    def create_tbox_core(self, config: dict, content: str, x: int, y: int,
                         is_static: bool, getter_func: Callable | None):

        ''' return textbox set up using the given config settings 
            * Config: ['ui']['TEXTBOXES'][...]
        '''
        
        # converting every setting to its correct type to avoid any python magic
        TEXTBOX =  PG_Text_Box(
            self.window, content, 
            str(config['font_path']),
            int(config['font_size']),
            pg.Color(config['font_color']), 
            config['apply_aa'],
            pg.Color(config['bg_color']),
            pg.Color(config['border_color']),
            int(config['border_width']),
            int(config['internal_padding_w']),
            int(config['internal_padding_h']),
            getter_func, x, y, is_static
        )
        return TEXTBOX

    def create_tbox_child(self, config: dict, content: str, parent: PG_Text_Box | PG_Rect,
                          parent_alignment: str, getter_func: Callable | None):

        ''' return textbox child set up using the given config settings 
            * Config: ['ui']['TEXTBOXES'][...]
        '''

        # converting every setting to its correct type to avoid any python magic
        TEXTBOX = PG_Text_Box_Child(
            self.window, content, 
            str(config['font_path']),
            int(config['font_size']),
            pg.Color(config['font_color']), 
            config['apply_aa'],
            pg.Color(config['bg_color']),
            pg.Color(config['border_color']),
            int(config['border_width']),
            int(config['internal_padding_w']),
            int(config['internal_padding_h']),
            getter_func, parent, parent_alignment,
            int(config['parent_padding']),
        )
        return TEXTBOX

    def create_controllable_sprite(self, config: dict, trigger_func: Callable | None,
                                   trigger_weight: float | None):

        ''' create and return a controllable type sprite from the given config 
            * Config: ['special_sprites']['UNIQUE_CONTROLLABLES'][...]
        '''
        
        starting_pos = Vec2(400.0, 400.0)
        size = (int(config['surface']['width']), int(config['surface']['height']))
        max_velocity = Vec2(
            float(config['weights']['max_velocity_x']),
            float(config['weights']['max_velocity_y'])
        )
        starting_velocity = Vec2(0.0, 0.0)
        starting_angle = float(0)

        SPRITE = Controllable(
            self.window,
            self.global_physics,
            Color(config['surface']['color']),
            starting_pos,
            size,
            config['surface']['image'],
            float(config['weights']['mass']),
            starting_velocity,
            max_velocity,
            trigger_func,
            trigger_weight,
            starting_angle,
            int(config['weights']['max_health']),
            int(config['weights']['max_mana']),
            int(config['weights']['max_health']),
            int(config['weights']['max_mana'])
        )
        return SPRITE

    def spawn_axis_outline(self, config: dict, trigger_func: Callable | None,
                              trigger_weight: float | None, group: Group, bounds: pg.Rect,
                              facing: int, override_color: None | Color):

        ''' encapsulate the given bounds with smaller rect blocks
            * config: ['environment']['BLOCKS'][...]
            * if iverride_color is None, uses the config color list at random
            * otherwise, choose the given color for all blocks
            * facing decides the alignment of the blocks relative to the bounds axis':
            * -1 => inwards
            * 0  => center
            * 1  => outwards
        '''

        # constant declarations for readability
        CF = config
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
        color = override_color
        last_block: Static_Interactive | None = None

        # 1) topleft --> topright
        curr_pos_x = MIN_X
        while curr_pos_x < MAX_X:
            # set random height/width from within the ranges
            width = randint(CF['min_width'], CF['max_width'])
            height = randint(CF['min_height'], CF['max_height'])

            # ensure no edge overlap by checking for the last block:
            if (curr_pos_x + width) > MAX_X:
                # if the block will be last, adjust size before creating
                width = (MAX_X - curr_pos_x)

            # create a vector to contain the position of the block
            position = Vec2(curr_pos_x, 0.0)

            # get a random color from the config list if override_color is None
            if not (override_color):
                color = self.get_rand_elem(CF['color_pool'])

            # assemble the block
            BLOCK = Static_Interactive(
                self.window, color, position, (width, height), None,
                None, None, None, trigger_func, trigger_weight
            )

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
            curr_pos_x = BLOCK.rect.right + CF['padding']

        # 2) topright --> bottomright
        curr_pos_y = last_block.rect.bottom
        while curr_pos_y < MAX_Y:
            width = randint(CF['min_width'], CF['max_width'])
            height = randint(CF['min_height'], CF['max_height'])
            if (curr_pos_y + height) > MAX_Y:
                height = MAX_Y - curr_pos_y
            if not (override_color):
                color = self.get_rand_elem(CF['color_pool'])
            position = Vec2(0.0, curr_pos_y)
            BLOCK = Static_Interactive(
                self.window, color, position, (width, height), None,
                None, None, None, trigger_func, trigger_weight
            )
            match (facing):
                case (-1):
                    BLOCK.rect.right = MAX_X
                case (0):
                    BLOCK.rect.centerx = MAX_X
                case (1):
                    BLOCK.rect.left = MAX_X
            last_block = BLOCK
            group.add(BLOCK)
            curr_pos_y = BLOCK.rect.bottom + CF['padding']

        # 3) bottomright --> bottomleft
        curr_pos_x = last_block.rect.left
        while curr_pos_x > MIN_X:
            width = randint(CF['min_width'], CF['max_width'])
            height = randint(CF['min_height'], CF['max_height'])
            if (curr_pos_x - width) < MIN_X:
                width = abs(MIN_X - curr_pos_x)
            if not (override_color):
                color = self.get_rand_elem(CF['color_pool'])
            position = Vec2()
            BLOCK = Static_Interactive(
                self.window, color, position, (width, height), None,
                None, None, None, trigger_func, trigger_weight
            )
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
            curr_pos_x = BLOCK.rect.left - CF['padding']

        # 4) bottomleft --> topright
        curr_pos_y = last_block.rect.top
        while curr_pos_y > MIN_Y:
            width = randint(CF['min_width'], CF['max_width'])
            height = randint(CF['min_height'], CF['max_height'])
            if (curr_pos_y - height) < MIN_Y:
                height = abs(MIN_Y - curr_pos_y)
            if not (override_color):
                color = self.get_rand_elem(CF['color_pool'])
            position = Vec2()
            BLOCK = Static_Interactive(
                self.window, color, position, (width, height), None,
                None, None, None, trigger_func, trigger_weight
            )
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
            curr_pos_y = BLOCK.rect.top - CF['padding']

    def spawn_static_obstacles(self, config: dict, n_obstacles: int, group: Group):
        
        ''' obstacle spawning algorithm
            * config: ['environment']['BLOCKS'][...]
            * checks for collision with the passed group and self.map_group before placing
        '''

        # shorten some constants for readability
        CF = config
        FAIL_LIMIT = self.cf['general']['loop_limit']

        # padding, taking into account the player size to not completely block paths:
        W_PADDING = int(self.player.rect.w + CF['padding'])
        H_PADDING = int(self.player.rect.h + CF['padding'])

        # initiate the loop
        placed_blocks = 0
        failed_attempts = 0
        while placed_blocks < n_obstacles:
            # set random height/width from within the ranges
            color = CF['color_pool'][randint(1, len(CF['color_pool'])-1)]
            width = randint(CF['min_width'], CF['max_width'])
            height = randint(CF['min_height'], CF['max_height'])
            position = Vec2(
                self.window.get_rand_x_inbound(width),
                self.window.get_rand_y_inbound(height)
            )
            BLOCK = Static_Interactive(
                self.window, color, position, (width, height), None,
                None, None, None, None, None
            )
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
            if ((pg.sprite.spritecollideany(BLOCK, self.map_group) == None)
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
                if (failed_attempts > FAIL_LIMIT):
                    msg = f'Fail limit of {FAIL_LIMIT} attempts reached. Too many or too large obstacles.\n'
                    msg += f'Current obstacle count: {placed_blocks} / {n_obstacles}'
                    raise ConfigError(msg, config)

            # make sure the copied temp rect is not saved in memory
            del inflated_rect

    def debug__print_player_velocity(self):
        if (self.player.velocity.y == self.player.max_velocity.y):
            print("terminal velocity reached @ \n")
            print(f'ms: {self.timer.total_time}')
            print(f'secs: {self.timer.active_segment.get_duration_formatted()}')

    def debug__draw_mask_outline(self, sprite: Sprite):
        ''' visualize mask outline by drawing lines along the set pixel points '''
        # get a list of cooordinates from the mask outline
        p_list = sprite.mask.outline()
        color = pg.Color(255, 255, 255)
        pg.draw.lines(sprite.image, color, 2, p_list)

    def debug__draw_mask_bounding_box(self, sprite: Sprite):
        ''' visualize the bounding rect of the mask '''
        # get a list of cooordinates from the mask outline
        p_list = sprite.mask.outline()
        color = pg.Color(255, 255, 255)
        pg.draw.lines(self.window.surface, color, 2, p_list)

    def loop(self):
        ''' main loop for drawing, checking events and updating the game '''

        # init the timer as the loop is about to start
        self.timer.start_first_segment(None)

        running = True
        while (running):
            # fill the main surface, then the game bounds
            self.window.fill_surface()
            self.window.bounds_rect.draw_background()

            # draw map constants
            self.map_group.draw(self.window.surface)

            # draw other sprites
            self.active_group.draw(self.window.surface)

            # draw the ui
            for obj in self.UI:
                obj.draw()
            for obj in self.UI_temp:
                obj.draw()

            # self.debug__draw_mask_outline(self.player)
            
            
            # refresh the display, applying drawing etc.
            pg.display.update()

            # loop through events
            for event in pg.event.get():
                # check if event type matches any triggers
                match (event.type):
                    case pg.QUIT:
                        running = False  # exit the app

                    case pg.MOUSEBUTTONDOWN:
                        self.player.rotate_c_clockwise(3.0)
                        # mouse click
                        # MOUSE_POS = pg.mouse.get_pos()
                        # print(MOUSE_POS)
                        pass

                    case pg.KEYDOWN:
                        # match keydown event to an action, or pass
                        match (event.key):
                            case pg.K_ESCAPE:
                                running = False

            # update the dynamic objects in core UI, and then temp UI
            for obj in self.UI:
                obj.update()

            for obj in self.UI_temp:
                obj.update()

            # now that events are read, update sprites before next frame
            self.update_group.update()

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
    APP = PG_App(GLOBAL_CF)
    APP.loop()
