# default python library imports
from typing import Callable     # type hint for function pointers
from random import randint, uniform

# library imports
import pygame as pg
from pygame.math import Vector2 as Vec2

# local imports
## general:
from config import CONFIG
from modules.exceptions import VersionError, LogicError
from modules.timing import Timer
## pygame specific:
from modules.PG_window import PG_Window
from modules.PG_shapes import PG_Rect
from modules.PG_ui import PG_Text_Box, PG_Text_Box_Child
# sprites:
from modules.PG_sprites import Static_Interactive


class PG_Wrapper:
    ''' singleton wrapper for the app
        * initializes and sets up pygame
        * reads and distributes settings from the given config
        * contains all objects relevant to the app
    '''
    def __init__(self, config: dict[str, any]):
        pg.init()
        if not (str(pg.__version__) == config['misc']['req_pygame_version']):
            raise VersionError("Pygame", str(pg.__version__), config['misc']['req_pygame_version'])

        self.cf = config
        self.window = PG_Window(
            config['window']['caption'],
            config['window']['width'],
            config['window']['height'],
            config['window']['bounds_padding'],
            config['window']['fill_color']
        )
        # misc
        self.clock = pg.time.Clock()
        self.max_fps: int = config['misc']['max_fps']
        self.timer = Timer()

        # set up UI
        self.ui_tbox_core: list[PG_Text_Box] = []
        self.ui_tbox_children: list[PG_Text_Box_Child] = []
        
        UI_TIME = self.create_tbox_core("Time: ", 0, 0, False, self.timer.get_active_segment_time)
        time_pos = (self.cf['ui']['default_padding'],
                    self.window.height - self.cf['ui']['default_padding'])
        UI_TIME.re.bottomleft = time_pos
        self.ui_tbox_core.append(UI_TIME)
        UI_FPS = self.create_tbox_child("FPS: ", UI_TIME, 'right', self.get_fps)
        self.ui_tbox_children.append(UI_FPS)

        self.terrain = pg.sprite.Group()
        self.create_terrain_outline()
        self.create_obstacles()

    def create_terrain_outline(self):
        ''' encapsulated the surface bounds with rects '''
        CF = self.cf['environment']['terrain_block']

        min_x = self.window.bounds['min_x']
        max_x = self.window.bounds['max_x']
        min_y = self.window.bounds['min_y']
        max_y = self.window.bounds['max_y']
        
        # topleft --> topright
        curr_pos_y = 0
        curr_pos_x = min_x
        last_block: Static_Interactive
        while curr_pos_x < max_x:
            # set random height/width from within the ranges
            width = randint(CF['min_width'], CF['max_width'])
            height = randint(CF['min_height'], CF['max_height'])
            # ensure no overlap: 
            if (curr_pos_x + width) > max_x:
                width = max_x - curr_pos_x
            POS = Vec2(curr_pos_x, curr_pos_y)
            BLOCK = Static_Interactive(
                self.window,
                CF['color_pool'][randint(1, len(CF['color_pool'])-1)],
                POS,
                (width, height),
                None, None, None, None, None
            )
            last_block = BLOCK
            self.terrain.add(BLOCK)
            curr_pos_x = BLOCK.rect.right
        
        # topright --> bottomright
        curr_pos_y = last_block.rect.bottom
        curr_pos_x = max_x
        while curr_pos_y < max_y:
            # set random height/width from within the ranges
            width = randint(CF['min_width'], CF['max_width'])
            height = randint(CF['min_height'], CF['max_height'])
            # ensure no overlap: 
            if (curr_pos_y + height) > max_y:
                height = max_y - curr_pos_y 
            POS = Vec2(curr_pos_x, curr_pos_y)
            BLOCK = Static_Interactive(
                self.window,
                CF['color_pool'][randint(1, len(CF['color_pool'])-1)],
                POS,
                (width, height),
                None, None, None, None, None
            )
            BLOCK.rect.right = curr_pos_x
            last_block = BLOCK
            self.terrain.add(BLOCK)
            curr_pos_y = BLOCK.rect.bottom

        # bottomright --> bottomleft
        curr_pos_x = last_block.rect.left
        curr_pos_y = max_y
        while curr_pos_x > min_x:
            # set random height/width from within the ranges
            width = randint(CF['min_width'], CF['max_width'])
            height = randint(CF['min_height'], CF['max_height'])
            # ensure no overlap: 
            if (curr_pos_x - width) < min_x:
                width = abs(min_x - curr_pos_x)
            POS = Vec2()
            BLOCK = Static_Interactive(
                self.window,
                CF['color_pool'][randint(1, len(CF['color_pool'])-1)],
                POS,
                (width, height),
                None, None, None, None, None
            )
            BLOCK.rect.bottom = curr_pos_y
            BLOCK.rect.right = curr_pos_x
            last_block = BLOCK
            self.terrain.add(BLOCK)
            curr_pos_x = BLOCK.rect.left

        # bottomleft --> topright
        curr_pos_x = min_x
        curr_pos_y = last_block.rect.top
        while curr_pos_y > min_y:
            # set random height/width from within the ranges
            width = randint(CF['min_width'], CF['max_width'])
            height = randint(CF['min_height'], CF['max_height'])
            # ensure no overlap: 
            if (curr_pos_y - width) < min_y:
                width = abs(min_y - curr_pos_y)
            POS = Vec2()
            BLOCK = Static_Interactive(
                self.window,
                CF['color_pool'][randint(1, len(CF['color_pool'])-1)],
                POS,
                (width, height),
                None, None, None, None, None
            )
            BLOCK.rect.left = curr_pos_x
            BLOCK.rect.bottom = curr_pos_y
            last_block = BLOCK
            self.terrain.add(BLOCK)
            curr_pos_y = BLOCK.rect.top

    def create_obstacles(self):
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
            width = randint(CF['min_width'], CF['max_width'])
            height = randint(CF['min_height'], CF['max_height'])
            POS = Vec2(self.window.get_rand_x_inbound(width),
                       self.window.get_rand_y_inbound(height))
            BLOCK = Static_Interactive(
                self.window,
                CF['color_pool'][randint(1, len(CF['color_pool'])-1)],
                POS,
                (width, height),
                None, None, None, None, None
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
            if len(pg.sprite.spritecollide(BLOCK, self.terrain, False)) == 0:
                # it doesn't collide, swap rect back
                BLOCK.rect = original_rect
                self.terrain.add(BLOCK)
                i += 1
            else:
                # otherwise, simply try again with a new block size and position
                failed += 1
                if (failed > FAIL_LIMIT):
                    msg = f'Fail limit of {FAIL_LIMIT} attempts reached. Too many or too large obstacles.'
                    msg += f'current obstacle count: {i} / {n_obstacles}'
                    raise LogicError(msg)

    def get_fps(self):
        return round(self.clock.get_fps())

    def create_tbox_core(self, content: str, x: int, y: int, is_static: bool, getter_func: Callable | None):
        ''' create tbox core using default settings '''
        return PG_Text_Box(
            self.window,
            content,
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
        ''' create tbox core using default settings '''
        return PG_Text_Box_Child(
            self.window,
            content,
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
            self.window.fill()

            # update objects for the next frame
            for elem in self.ui_tbox_core:
                elem.update()

            for elem in self.ui_tbox_children:
                elem.update()
            
            self.terrain.draw(self.window.surface)

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
    GAME = PG_Wrapper(CONFIG)
    GAME.loop()
