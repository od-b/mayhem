# import cProfile
from warnings import warn as warnings_warn

# installed library imports
import pygame as pg
from pygame import Color
from pygame.sprite import Sprite, Group, GroupSingle

# config dicts
from config.cf_global import CF_GLOBAL
from config.cf_window import CF_WINDOW
from config.cf_timer import CF_TIMER
from config.cf_menu import CF_MENU
from config.cf_maps import CF_MAPS

# local modules
from modules.PG_window import PG_Window
from modules.PG_map import PG_Map
from modules.PG_timer import PG_Timer

from modules.PG_ui_container import (
    UI_Sprite_Container,
    UI_Container_Wrapper,
    UI_Sprite_Container_Filled,
    UI_Container_Single,
    UI_Container_Single_Filled
)
from modules.PG_ui_text_box import UI_Text_Box


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
            cf_global: dict,
            cf_window: dict,
            cf_timer: dict,
            cf_menu: dict,
            cf_maps: dict
        ):

        self.cf_global = cf_global
        self.cf_window = cf_window
        self.cf_timer = cf_timer
        self.cf_menu = cf_menu
        self.cf_maps = cf_maps

        # store relevant global constants
        self.FPS_LIMIT = int(self.cf_global['fps_limit'])
        self.DEBUG_COLOR = Color(self.cf_global['debug_color'])
        self.DEBUG_COLOR_2 = Color(self.cf_global['debug_color_2'])

        # create a list of available map keys
        self.valid_cf_maps_keys = []
        for key, _ in self.cf_maps.items():
            self.valid_cf_maps_keys.append(str(key))
        # print(f'loaded maps (config map keys): {self.valid_cf_maps_keys}')

        # create the window
        self.window = PG_Window(self.cf_global, self.cf_window)
        ''' object containing main surface window and bounds '''

        # create the timer
        self.timer = PG_Timer(self.cf_global, self.cf_timer)
        ''' pygame specific timer object '''

        self.timer.block_events(self.cf_global['blocked_events'])
        self.fetch_menu_controls()

        self.menu_wrapper_group = GroupSingle()
        ''' group of ui sprites that may be run at any point '''
        
        self.menu_title_text = str("<GameName>")

        self.looping = True
        self.map_object_loaded = False
        self.run_map_on_launch = False
        self.print_misc_info = True

        self.set_up_menu()

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

        # create the map object as an attribute of self
        self.map = PG_Map(self.cf_global, self.cf_maps[cf_maps_key], self.timer, self.window.map_surface)

        if (self.print_misc_info):
            print(f'> Map object "{self.map.name}" created from config! Setting up map assets ...')

        # set up the map
        self.map.set_up_all(True)
        self.window.set_extended_caption(self.map.name)

        if (self.print_misc_info):
            print(f'> succesfully created and set up map. Returning ...')

        self.map_object_loaded = True

    def check_events(self):
        for event in pg.event.get():
            match (event.type):
                case pg.KEYDOWN:
                    # TODO: MENU CONTROLS
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
                            pass
                        case self.MENU_BACK:
                            pass
                        case _:
                            pass
                case pg.QUIT:
                   self.looping = False
                case _:
                    pass

    def set_up_menu(self):
        subcontainers_left = self.cf_menu['n_subcontainers']
        cf_containers = self.cf_menu['containers']
        cf_text_box_styles = self.cf_menu['text_box_styles']
        cf_wrapper = cf_containers['wrapper']
        cf_subcontainer = cf_containers['subcontainer']

        # create a wrapper to hold other containers
        self.MENU_WRAPPER = UI_Container_Wrapper(
            cf_wrapper['position'],
            cf_wrapper['size'],
            cf_wrapper['child_anchor'],
            cf_wrapper['child_align'],
            cf_wrapper['child_padding'],
            cf_wrapper['bg_color'],
            cf_wrapper['border_color'],
            cf_wrapper['border_width']
        )
        self.menu_wrapper_group.add(self.MENU_WRAPPER)

        # list for all subcontainers
        self.menu_subcontainers = []

        # store the calculated sizes
        subcontainer_width = int(cf_subcontainer['size'][0])
        subcontainer_height = int(cf_subcontainer['size'][1])
        unclaimed_height = 0


        ### subcontainer 1 --> menu title ###
        # slim down the title text box by -ish- half the regular height
        title_container_height = int(subcontainer_height / 2)
        unclaimed_height += int(subcontainer_height - title_container_height)

        # create text box within a single-container to keep it centered
        TITLE_CONTAINER = UI_Container_Single(
            cf_subcontainer['position'],
            (subcontainer_width, title_container_height),
            None, "centerx", "centery", 0, 0,
            UI_Text_Box(
                cf_text_box_styles['xlarge'], self.cf_global,
                None, '', self.get_menu_title_text, (0, 0)
            )
        )
        self.menu_subcontainers.append(TITLE_CONTAINER)


        ### subcontainer 2 --> subtitle text ###
        subtitle_container_height = int(subcontainer_height / 1.5)
        unclaimed_height += int(subcontainer_height - subtitle_container_height)
    
        SUBTITLE_CONTAINER = UI_Container_Single(
            cf_subcontainer['position'],
            (subcontainer_width, subtitle_container_height),
            None, "centerx", "centery", 0, 0,
            UI_Text_Box(
                cf_text_box_styles['large'], self.cf_global,
                None, '', self.get_menu_subtitle_text, (0, 0)
            )
        )
        self.menu_subcontainers.append(SUBTITLE_CONTAINER)


        ### subcontainer 3 --> map selection || end map
        # create an internal wrapper for containing buttons
        sub_3_height = int(subcontainer_height / 2)
        unclaimed_height += int(subcontainer_height - sub_3_height)

        btn_padding = int(4)
        SUB_3_BTN_WRAPPER = UI_Container_Wrapper(
            cf_subcontainer['position'],
            (subcontainer_width, sub_3_height),
            "left", "right", btn_padding, None, None, None
        )

        # n_buttons = len(self.valid_cf_maps_keys)
        n_buttons = 4
        total_padded_width = int(btn_padding * (n_buttons + 1))
        btn_width = int((subcontainer_width - total_padded_width) / n_buttons)
        btn_height = int(sub_3_height - (2 * btn_padding))

        btn_list = []
        while (n_buttons != 0):
            BTN = UI_Container_Single(
                cf_subcontainer['position'],
                (btn_width, btn_height),
                None, "centerx", "centery", 0, 0,
                UI_Text_Box(
                    cf_text_box_styles['alt_small'], self.cf_global,
                    None, '', self.get_btn_text, (0, 0)
                )
            )
            btn_list.append(BTN)
            n_buttons -= 1

        SUB_3_BTN_WRAPPER.add_child(btn_list)
        self.menu_subcontainers.append(SUB_3_BTN_WRAPPER)

        # give the freed space from title back to the remaining subcontainers
        subcontainers_left -= len(self.menu_subcontainers)
        subcontainer_height += int(unclaimed_height / subcontainers_left)

        # create the rest as regular subcontainers
        for _ in range(subcontainers_left):
            subcontainer = UI_Sprite_Container(
                cf_subcontainer['position'],
                (subcontainer_width, subcontainer_height),
                cf_subcontainer['child_anchor'],
                cf_subcontainer['child_align'],
                cf_subcontainer['child_padding']
            )
            self.menu_subcontainers.append(subcontainer)

        # # add all subcontainers to the wrapper
        self.MENU_WRAPPER.add_child(self.menu_subcontainers)

        #### set up the rest of the menu content ####

    def get_menu_title_text(self):
        return self.menu_title_text

    def get_menu_subtitle_text(self):
        if (self.map_object_loaded):
            # TODO: MAP BEST TIME // POINTS
            pass
        else:
            return "Select a map! Confirm with space"

    def get_btn_text(self):
        return str("test")

    def loop(self):
        ''' main loop for drawing, checking events and updating the game '''

        while (self.looping):
            self.window.fill_surface()
            self.menu_wrapper_group.update(self.window.surface)
            self.check_events()
            pg.display.update()

            if (self.run_map_on_launch):
                self.run_map_on_launch = False
                self.init_map(self.valid_cf_maps_keys[0])
                self.map.looping = True

            if (self.map_object_loaded):
                # cProfile.run('APP.map.loop()')
                self.map.loop()
                if (self.map.done_looping):
                    self.looping = False
                    pass
                else:
                    # MENU CALL
                    pass

        if (self.print_misc_info):
            print('[APP][loop] App exiting through main loop')

if __name__ == '__main__':
    # initialize pygame and verify the version before anything else
    pg.init()
    run_app = True
    if (pg.version.vernum < CF_GLOBAL['req_pg_version']['vernum']):
        msg = f'\nExpected pygame version {CF_GLOBAL["req_pg_version"]["string"]} or newer. '
        msg += '(if using pip, "pip install pygame --upgrade" will upgrade pygame)'
        warnings_warn(msg, stacklevel=2, source=None)

        if not str(input("> Try running app anyway? (y/n): ")) in ['y', 'yes', 'Y']:
            run_app = False
            print('Exiting ...')

    if (run_app):
        # load the app
        APP = PG_App(CF_GLOBAL, CF_WINDOW, CF_TIMER, CF_MENU, CF_MAPS)
        APP.loop()

    pg.quit()
