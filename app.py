# import cProfile
from copy import deepcopy

# installed library imports
import pygame as pg
## simplify some imports for readability:
from pygame import Color
from pygame.sprite import Group

### local dir imports
from modules.general.exceptions import VersionError
from modules.PG_window import PG_Window
from modules.PG_map import PG_Map
from modules.PG_timer import PG_Timer
from modules.PG_ui_container import UI_Container
from modules.PG_ui_text_box import UI_Text_Box

# import config dicts
from config.cf_global import CF_GLOBAL
from config.cf_window import CF_WINDOW
from config.cf_maps import CF_MAPS
from config.cf_ui import CF_CONTAINERS, CF_BAR_STYLES


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
            config_ui_containers: dict,
            config_ui_bar_styles: dict
        ):

        self.cf_global = config_global
        self.cf_window = config_window
        self.cf_maps = config_maps
        self.cf_ui_containers = config_ui_containers
        self.cf_ui_bar_styles = config_ui_bar_styles

        # store relevant global constants
        self.FPS_LIMIT = int(self.cf_global['fps_limit'])
        self.DEBUG_COLOR = Color(self.cf_global['debug_color'])
        self.DEBUG_COLOR_2 = Color(self.cf_global['debug_color_2'])

        # store chosen ui style dicts

        # create a list of available map keys
        self.valid_cf_maps_keys = []
        for key, _ in self.cf_maps.items():
            self.valid_cf_maps_keys.append(str(key))
        # print(f'loaded maps (config map keys): {self.valid_cf_maps_keys}')

        # create the window
        self.window = PG_Window(self.cf_global, self.cf_window)
        ''' object containing main surface window and bounds '''

        # create the timer
        self.timer = PG_Timer(self.cf_global['fps_limit'], self.cf_global['accurate_timing'])
        ''' pygame specific timer object '''

        self.menu_ui_group = Group()
        ''' group of ui sprites that may be run at any point '''

        # init core app features
        self.timer.block_events(self.cf_global['blocked_events'])
        self.fetch_menu_controls()

        self.looping = True
        self.map_object_loaded = False
        self.run_map_on_launch = True
        self.print_misc_info = True

    def fetch_menu_controls(self):
        ''' fetch and store player controls from the global config '''
        cf_controls = self.cf_global['menu_controls']
        self.MENU_UP      = int(cf_controls['up'])
        self.MENU_LEFT    = int(cf_controls['left'])
        self.MENU_DOWN    = int(cf_controls['down'])
        self.MENU_RIGHT   = int(cf_controls['right'])
        self.MENU_CONFIRM = int(cf_controls['confirm'])
        self.MENU_BACK    = int(cf_controls['back'])

    def init_map(self, cf_maps_key: str):
        if (self.print_misc_info):
            print(f'[APP][init_map]:\n> Call to create map from key "{cf_maps_key}"')

        if (self.map_object_loaded):
            if (self.print_misc_info):
                print(f'Map object "{self.map.name}" already loaded. Deleting it')
            # TODO: Clear up sprites properly, make sure memory is released
            del self.map

        if not (str(cf_maps_key) in self.valid_cf_maps_keys):
            raise ValueError(f'> key error: "{cf_maps_key}" not found in config/cf_maps/CF_MAPS')

        self.map = PG_Map(self, self.cf_maps[cf_maps_key], self.window.map_surface)

        if (self.print_misc_info):
            print(f'> Map object "{self.map.name}" created from config! Setting up map assets ... ')

        self.map.set_up_all(True)
        self.window.set_extended_caption(self.map.name)

        if (self.print_misc_info):
            print(f'> succesfully created and set up map. Returning to loop>')

        self.map_object_loaded = True

    def check_events(self):
        for event in pg.event.get():
            match (event.type):
                case pg.QUIT:
                   self.looping = False
                case pg.MOUSEBUTTONDOWN:
                    print(pg.mouse.get_pos())
                case pg.KEYDOWN:
                    # match keydown event to an action
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
                            self.init_map('map_1', (400, 400))
                        case self.MENU_BACK:
                            pass
                        case _:
                            pass
                case _:
                    pass

    def loop(self):
        ''' main loop for drawing, checking events and updating the game '''

        while (self.looping):
            if (self.run_map_on_launch):
                self.run_map_on_launch = False
                self.init_map(self.valid_cf_maps_keys[0])
                self.map.looping = True

            if (self.map_object_loaded):
                self.map.loop()
            else:
                self.window.fill_surface()
                self.menu_ui_group.update()
                pg.display.update()

                # loop through menu/app events
                self.check_events()
        
        if (self.print_misc_info):
            print('[APP][loop] App closing through main loop')


if __name__ == '__main__':
    # initialize pygame and verify the version before anything else
    pg.init()

    if (pg.__version__ != CF_GLOBAL['req_pg_version']):
        msg = 'run "pip install pygame --upgrade" to upgrade, or change the  '
        msg += 'config (_global.py) to your installed version to try anyway.'
        raise VersionError("Pygame", pg.__version__,
            CF_GLOBAL['req_pg_version'], msg
        )

    # load the app
    APP = PG_App(CF_GLOBAL, CF_WINDOW, CF_MAPS, CF_CONTAINERS, CF_BAR_STYLES)
    # cProfile.run('GAME.loop()')
    APP.loop()
    pg.quit()
