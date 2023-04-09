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
    UI_Single_Centered_Container,
    UI_Single_Centered_Container_Filled
)
from modules.PG_ui_text_box import UI_Text_Box
from modules.PG_ui_button import UI_Button


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
        print(f'loaded maps (config map keys): {self.valid_cf_maps_keys}')

        # create the window
        self.window = PG_Window(self.cf_global, self.cf_window)
        ''' object containing main surface window and bounds '''

        # create the timer
        self.timer = PG_Timer(self.cf_global, self.cf_timer)
        ''' pygame specific timer object '''

        self.timer.block_events(self.cf_global['blocked_events'])
        self.fetch_menu_controls()

        self.main_menu_wrapper_group = GroupSingle()
        ''' group of ui sprites that may be run at any point '''
        self.main_menu_button_group = Group()

        self.menu_title_text = str("<GameName>")

        self.curr_mouse_pos = pg.mouse.get_pos()
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
                case pg.MOUSEBUTTONUP:
                    self.check_button_onclick()
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
        ''' This function has a lot of constants / magic numbers / settings
        
            Originally tried doing this exclusively through config, but no way tbh.
            Callable references, etc, are for one not viable if that is done. Also, nearly 
            everything relies on calculating previous sizes.
            
            As a compromise, I chose to do the very size of the menu frame in config, then 
            dynamically position all the subcontainers within the set bounds,
        '''

        N_SUBCONTAINERS = 5
        subcontainers_left = int(N_SUBCONTAINERS)

        cf_fonts = self.cf_menu['fonts']
        cf_wrapper = self.cf_menu['wrapper']

        # create a wrapper to hold other containers
        self.MENU_WRAPPER = UI_Container_Wrapper(
            cf_wrapper['position'],
            cf_wrapper['size'],
            cf_wrapper['child_anchor'],
            cf_wrapper['child_anchor_offset_x'],
            cf_wrapper['child_anchor_offset_y'],
            cf_wrapper['child_align_x'],
            cf_wrapper['child_align_y'],
            cf_wrapper['child_padding_x'],
            cf_wrapper['child_padding_y'],
            cf_wrapper['bg_color'],
            cf_wrapper['border_color'],
            cf_wrapper['border_width']
        )
        # add wrapper to the apps groupsingle for updates
        self.main_menu_wrapper_group.add(self.MENU_WRAPPER)

        #### SUBCONTAINER CREATION ####
        # first, some setup and declarations. 
        MENU_WIDTH = int(cf_wrapper['size'][0])
        MENU_HEIGHT = int(cf_wrapper['size'][1])

        # note: padding is often +1 to account for the fact that the first elem is padded twice (top/bottom)

        # find / set cumulative padding applied by the wrapper, calculate sizes accordingly
        wrapper_cum_padding_x = int(20)
        wrapper_cum_padding_y = int(cf_wrapper['child_padding_y'] * (N_SUBCONTAINERS + 1))

        subcontainer_w = int(
            MENU_WIDTH - wrapper_cum_padding_x - (2 * cf_wrapper['child_anchor_offset_x'])
        )
        subcontainer_h = int(
            ((MENU_HEIGHT - wrapper_cum_padding_y) / (N_SUBCONTAINERS)) 
            - round((2 * cf_wrapper['child_anchor_offset_y']) / N_SUBCONTAINERS)
        )

        dummy_pos = (self.MENU_WRAPPER.rect.center)  # does not really matter due to autopositioning
        unclaimed_height = 0

        # list for all subcontainers
        wrapper_subcontainers = []

        ### subcontainer 1 --> menu title ###
        # slim down the title text box by -ish- half the regular height
        title_container_height = int(subcontainer_h / 2)
        unclaimed_height += int(subcontainer_h - title_container_height)

        # create text box within a single-container to keep it centered
        TITLE_CONTAINER = UI_Single_Centered_Container(
            None, (subcontainer_w, title_container_height), 0, 0,
            UI_Text_Box(
                cf_fonts['xlarge'], self.cf_global,
                None, '', self.get_menu_title_text, None, (0, 0)
            )
        )
        wrapper_subcontainers.append(TITLE_CONTAINER)


        ### subcontainer 2 --> subtitle text ###
        subtitle_container_height = int(subcontainer_h / 1.5)
        unclaimed_height += int(subcontainer_h - subtitle_container_height)

        SUBTITLE_CONTAINER = UI_Single_Centered_Container(
            None, (subcontainer_w, subtitle_container_height), 0, 0,
            UI_Text_Box(
                cf_fonts['large'], self.cf_global,
                None, '', self.get_menu_subtitle_text, None, (0, 0)
            )
        )
        wrapper_subcontainers.append(SUBTITLE_CONTAINER)


        ### subcontainer 3 --> button wrapper --> map selection || end map ###
        # create an internal wrapper for containing buttons
        sub_3_height = int(subcontainer_h / 2)
        unclaimed_height += int(subcontainer_h - sub_3_height)

        n_buttons = len(self.valid_cf_maps_keys)
        # n_buttons = int(4)

        btn_padding_x = int(cf_wrapper['border_width'])
        btn_padding_y = int(0)

        btn_width = int((subcontainer_w - (btn_padding_x * (n_buttons - 1))) / n_buttons)
        btn_height = int(sub_3_height)

        self.SUB_3_BTN_WRAPPER = UI_Container_Wrapper(
            dummy_pos, (subcontainer_w, sub_3_height),
            "left", int(-btn_padding_x), 0,
            "right", "container_centery",
            btn_padding_x, btn_padding_y, None, None, None
        )

        map_btn_list = []
        cf_button = self.cf_menu['buttons']['map_selection']
        for i in range(n_buttons):
            BTN = UI_Button(
                cf_button,
                self.cf_global,
                str(self.valid_cf_maps_keys[i]),
                '',
                self.get_menu_button_text,
                (btn_width, btn_height),
                dummy_pos,
                self.init_map,
                str(self.valid_cf_maps_keys[i]),
                self.mouse_is_over
            )
            map_btn_list.append(BTN)

        self.SUB_3_BTN_WRAPPER.add_child(map_btn_list)
        self.main_menu_button_group.add(map_btn_list)
        wrapper_subcontainers.append(self.SUB_3_BTN_WRAPPER)


        ### subcontainer 4 --> ###


        ### create the rest as regular subcontainers ###
        # give the freed space from title back to the remaining subcontainers
        subcontainers_left -= len(wrapper_subcontainers)
        subcontainer_h += int(unclaimed_height / subcontainers_left)

        for _ in range(subcontainers_left):
            subcontainer = UI_Sprite_Container(
                dummy_pos,
                (subcontainer_w, subcontainer_h),
                "left", 0, 0,
                "right", "centery", int(4), int(0)
            )
            wrapper_subcontainers.append(subcontainer)


        ## add all subcontainers to the wrapper
        self.MENU_WRAPPER.add_child(wrapper_subcontainers)

        ### PIXEL PERFECT SIZE CORRECTIONS ###
        # update to get the actual positions
        self.main_menu_wrapper_group.update(self.window.surface)

        # correct last subcontainer height
        target_y_pos = int(
            self.MENU_WRAPPER.rect.bottom - self.MENU_WRAPPER.border_width - self.MENU_WRAPPER.CHILD_PADDING_Y)
        SUBC_LIST = self.MENU_WRAPPER.children.sprites()
        actual_y_pos = SUBC_LIST[len(SUBC_LIST)-1].rect.bottom
        SUBC_LIST[len(SUBC_LIST)-1].rect.height += (target_y_pos - actual_y_pos)

        # # correct btn width
        # last_btn_i = len(btn_list)-1
        # btn_list[last_btn_i].rect.width += int(self.SUB_3_BTN_WRAPPER.rect.right - btn_list[last_btn_i].rect.right)

    def mouse_is_over(self, has_rect):
        if has_rect.rect.collidepoint(self.curr_mouse_pos):
            return True
        return False

    def get_menu_button_text(self, ref_id):
        if not (self.map_object_loaded):
            return str(self.cf_maps[ref_id]['name'])
        else:
            # TODO -> EXIT MAP ETC
            pass

    def check_button_onclick(self):
        if not (self.map_object_loaded):
            for button in self.main_menu_button_group:
                if self.mouse_is_over(button):
                    button.trigger()
                    break

    def get_menu_title_text(self):
        return self.menu_title_text

    def get_menu_subtitle_text(self):
        if (self.map_object_loaded):
            # TODO: MAP BEST TIME // POINTS
            pass
        else:
            return "Choose a map! Mouse over for more info"

    def get_btn_text(self):
        return str("test")

    def loop(self):
        ''' main loop for drawing, checking events and updating the game '''

        while (self.looping):
            self.window.fill_surface()
            self.curr_mouse_pos = pg.mouse.get_pos()
            self.main_menu_wrapper_group.update(self.window.surface)
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
                    # PAUSE MENU CALL
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
