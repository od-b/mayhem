# default python library imports
from typing import Callable     # type hint for function pointers
from random import randint, uniform

# library imports
import pygame as pg
from pygame.math import Vector2 as Vec2
from pygame.sprite import Group

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

    def __init__(self, config: dict[str, any]):
        self.cf = config
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

        self.draw_group = Group()
        ''' group of sprites that are to be drawn '''

        # outline the game area with blocks:
        self.spawn_terrain_outline(None, None, self.draw_group, self.window.bounds)

        # place obstacles within the game area, adjusted for player size + settings:
        w_padding = int(self.cf['player']['width'] + self.cf['environment']['obstacle_padding'])
        h_padding = int(self.cf['player']['height'] + self.cf['environment']['obstacle_padding'])
        self.spawn_static_obstacles(None, None, self.draw_group, w_padding, h_padding)

        # create the player sprite:
        self.player = self.create_controllable_sprite(self.cf['player'], None, None)
        self.draw_group.add(self.player)
        self.update_group.add(self.player)

    def _set_up_ui_constants(self) -> tuple[PG_Text_Box | PG_Text_Box_Child, ...]:
        ''' set up UI constants, objects that will exist until the app is exited '''

        # create as a list
        elems = []

        # create the 'root' element and manually set its position to bottom left (+default padding),
        UI_TIME = self.create_tbox_core("Time: ", 0, 0, False, self.timer.get_duration)
        UI_TIME.re.bottomleft = (
            self.cf['ui']['default_padding'],
            self.window.height - self.cf['ui']['default_padding'])
        elems.append(UI_TIME)

        # create the fps frame as a child of time, located to the right
        UI_FPS = self.create_tbox_child("FPS: ", UI_TIME, 'right', self.timer.get_fps_int)
        elems.append(UI_FPS)

        # return as a tuple
        return tuple(elems)

    def _pygame_init(self):
        ''' initialize pygame and verify pygame version '''

        pg.init()
        pg_version = str(pg.__version__)
        req_pg_version = str(self.cf['general']['req_pygame_version'])
        if not (pg_version == req_pg_version):
            raise VersionError("Pygame", pg_version, req_pg_version)

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

    def create_tbox_child(self, content: str, parent: PG_Text_Box | PG_Rect, alignment: str,
                          getter_func: Callable | None):
        
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

    def get_rand_list_elem(self, list: list):
        ''' get random elem from non-empty list '''
        return list[randint(1, len(list)-1)]

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

    def spawn_terrain_outline(self, trigger_func: Callable | None, trigger_weight: float | None,
                              group: Group, bounds: dict):

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
                self.window, color, position, (width, height), None,
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
                self.window, color, position, (width, height), None,
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
                self.window, color, position, (width, height), None,
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
                self.window, color, position, (width, height), None,
                None, None, None, trigger_func, trigger_weight
            )
            BLOCK.rect.left = curr_pos_x
            BLOCK.rect.bottom = curr_pos_y
            last_block = BLOCK
            group.add(BLOCK)
            curr_pos_y = BLOCK.rect.top

    def spawn_static_obstacles(self, trigger_func: Callable | None, trigger_weight: float | None,
                                group: Group, width_padding: int, height_padding: int):
        
        ''' obstacle spawning algorithm '''

        n_obstacles = self.cf['environment']['n_obstacles']
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
                self.window, color, position, (width, height), None,
                None, None, None, trigger_func, trigger_weight
            )
            # the block is now created, but there's 2 potential problems:
            # 1) the block might overlap other blocks
            # 2) we don't want to lock the spaceship in by bad rng

            # solution: create a copy of the rect and inflate it using the spaceship size + set padding
            inflated_rect = BLOCK.rect.copy().inflate(width_padding, height_padding)
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

    def loop(self):
        ''' main loop for drawing, checking events and updating the game '''

        running: bool = True

        # init the timer before first loop
        self.timer.start_first_segment(ref=None)

        while (running):
            # fill the main surface, then the game bounds
            self.window.fill_surface(None)
            self.window.bounds_rect.draw_background()

            # draw sprites
            self.draw_group.draw(self.window.surface)

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
