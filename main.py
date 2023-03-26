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

### local dir imports
# general classes
from modules.exceptions import VersionError, ConfigError
# pygame specific classes
from modules.PG_window import PG_Window
from modules.PG_timer import PG_Timer
from modules.PG_ui import Container, Text_Box
# import config dicts
from config._global import GLOBAL as CF_GLOBAL
from config.window import WINDOW as CF_WINDOW
from config.maps import MAPS as CF_MAPS
from config.ui_sprites import UI_SPRITES as CF_UI_SPRITES


class PG_App:
    ''' Singleton app class.
        Takes in config dicts specifying various predefined constants / weights
        * Contains most objects relevant to the app
        * Initializes and sets up pygame objects from the given config
        * Handles game loop and specialized setup-functions
        * attributes that start with cf_ are imported config dicts

        * Conventions defined for the scope of this class:
        * Methods that start with _ are helper methods, or only called once
            E.g.; if the method spawns blocks, config should be a dict from ['map']['BLOCKS'].
        * Methods that start with 'create_' will return the object. 'spawn_' functions are void
        * Methods that take in 'config' as a parameter will refer to the relevant subdict of self.cf.
            The expected config is listed in the method docstring.
    '''

    def __init__(self, 
            config_global: dict,
            config_window: dict,
            config_maps: dict,
            config_UI: dict
        ):

        self.cf_global = config_global
        self.cf_window = config_window
        self.cf_maps = config_maps
        self.cf_UI = config_UI
        
        self.MAP_KEYS = []
        for key, _ in self.cf_maps.items():
            self.MAP_KEYS.append(str(key))
        print(f'loaded map config keys: {self.MAP_KEYS}')

        # store chosen ui style dicts
        self.cf_container_style: dict = self.cf_UI['CONTAINERS'][str(self.cf_global['container_style'])]
        self.cf_textbox_style: dict = self.cf_UI['TEXTBOXES'][str(self.cf_global['textbox_style'])]

        # store global constants
        self.DEBUG_COLOR = Color(self.cf_global['debug_color'])
        self.FPS_LIMIT = int(self.cf_global['fps_limit'])

        # create the window
        self.window = PG_Window(self.cf_global, self.cf_window)
        ''' object containing main surface window and bounds '''

        # create the timer
        self.timer = PG_Timer(self.cf_global['fps_limit'], self.cf_global['accurate_timing'])
        ''' pygame specific timer object '''

        # 
        self.container_group = Group()
        ''' group of ui containers. Contains their own groups of children '''

        self.set_up_ui()
        self.fetch_menu_controls()
        self.ban_events()
        self.app_is_running = True
        self.map_is_active = False

    def set_up_map(self, map_name: str, player_pos: tuple[int, int]):
        ''' bundle of function calls to initialize the map, player and controls '''

        if not str(map_name) in self.MAP_KEYS:
            raise ValueError(f'map "{map_name}" not found')

        self.window.create_map(self.cf_maps['map_1'])
        self.window.map.set_up_terrain()
        self.window.map.spawn_player(player_pos)
        self.fetch_player_controls()

        if not (self.timer.first_init_done):
            self.timer.start_first_segment(self.window.map.name)
        else:
            self.timer.new_segment(self.window.map.name, True)

        self.map_is_active = True

    def fetch_menu_controls(self):
        ''' fetch and store player controls from the global config '''
        cf_controls = self.cf_global['menu_controls']
        self.MENU_UP =      int(cf_controls['up'])
        self.MENU_LEFT =    int(cf_controls['left'])
        self.MENU_DOWN =    int(cf_controls['down'])
        self.MENU_RIGHT =   int(cf_controls['right'])
        self.MENU_CONFIRM = int(cf_controls['confirm'])
        self.MENU_BACK =    int(cf_controls['back'])

    def fetch_player_controls(self):
        ''' fetch and store player controls from the map '''
        cf_controls = self.window.map.get_player_controls()
        self.STEER_UP =     int(cf_controls['steer_up'])
        self.STEER_LEFT =   int(cf_controls['steer_left'])
        self.STEER_DOWN =   int(cf_controls['steer_down'])
        self.STEER_RIGHT =  int(cf_controls['steer_right'])
        self.HALT =         int(cf_controls['halt'])
        self.LOCK =         int(cf_controls['lock'])

    def get_current_player_angle(self):
        return self.window.map.player.get_angle()

    def set_up_ui(self):
        ''' specialized, run-once function for creating the game ui '''

        # create bottom info panel container
        # set width to the size of the map
        # set size and pos to match the available padded bottom space
        position = self.window.map_rect.bottomleft
        width = self.window.map_rect.w
        height = (self.window.height - self.window.map_rect.h - self.window.map_rect.top)

        if (height < 40):
            print("not enough vertical padding to fit the UI. Increase ['map']['padded_bounds'].")
            return

        BOTTOM_PANEL = Container(
            self.window.surface,
            (width, height),
            position,
            Color(self.cf_container_style['color']),
            Color(self.cf_container_style['border_color']),
            int(self.cf_container_style['border_width']),
            "right",
            "left_right",
            int(self.cf_container_style['children_padding']),
            int(self.cf_container_style['separator_width']),
            Color(self.cf_container_style['separator_color'])
        )

        self.container_group.add(BOTTOM_PANEL)
        
        FPS_FRAME = Text_Box(
            Color(self.cf_textbox_style['text_bg_color']),
            str('FPS: '),
            self.timer.get_fps_int,
            str(self.cf_textbox_style['font_path']),
            int(self.cf_textbox_style['font_size']),
            Color(self.cf_textbox_style['font_color']),
            self.cf_textbox_style['font_antialias']
        )

        DURATION_FRAME = Text_Box(
            Color(self.cf_textbox_style['text_bg_color']),
            str('Time: '),
            self.timer.get_duration,
            str(self.cf_textbox_style['font_path']),
            int(self.cf_textbox_style['font_size']),
            Color(self.cf_textbox_style['font_color']),
            self.cf_textbox_style['font_antialias']
        )

        ANGLE_FRAME = Text_Box(
            Color(self.cf_textbox_style['text_bg_color']),
            str('Angle: '),
            self.get_current_player_angle,
            str(self.cf_textbox_style['font_path']),
            int(self.cf_textbox_style['font_size']),
            Color(self.cf_textbox_style['font_color']),
            self.cf_textbox_style['font_antialias']
        )

        BOTTOM_PANEL.children.add([FPS_FRAME, DURATION_FRAME, ANGLE_FRAME])
        # BOTTOM_PANEL.verify_children()

    def debug__print_player_velocity(self):
        if (self.player.velocity.y == self.player.MAX_VELOCITY.y):
            print("terminal velocity reached @ \n")
            print(f'ms: {self.timer.total_time}')
            print(f'secs: {self.timer.active_segment.get_duration_formatted()}')

    def debug__sprite_mask_outline(self, sprite: Sprite):
        ''' visualize mask outline by drawing lines along the set pixel points '''
        p_list = sprite.mask.outline()  # get a list of cooordinates from the mask outline
        pg.draw.lines(sprite.image, self.debug_color, 1, p_list)

    def debug__draw_poking_stick(self, sprite, len: float, width: int):
        p1 = Vec2(sprite.position)
        p2 = Vec2(sprite.position + len*sprite.velocity)
        # p2.scale_to_length(len)
        # print(p1, p2)
        pg.draw.line(self.window.map_surface, self.debug_color, p1, p2, width)

    def ban_events(self):
        ''' blocks some unused events from entering the event queue
            * saves some time when iterating over pg.event.get()
        '''
        pg.event.set_blocked(pg.MOUSEMOTION)
        pg.event.set_blocked(pg.MOUSEBUTTONUP)
        pg.event.set_blocked(pg.MOUSEBUTTONDOWN)
        pg.event.set_blocked(pg.TEXTINPUT)

    def menu_loop_events(self):
        for event in pg.event.get():
            match (event.type):
                case pg.QUIT:
                   self.app_is_running = False
                case pg.MOUSEBUTTONDOWN:
                    print(pg.mouse.get_pos())
                case pg.KEYDOWN:
                    # match keydown event to an action, or pass
                    match (event.key):
                        case self.MENU_UP:
                            pass
                        case self.MENU_DOWN:
                            pass
                        case self.MENU_LEFT:
                            pass
                        case self.MENU_RIGHT:
                            pass
                        case self.MENU_CONFIRM:
                            self.set_up_map('map_1', (400, 400))
                        case self.MENU_BACK:
                            pass
                        case _:
                            pass

    def loop_events(self):
        ''' loop all queued events and check for any trigger matches '''

        for event in pg.event.get():
            # check if event type matches any triggers
            match (event.type):
                case pg.QUIT:
                    self.app_is_running = False
                    self.map_is_active = False
                case pg.MOUSEBUTTONDOWN:
                    print(pg.mouse.get_pos())
                case pg.KEYDOWN:
                    # match keydown event to an action, or pass
                    match (event.key):
                        case self.STEER_UP:
                            self.window.map.player.direction.y -= self.window.map.player.handling
                        case self.STEER_DOWN:
                            self.window.map.player.direction.y += self.window.map.player.handling
                        case self.STEER_LEFT:
                            self.window.map.player.direction.x -= self.window.map.player.handling
                        case self.STEER_RIGHT:
                            self.window.map.player.direction.x += self.window.map.player.handling
                        case self.HALT:
                            self.window.map.player.halt += 1.0
                        case self.LOCK:
                            pass
                        case _:
                            pass
                case pg.KEYUP:
                    # match keydown event to an action, or pass
                    match (event.key):
                        case self.STEER_UP:
                            self.window.map.player.direction.y += self.window.map.player.handling
                        case self.STEER_DOWN:
                            self.window.map.player.direction.y -= self.window.map.player.handling
                        case self.STEER_LEFT:
                            self.window.map.player.direction.x += self.window.map.player.handling
                        case self.STEER_RIGHT:
                            self.window.map.player.direction.x -= self.window.map.player.handling
                        case self.HALT:
                            self.window.map.player.halt -= 1.0
                        case self.LOCK:
                            pass
                        case _:
                            pass
                case _:
                    # print(event.type)
                    # print(event)
                    pass

    def loop(self):
        ''' main loop for drawing, checking events and updating the game '''
        
        while (self.app_is_running):
            # the map not be active. this keeps the program active until exited
            self.window.fill_surface()
            pg.display.update()

            # loop through menu events
            self.menu_loop_events()

            # if a map was initiated by the menu, launch the main loop
            while (self.map_is_active):
                # fill the main surface, then the game bounds
                self.window.map.fill_surface()

                # draw map blocks
                self.window.map.block_group.draw(self.window.map_surface)

                # draw the player
                self.window.map.player_group.draw(self.window.map_surface)

                # update + draw the ui (both are done through update)
                self.container_group.update()

                # refresh the display, applying drawing etc.
                pg.display.update()

                # loop through events
                self.loop_events()

                # now that events are read, update sprites before next frame
                self.window.map.player_group.update()

                # update the timer. Also limits the framerate if set
                self.timer.update()


if __name__ == '__main__':

    # initialize pygame and verify the version before anything else
    pg.init()

    if (pg.__version__ != CF_GLOBAL['req_pg_version']):
        msg = 'run "pip install pygame --upgrade" to upgrade, '
        msg += 'or change the config to your current version to try anyway.'
        raise VersionError("Pygame", pg.__version__,
            CF_GLOBAL['req_pg_version'], msg
        )

    # load the game
    GAME = PG_App(CF_GLOBAL, CF_WINDOW, CF_MAPS, CF_UI_SPRITES)
    GAME.loop()
