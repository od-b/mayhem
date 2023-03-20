# default python library imports
from typing import Callable     # type hint for function pointers
from random import randint, uniform

# library imports
import pygame as pg
from pygame.math import Vector2 as Vec2
from pygame.sprite import Group
from pygame.sprite import Sprite

# local imports
## general:
from constants.config import CONFIG as CF
from modules.exceptions import VersionError, LogicError
## pygame specific:
from modules.PG_window import PG_Window
from modules.PG_shapes import PG_Rect
from modules.PG_timer import PG_Timer
from modules.PG_ui import PG_Text_Box, PG_Text_Box_Child
# sprites:
from modules.PG_sprites import Static_Interactive, Controllable


class PG_App:
    ''' singleton app class
        * takes in a config dict specifying various constants and parameters
        * contains most objects relevant to the app
        * initializes and sets up pygame objects from the given config
        * contains game loop, specialized setup-functions
        * methods used internally and only once start with '_'
    '''

    def __init__(self, cf: dict[str, any]):
        self.cf = cf
        ''' reference to the 'CONFIG' dict from ./constants/config.py '''

        self._pygame_init() # init pygame and perform version control

        self.window = PG_Window(
            self.cf['window']['caption'],
            self.cf['window']['width'],
            self.cf['window']['height'],
            self.cf['window']['bounds_padding'],
            self.cf['window']['fill_color'],
            self.cf['window']['bounds_fill_color'],
        )
        ''' object containing main surface window and bounds '''

        self.timer = PG_Timer(self.cf['timing']['fps_limit'])   
        ''' pygame specific timer object '''

        self.UI = self._set_up_ui_constants()
        ''' constant tuple of ui objects to be updated in the order of addition '''

        self.UI_temp: list[PG_Text_Box | PG_Text_Box_Child] = []
        ''' list of ui objects with a temporary lifespan, eg; popups, info messages '''

        self.update_group = Group()
        ''' group of sprites that are to be updated '''

        self.map_group = Group()
        ''' group of constant, map-related sprites '''
        
        self.active_group = Group()
        ''' group of misc. sprites, including the player(s) '''

        # create the player sprite:
        self.player = self.create_controllable_sprite(self.cf['player'], None, None)
        self.active_group.add(self.player)
        self.update_group.add(self.player)

        # create the terrain:
        self._set_up_map(self.map_group)

    def get_rand_list_elem(self, list: list):
        ''' generic helper function. get random elem from a given, non-empty list '''
        return list[randint(1, len(list)-1)]

    def _set_up_ui_constants(self) -> tuple[PG_Text_Box | PG_Text_Box_Child, ...]:
        ''' set up UI constants: objects that will exist until the app is exited '''

        # create a list to allow appending
        elems = []
        DEFAULT_CONFIG = self.cf['ui']['textbox']['default']

        # create the 'root' UI element. Pass (0, 0) as top left pos, seeing as
        # we don't know it's pixel size before rendering and want to place it bottom left
        UI_TIME = self.create_tbox_core(DEFAULT_CONFIG, "Time: ", 0, 0, False, self.timer.get_duration)

        # after its rendered, set the position to bottom left (adjusted for default padding)
        UI_TIME.re.bottomleft = (
            self.cf['ui']['default']['padding'],
            (self.window.height - self.cf['ui']['default']['padding']))
        elems.append(UI_TIME)

        # create the fps frame anchored to the right of UI_TIME
        UI_FPS = self.create_tbox_child(DEFAULT_CONFIG, "FPS: ", UI_TIME, 'right', self.timer.get_fps_int)
        elems.append(UI_FPS)

        # return the list as a tuple
        return tuple(elems)

    def _set_up_map(self, group: Group):
        ''' spawn various static sprites around the map. Add to the given group '''

        # outline the entire game bounds with terrain_blocks:
        terrain_facing = 0
        self.spawn_terrain_outline(
            self.cf['environment']['terrain_block'],
            None, None, group, self.window.bounds_rect.re, terrain_facing
        )

        # place obstacle_blocks within the game area
        self.spawn_static_obstacles(
            self.cf['environment']['obstacle_block'],
            self.cf['environment']['n_obstacles'],
            None, None, group
        )

    def _pygame_init(self):
        ''' initialize pygame and verify pygame version '''

        pg.init()
        pg_version = str(pg.__version__)
        req_pg_version = str(self.cf['general']['req_pygame_version'])
        if not (pg_version == req_pg_version):
            raise VersionError("Pygame", pg_version, req_pg_version)

    def create_tbox_core(self, config: dict, content: str, x: int, y: int,
                         is_static: bool, getter_func: Callable | None):

        ''' return textbox set up using the given config settings '''
        
        # converting every setting to its correct type to avoid any python magic
        return PG_Text_Box(
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

    def create_tbox_child(self, config: dict, content: str, parent: PG_Text_Box | PG_Rect,
                          parent_alignment: str, getter_func: Callable | None):

        ''' return textbox child set up using the given config settings '''

        # converting every setting to its correct type to avoid any python magic
        return PG_Text_Box_Child(
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

    def create_controllable_sprite(self, config: dict, trigger_func: Callable | None,
                                   trigger_weight: float | None):
        
        ''' create and return a controllable type sprite from the given config '''
        
        MAX_VELOCITY = Vec2(
            float(config['max_velocity_x']),
            float(config['max_velocity_y']))
        VELOCITY = Vec2(
            float(config['initial_vectors']['velocity_x']),
            float(config['initial_vectors']['velocity_y']))
        POSITION = Vec2(
            int(config['initial_vectors']['pos_x']),
            int(config['initial_vectors']['pos_y']))
        SIZE = (int(config['width']), int(config['height']))

        SPRITE = Controllable(
            self.window,
            self.cf['physics'],
            config['color'],
            POSITION,
            SIZE,
            config['image'],
            float(config['mass']),
            VELOCITY,
            MAX_VELOCITY,
            trigger_func,
            trigger_weight,
            float(config['initial_vectors']['angle']),
            int(config['max_health']),
            int(config['max_mana']),
            int(config['initial_vectors']['health']),
            int(config['initial_vectors']['mana'])
        )
        return SPRITE

    def spawn_terrain_outline(self, config: dict, trigger_func: Callable | None,
                              trigger_weight: float | None, group: Group, bounds: pg.Rect, facing: int):

        ''' encapsulate the given bounds with smaller rect blocks
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
        last_block: Static_Interactive | None = None

        # 1) topleft --> topright
        curr_pos_x = MIN_X
        while curr_pos_x < MAX_X:
            # set random height/width from within the ranges
            width = randint(CF['min_width'], CF['max_width'])
            height = randint(CF['min_height'], CF['max_height'])

            # ensure no edge overlap by checking for the last block:
            if (curr_pos_x + width) > MAX_X:
                width = (MAX_X - curr_pos_x)
            
            # create a vector to contain the position of the block
            position = Vec2(curr_pos_x, 0.0)

            # get a random color from the given list
            color = self.get_rand_list_elem(CF['color_pool'])
            
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
            color = self.get_rand_list_elem(CF['color_pool'])
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
            color = self.get_rand_list_elem(CF['color_pool'])
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
            curr_pos_x = BLOCK.rect.left + CF['padding']

        # 4) bottomleft --> topright
        curr_pos_y = last_block.rect.top
        while curr_pos_y > MIN_Y:
            width = randint(CF['min_width'], CF['max_width'])
            height = randint(CF['min_height'], CF['max_height'])
            if (curr_pos_y - height) < MIN_Y:
                height = abs(MIN_Y - curr_pos_y)
            color = self.get_rand_list_elem(CF['color_pool'])
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
            curr_pos_y = BLOCK.rect.top + CF['padding']

    def spawn_static_obstacles(self, config: dict, n_obstacles: int, trigger_func: Callable | None,
                               trigger_weight: float | None, group: Group):
        
        ''' obstacle spawning algorithm '''

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
                None, None, None, trigger_func, trigger_weight
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
            if len(pg.sprite.spritecollide(BLOCK, group, False)) == 0:
                # it doesn't collide, swap rect back
                BLOCK.rect = original_rect
                group.add(BLOCK)
                placed_blocks += 1
            else:
                # otherwise, free (delete) the sprite and try again
                del BLOCK
                failed_attempts += 1
                if (failed_attempts > FAIL_LIMIT):
                    msg = f'Fail limit of {FAIL_LIMIT} attempts reached. Too many or too large obstacles.'
                    msg += f'current obstacle count: {placed_blocks} / {n_obstacles}'
                    raise LogicError(msg)

            # make sure the temp rect is not saved in memory
            del inflated_rect

    def loop(self):
        ''' main loop for drawing, checking events and updating the game '''

        # init the timer as the loop is about to start
        self.timer.start_first_segment(ref=None)

        running = True
        while (running):
            # fill the main surface, then the game bounds
            self.window.fill_surface(None)
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

            # refresh the display, applying drawing etc.
            self.window.update()

            # loop through events
            for event in pg.event.get():
                # check if event type matches any triggers
                match (event.type):
                    case pg.QUIT:
                        running = False  # exit the app
        
                    case pg.MOUSEBUTTONDOWN:
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
    # load the game
    APP = PG_App(CF)
    APP.loop()
