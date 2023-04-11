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
    UI_Single_Centered_Container,
    UI_Text_Container
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
        self.PG_MOUSE_EVENTS = [pg.MOUSEMOTION, pg.MOUSEBUTTONUP, pg.MOUSEBUTTONDOWN]

        # ui groups / lists
        self.menu_wrapper_group = GroupSingle()
        self.tooltip_group = GroupSingle()
        self.MAIN_MENU_BUTTONS = []
        self.PAUSE_MENU_BUTTONS = []

        self.menu_title_text = str("<GameName>")
        self.curr_mouse_pos = pg.mouse.get_pos()

        self.looping = True
        self.map_loaded = False
        self.run_map_on_launch = False
        self.print_misc_info = True

        self.set_up_menu()
        self.create_menu_tooltip()

    def get_map_tooltip(self, cf_map: dict):
        return str("TESTDADWDA")

    def set_up_menu(self):
        ''' This function has a lot of constants / magic numbers / settings
        
            Originally tried doing this exclusively through config, but no way tbh.
            Callable references, etc, are for one not viable if that is done. Also, nearly 
            everything relies on calculating previous sizes.
            
            As a compromise, I chose to do the very size of the menu frame in config, then 
            dynamically position all the subcontainers within the set bounds,
        '''
        CF_BG_NONE = None
        N_SUBCONTAINERS = 5
        subcontainers_left = int(N_SUBCONTAINERS)

        cf_default_fonts = self.cf_menu['default_fonts']
        cf_wrapper = self.cf_menu['wrapper']

        # create a wrapper to hold other containers
        self.MENU_WRAPPER = UI_Container_Wrapper(
            cf_wrapper['cf_bg'],
            cf_wrapper['position'],
            cf_wrapper['size'],
            cf_wrapper['child_anchor'],
            cf_wrapper['child_anchor_offset_x'],
            cf_wrapper['child_anchor_offset_y'],
            cf_wrapper['child_align_x'],
            cf_wrapper['child_align_y'],
            cf_wrapper['child_padding_x'],
            cf_wrapper['child_padding_y']
        )
        # add wrapper to the apps groupsingle for updates
        self.menu_wrapper_group.add(self.MENU_WRAPPER)

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

        ### subcontainer 1 --> menu title ###
        # slim down the title text box by -ish- half the regular height
        title_container_height = int(subcontainer_h / 2)
        unclaimed_height += int(subcontainer_h - title_container_height)

        # create text box within a single-container to keep it centered
        TITLE_CONTAINER = UI_Single_Centered_Container(
            CF_BG_NONE, None, (subcontainer_w, title_container_height), 0, 0,
            UI_Text_Box(
                cf_default_fonts['xlarge'], self.cf_global,
                None, '', self.get_menu_title_text, None, (0, 0)
            )
        )
        self.MENU_WRAPPER.add_child(TITLE_CONTAINER)

        ### subcontainer 2 --> subtitle text ###
        subtitle_container_height = int(subcontainer_h / 1.5)
        unclaimed_height += int(subcontainer_h - subtitle_container_height)

        SUBTITLE_CONTAINER = UI_Single_Centered_Container(
            CF_BG_NONE, None, (subcontainer_w, subtitle_container_height), 0, 0,
            UI_Text_Box(
                cf_default_fonts['large'], self.cf_global,
                None, '', self.get_menu_subtitle_text, None, (0, 0)
            )
        )
        self.MENU_WRAPPER.add_child(SUBTITLE_CONTAINER)


        ### subcontainer 3 --> all-purpose button wrapper
        # create an internal wrapper for containing buttons
        btn_wrapper_height = int(subcontainer_h / 2)
        unclaimed_height += int(subcontainer_h - btn_wrapper_height)

        n_buttons = len(self.valid_cf_maps_keys)
        btn_padding_x = int(self.MENU_WRAPPER.border_width)
        btn_padding_y = int(0)

        self.MENU_BUTTON_WRAPPER = UI_Container_Wrapper(
            CF_BG_NONE,
            dummy_pos, (subcontainer_w, btn_wrapper_height),
            "left", int(-btn_padding_x), 0,
            "right", "container_centery",
            btn_padding_x, btn_padding_y
        )
        self.MENU_WRAPPER.add_child(self.MENU_BUTTON_WRAPPER)

        ### create MENU_BUTTON_WRAPPER's buttons ###

        # calculate width of map selection buttons
        btn_width = int((subcontainer_w - (btn_padding_x * (n_buttons - 1))) / n_buttons)
        btn_height = int(btn_wrapper_height)

        for i in range(n_buttons):
            cf_map_key = self.valid_cf_maps_keys[i]
            trigger_parameter = cf_map_key
            ref_id = cf_map_key
            tooltip_text = self.get_map_tooltip(self.cf_maps[cf_map_key])

            BTN = UI_Button(
                self.cf_menu['buttons']['map_selection'],
                self.cf_global,
                ref_id,
                '',
                self.get_menu_button_text,
                (btn_width, btn_height),
                dummy_pos,
                self.init_map,
                trigger_parameter,
                self.button_mouse_over,
                tooltip_text
            )
            self.MAIN_MENU_BUTTONS.append(BTN)

        self.MENU_BUTTON_WRAPPER.add_child(self.MAIN_MENU_BUTTONS)

        # recalculate width for the map pause buttons
        n_buttons = int(3)
        btn_width = int((subcontainer_w - (btn_padding_x * (n_buttons - 1))) / n_buttons)

        # 1) main menu
        btn_return_tooltip = "Return to the main menu. n/t/Warning n/_b_All progress will be lost."
        BTN_RETURN = UI_Button(
            self.cf_menu['buttons']['map_paused_action'],
            self.cf_global,
            ["BUTTON", "PAUSE_MENU", "RETURN"],
            str('Main Menu'),
            None,
            (btn_width, btn_height),
            dummy_pos,
            self.exit_map,
            False,
            self.button_mouse_over,
            btn_return_tooltip
        )

        # 2) restart
        btn_reset_tooltip = "Reset the map. n/Map setup will be the same."
        BTN_RESET = UI_Button(
            self.cf_menu['buttons']['map_paused_action'],
            self.cf_global,
            ["BUTTON", "PAUSE_MENU", "RESET"],
            str('Reset'),
            None,
            (btn_width, btn_height),
            dummy_pos,
            self.reset_map,
            None,
            self.button_mouse_over,
            btn_reset_tooltip
        )

        # 3) unpause
        btn_unpause_tooltip = str("Return to the game.")
        BTN_UNPAUSE = UI_Button(
            self.cf_menu['buttons']['map_paused_action'],
            self.cf_global,
            ["BUTTON", "PAUSE_MENU", "UNPAUSE"],
            str('Unpause'),
            None,
            (btn_width, btn_height),
            dummy_pos,
            self.unpause_map,
            None,
            self.button_mouse_over,
            btn_unpause_tooltip
        )

        self.PAUSE_MENU_BUTTONS.extend([BTN_RETURN, BTN_RESET, BTN_UNPAUSE])

        # TODO
        ## out of map 
        #   --> control info? how to access menu ingame?
        #   --> key config options?
        ## in-map
        #   --> status report? (coin count, health, fuel, fastest map time)
        # 
        ### subcontainer 4 -->  ###


        ### create the rest as regular subcontainers ###
        # give the freed space from title back to the remaining subcontainers
        subcontainers_left -= len(self.MENU_WRAPPER.children.sprites())
        subcontainer_h += int(unclaimed_height / subcontainers_left)

        for _ in range(subcontainers_left):
            subcontainer = UI_Sprite_Container(
                CF_BG_NONE, dummy_pos,
                (subcontainer_w, subcontainer_h),
                "left", 0, 0,
                "right", "centery", int(4), int(0)
            )
            self.MENU_WRAPPER.add_child(subcontainer)


        ### PIXEL PERFECT SIZE CORRECTIONS ###
        # update to get the actual positions
        self.menu_wrapper_group.update(self.window.surface)

        # correct last subcontainer height
        target_y_pos = int(
            self.MENU_WRAPPER.rect.bottom - self.MENU_WRAPPER.border_width - self.MENU_WRAPPER.CHILD_PADDING_Y)
        SUBC_LIST = self.MENU_WRAPPER.children.sprites()
        actual_y_pos = SUBC_LIST[len(SUBC_LIST)-1].rect.bottom
        SUBC_LIST[len(SUBC_LIST)-1].rect.height += (target_y_pos - actual_y_pos)

        # # correct btn width
        # last_btn_i = len(btn_list)-1
        # btn_list[last_btn_i].rect.width += int(self.MENU_BUTTON_WRAPPER.rect.right - btn_list[last_btn_i].rect.right)

    def create_menu_tooltip(self):
        ''' create a text container that will dynamically change its size to fit the given text '''
        cf_tooltip = self.cf_menu['tooltip_container']

        self.TOOLTIP = UI_Text_Container(
            cf_tooltip['cf_bg'],
            cf_tooltip['cf_fonts'],
            cf_tooltip['cf_formatting_triggers'],
            self.window,
            self.MENU_WRAPPER.rect.topleft,
            cf_tooltip['max_width'],
            cf_tooltip['max_height'],
            cf_tooltip['child_padding_x'],
            cf_tooltip['child_padding_y'],
            cf_tooltip['title_padding_y'],
            str("_H_This _N_is a _*_tooltip test. _N_Hello _N_World! 1234 abc")
        )

    def init_map(self, cf_maps_key: str):
        if (self.print_misc_info):
            print(f'[APP][init_map]:\n> Call to create map from key "{cf_maps_key}"')

        if (self.map_loaded):
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

        self.map_loaded = True
        self.timer.activate_duration_text()

    def exit_map(self, map_completed: bool):
        # save segment if map was completed
        self.timer.new_segment("menu", map_completed)
        self.map_loaded = False
        del self.map
        self.MENU_BUTTON_WRAPPER.replace_children(self.MAIN_MENU_BUTTONS)
        self.timer.kill_duration_text()

    def reset_map(self):
        self.map.reset()
        if (self.map.paused):
            self.map.unpause()

    def unpause_map(self):
        self.map.unpause()

    def mouse_is_over(self, has_rect):
        if has_rect.rect.collidepoint(self.curr_mouse_pos):
            return True
        return False

    def button_mouse_over(self, button: UI_Button):
        hovering = self.mouse_is_over(button)
        if (hovering):
            if (hasattr(button, "tooltip_text")):
                self.TOOLTIP.set_text(button.tooltip_text)
                self.TOOLTIP.move(self.curr_mouse_pos)
                self.tooltip_group.add(self.TOOLTIP)
        return hovering

    def check_button_onclick(self):
        ''' check if mouse is above a button when mouse1 clicked '''
        if (self.map_loaded):
            for button in self.PAUSE_MENU_BUTTONS:
                if self.mouse_is_over(button):
                    button.trigger()
                    break
        else:
            for button in self.MAIN_MENU_BUTTONS:
                if self.mouse_is_over(button):
                    button.trigger()
                    break

    def get_menu_button_text(self, ref_id):
        ''' could be omitted and set text on creation, but leaving for now,
            seeing as performance during menu is not an issue whatsoever
        '''
        return str(self.cf_maps[ref_id]['name'])

    def get_menu_title_text(self):
        if (self.map_loaded):
            return f'{self.menu_title_text} - {self.map.name}'
        return self.menu_title_text

    def get_menu_subtitle_text(self):
        if (self.map_loaded):
            return str("Map Paused. Select an action")
        return str("Hover over the maps for more info")

    def check_events(self):
        for event in pg.event.get():
            match (event.type):
                case pg.MOUSEBUTTONUP:
                    self.check_button_onclick()
                case pg.KEYDOWN:
                    # TODO: MENU CONTROLS
                    match (event.key):
                        case pg.K_ESCAPE:
                            print("unpause called")
                            if (self.map_loaded):
                                if (self.map.paused):
                                    self.map.unpause()
                        case _:
                            pass
                case pg.QUIT:
                   self.looping = False
                case _:
                    pass

    def loop(self):
        ''' main loop for drawing, checking events and updating the game '''
        self.window.fill_surface()

        while (self.looping):
            self.timer.update_paused()
            self.curr_mouse_pos = pg.mouse.get_pos()
            self.menu_wrapper_group.update(self.window.surface)
            self.tooltip_group.update(self.window.surface)
 
            self.check_events()
            self.timer.draw_ui(self.window.map_surface)
            pg.display.update()

            self.tooltip_group.empty()
            if (self.run_map_on_launch):
                self.run_map_on_launch = False
                self.init_map(self.valid_cf_maps_keys[0])
                self.map.looping = True

            if (self.map_loaded):
                if not (self.map.paused):
                    # ignore mouse events when map is active
                    self.timer.block_events(self.PG_MOUSE_EVENTS)
                    self.map.loop()
                    if (self.map.quit_called):
                        self.looping = False
                    else:
                        self.timer.allow_events(self.PG_MOUSE_EVENTS)
                        if (self.map.paused):
                            self.MENU_BUTTON_WRAPPER.replace_children(self.PAUSE_MENU_BUTTONS)
                else:
                    self.map.draw()
                    self.map.ui_container_group.update(self.map.surface)
            else:
                self.window.fill_surface()

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
