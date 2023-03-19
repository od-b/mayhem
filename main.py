# default python library imports
from typing import Callable     # type hint for function pointers
from random import randint, uniform
from copy import deepcopy

# library imports
import pygame as pg
from pygame.math import Vector2 as Vec2
from pygame.sprite import Group

# local imports
## general:
from config import CONFIG as WRAPPER_CONFIG
from modules.exceptions import VersionError, LogicError
from modules.timing import Timer
## pygame specific:
from modules.PG_window import PG_Window
from modules.PG_shapes import PG_Rect
from modules.PG_ui import PG_Text_Box, PG_Text_Box_Child
# sprites:
from modules.PG_sprites import Static_Interactive


class PG_App:
    ''' app class, may serve multiple app instances
        * takes in a config dict specifying various constants and parameters
        * contains most objects relevant to the app
        * initializes and sets up pygame objects from the given config
        * contains game loop, specialized setup-functions
    '''
    def __init__(self, CONFIG: dict[str, any]):
        self.cf = deepcopy(CONFIG)
        # load and store a copy of the CONFIG
        # certain settings in cf may be modified during runtime, however CONFIG
        # should remain unchanged to avoid change across app instances
        self.window = PG_Window(
            self.cf['window']['caption'],
            self.cf['window']['width'],
            self.cf['window']['height'],
            self.cf['window']['bounds_padding'],
            self.cf['window']['fill_color'],
            self.cf['window']['bounds_fill_color'],
        )
        # the timer is not pygame specific and depends on a clock for updates
        # pygame clock
        self.clock = pg.time.Clock()
        self.timer = Timer()

        # misc
        self.max_fps: int = self.cf['misc']['max_fps']

        # set up UI
        self.ui_tbox_core: list[PG_Text_Box] = []
        self.ui_tbox_children: list[PG_Text_Box_Child] = []
        
        # create the 'root' element and manually set its position to bottom left (+default padding),
        UI_TIME = self.create_tbox_core("Time: ", 0, 0, False, self.get_duration)
        UI_TIME.re.bottomleft = (
            self.cf['ui']['default_padding'],
            self.window.height - self.cf['ui']['default_padding'])
        self.ui_tbox_core.append(UI_TIME)
        
        # create the fps frame as a child of time, located to the right
        UI_FPS = self.create_tbox_child("FPS: ", UI_TIME, 'right', self.get_fps_int)
        self.ui_tbox_children.append(UI_FPS)

        self.update_group = Group()
        ''' group of sprites that are to be updated '''
        self.draw_group = Group()
        ''' group of sprites that are to be drawn '''

        # outline the game area with blocks
        self.create_terrain_outline(None, None, self.draw_group, self.window.bounds)
        # place obstacles within the game area
        self.create_static_obstacles(None, None, self.draw_group)

    def get_rand_list_elem(self, list: list):
        ''' get random elem from non-empty list '''
        return list[randint(1, len(list)-1)]

    def get_duration(self):
        ''' to allow referencing the function before first segment is initialized '''
        return self.timer.active_segment.get_duration_formatted()

    def get_fps_int(self):
        ''' get fps, rounded to the nearest integer '''
        return round(self.clock.get_fps(), None)

    def create_terrain_outline(self, trigger_func: Callable | None, trigger_weight: float | None, group: Group, bounds: dict):
        ''' encapsulate the given bounds with rects '''
        # constant declarations for readability and convenience:
        CF = self.cf['environment']['terrain_block']
        MIN_X = bounds['min_x']
        MAX_X = bounds['max_x']
        MIN_Y = bounds['min_y']
        MAX_Y = bounds['max_y']
        
        # below are four loops that together will outline the entire bounds
        last_block: Static_Interactive | None = None  # for remembering the last block placed

        # 1) topleft --> topright
        curr_pos_y = MIN_Y
        curr_pos_x = MIN_X
        while curr_pos_x < MAX_X:
            # set random height/width from within the ranges
            width = randint(CF['min_width'], CF['max_width'])
            height = randint(CF['min_height'], CF['max_height'])
            # ensure no overlap: 
            if (curr_pos_x + width) > MAX_X:
                width = MAX_X - curr_pos_x
            position = Vec2(curr_pos_x, curr_pos_y)
            color = self.get_rand_list_elem(CF['color_pool'])
            BLOCK = Static_Interactive(
                self.window, color, position, (width, height),
                None, None, None, trigger_func, trigger_weight
            )
            last_block = BLOCK
            group.add(BLOCK)
            curr_pos_x = BLOCK.rect.right
        
        # 2) topright --> bottomright
        curr_pos_y = last_block.rect.bottom
        curr_pos_x = MAX_X
        while curr_pos_y < MAX_Y:
            width = randint(CF['min_width'], CF['max_width'])
            height = randint(CF['min_height'], CF['max_height'])
            if (curr_pos_y + height) > MAX_Y:
                height = MAX_Y - curr_pos_y 
            position = Vec2(0.0, curr_pos_y)
            color = self.get_rand_list_elem(CF['color_pool'])
            BLOCK = Static_Interactive(
                self.window, color, position, (width, height),
                None, None, None, trigger_func, trigger_weight
            )
            BLOCK.rect.right = curr_pos_x
            last_block = BLOCK
            group.add(BLOCK)
            curr_pos_y = BLOCK.rect.bottom

        # 3) bottomright --> bottomleft
        curr_pos_x = last_block.rect.left
        curr_pos_y = MAX_Y
        while curr_pos_x > MIN_X:
            # set random height/width from within the ranges
            width = randint(CF['min_width'], CF['max_width'])
            height = randint(CF['min_height'], CF['max_height'])
            # ensure no overlap: 
            if (curr_pos_x - width) < MIN_X:
                width = abs(MIN_X - curr_pos_x)
            position = Vec2()
            color = self.get_rand_list_elem(CF['color_pool'])
            BLOCK = Static_Interactive(
                self.window, color, position, (width, height),
                None, None, None, trigger_func, trigger_weight
            )
            BLOCK.rect.bottom = curr_pos_y
            BLOCK.rect.right = curr_pos_x
            last_block = BLOCK
            group.add(BLOCK)
            curr_pos_x = BLOCK.rect.left

        # 4) bottomleft --> topright
        curr_pos_x = MIN_X
        curr_pos_y = last_block.rect.top
        while curr_pos_y > MIN_Y:
            width = randint(CF['min_width'], CF['max_width'])
            height = randint(CF['min_height'], CF['max_height'])
            if (curr_pos_y - height) < MIN_Y:
                height = abs(MIN_Y - curr_pos_y)
            position = Vec2()
            color = self.get_rand_list_elem(CF['color_pool'])
            BLOCK = Static_Interactive(
                self.window, color, position, (width, height),
                None, None, None, trigger_func, trigger_weight
            )
            BLOCK.rect.left = curr_pos_x
            BLOCK.rect.bottom = curr_pos_y
            last_block = BLOCK
            group.add(BLOCK)
            curr_pos_y = BLOCK.rect.top

    def create_static_obstacles(self, trigger_func: Callable | None, trigger_weight: float | None, group: Group):
        ''' obstacle spawning algorithm '''
        n_obstacles = self.cf['environment']['n_obstacles']
        adjusted_width = self.cf['spaceship']['width'] + self.cf['environment']['obstacle_padding']
        adjusted_height = self.cf['spaceship']['height'] + self.cf['environment']['obstacle_padding']
        # how many obstacle placement attempts to allow before deciding a solution can't be found:
        FAIL_LIMIT = self.cf['environment']['obstacle_placement_attempt_limit']
        # relevant dict for readability:
        CF = self.cf['environment']['obstacle_block']

        i = 0
        failed = 0
        while i < n_obstacles:
            # set random height/width from within the ranges
            color = CF['color_pool'][randint(1, len(CF['color_pool'])-1)]
            width = randint(CF['min_width'], CF['max_width'])
            height = randint(CF['min_height'], CF['max_height'])
            position = Vec2(
                self.window.get_rand_x_inbound(width),
                self.window.get_rand_y_inbound(height)
            )
            BLOCK = Static_Interactive(
                self.window, color, position, (width, height),
                None, None, None, trigger_func, trigger_weight
            )
            # the block is now created, but there's 2 potential problems:
            # 1) the block might overlap other blocks
            # 2) we don't want to lock the spaceship in by bad rng

            # solution: create a copy of the rect and inflate it using the spaceship size + set padding
            inflated_rect = BLOCK.rect.copy().inflate(adjusted_width, adjusted_height)
            # temporarily swap the rect with the one of the block, while saving the original
            # this is to allow for easy and fast spritecollide checking
            original_rect = BLOCK.rect.copy()
            BLOCK.rect = inflated_rect

            # if the block + spaceship rect doesn't collide with any terrain, add it to the group
            if len(pg.sprite.spritecollide(BLOCK, group, False)) == 0:
                # it doesn't collide, swap rect back
                BLOCK.rect = original_rect
                group.add(BLOCK)
                i += 1
            else:
                # otherwise, free (delete) the sprite and try again
                del BLOCK
                failed += 1
                if (failed > FAIL_LIMIT):
                    msg = f'Fail limit of {FAIL_LIMIT} attempts reached. Too many or too large obstacles.'
                    msg += f'current obstacle count: {i} / {n_obstacles}'
                    raise LogicError(msg)

    def create_tbox_core(self, content: str, x: int, y: int, is_static: bool, getter_func: Callable | None):
        ''' create textbox core using default settings '''
        return PG_Text_Box(
            self.window, content,
            self.cf['fonts']['semibold'],
            self.cf['ui']['default_font_size'],
            self.cf['ui']['apply_aa'],
            self.cf['ui']['text_color_light'], 
            self.cf['ui']['default_bg_color'],
            self.cf['ui']['default_border_color'],
            self.cf['ui']['default_border_width'],
            getter_func, x, y, is_static
        )

    def create_tbox_child(self, content: str, parent: PG_Text_Box | PG_Rect, alignment: str, getter_func: Callable | None):
        ''' create textbox child using default settings '''
        return PG_Text_Box_Child(
            self.window, content,
            self.cf['fonts']['semibold'],
            self.cf['ui']['default_font_size'],
            self.cf['ui']['apply_aa'],
            self.cf['ui']['text_color_light'], 
            self.cf['ui']['default_bg_color'],
            self.cf['ui']['default_border_color'],
            self.cf['ui']['default_border_width'],
            getter_func, parent, alignment,
            self.cf['ui']['default_padding'],
        )

    def loop(self):
        ''' main loop for drawing, checking events and updating the game '''
        running: bool = True

        # init the timer before first loop
        self.timer.start_first_segment(pg.time.get_ticks(), 1)

        while (running):
            # fill the window before drawing/rendering
            self.window.fill_surface(None)
            self.window.bounds_rect.draw()

            # update objects for the next frame
            for elem in self.ui_tbox_core:
                elem.update()

            for elem in self.ui_tbox_children:
                elem.update()
            
            self.draw_group.draw(self.window.surface)

            # refresh the display, applying drawing etc.
            self.window.update()

            # loop through events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False  # exit the app
    
                elif event.type == pg.MOUSEBUTTONDOWN:
                    # mouse click
                    # MOUSE_POS = pg.mouse.get_pos()
                    # print(MOUSE_POS)
                    pass

                elif (event.type == pg.KEYDOWN):
                    # match keydown event to an action, or pass
                    match (event.key):
                        case pg.K_ESCAPE:
                            running = False
                        case _:
                            pass

            # limit the framerate
            self.clock.tick(self.max_fps)
            self.timer.update(pg.time.get_ticks())

if __name__ == '__main__':
    # initialize pygame
    pg.init()

    # verify pygame version
    req_pg_version = str(WRAPPER_CONFIG['misc']['req_pygame_version'])
    if not (str(pg.__version__) == req_pg_version):
        raise VersionError("Pygame", str(pg.__version__), req_pg_version)

    # load the game
    APP = PG_App(WRAPPER_CONFIG)
    APP.loop()
