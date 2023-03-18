# default python library imports
from typing import Callable     # type hint for function pointers

# pygame 2.1.2 --> print(pygame.__version__)
import pygame as pg
import sys
# local imports
## general:
from exceptions import VersionError
from config import CONFIG
from timing import Timer
## pygame specific:
from PG_window import PG_Window
from PG_shapes import PG_Rect
from PG_ui import PG_Text_Box, PG_Text_Box_Child


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
            config['window']['surface_offset_x'],
            config['window']['surface_offset_y'],
            config['window']['fill_color']
        )
        # misc
        self.clock = pg.time.Clock()
        self.max_fps: int = config['misc']['max_fps']
        self.timer = Timer()

        # set up UI
        self.ui_tbox_core: list[PG_Text_Box] = []
        self.ui_tbox_children: list[PG_Text_Box_Child] = []
        
        UI_TIME = self.create_tbox_core("Time: ", 100, 100, False, self.timer.get_active_segment_time)
        self.ui_tbox_core.append(UI_TIME)
        UI_FPS = self.create_tbox_child("FPS: ", UI_TIME, 'bottom', self.get_fps)
        self.ui_tbox_children.append(UI_FPS)

        self.print_setup()
    
    def get_fps(self):
        return round(self.clock.get_fps())

    def print_setup(self):
        msg = f'{self.window}\n'
        msg += '< Misc:\n'
        msg += f'  max_fps="{self.max_fps}"'
        print(msg+'\n>')
    
    def create_tbox_core(self, content: str, x: int, y: int, is_static: bool, getter_func: Callable | None):
        ''' create tbox core using default settings '''
        return PG_Text_Box(
            self.window,
            content,
            self.cf['fonts']['semibold'],
            self.cf['ui']['default_font_size'],
            self.cf['ui']['apply_aa'],
            self.cf['ui']['text_color_dim'], 
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
            self.cf['ui']['default_child_offset'],
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
