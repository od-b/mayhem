# import cProfile
from warnings import warn as warnings_warn

# installed library imports
import pygame as pg
from pygame import Color
from pygame.sprite import GroupSingle

# config dicts
from config.cf_global import CF_GLOBAL
from config.cf_window import CF_WINDOW
from config.cf_timer import CF_TIMER
from config.cf_menu import CF_MENU
from config.cf_maps import CF_MAPS
from config.cf_players import CF_PLAYERS

# local modules
from modules.PG_window import PG_Window
from modules.PG_map import PG_Map
from modules.PG_timer import PG_Timer
from modules.PG_ui_containers import (
    UI_Container_Wrapper,
    UI_Single_Centered_Container,
    UI_Text_Container
)
from modules.PG_ui_text_box import UI_Text_Box
from modules.PG_ui_buttons import UI_Button, UI_Text_Button, UI_Image_Button

INFO_PRINT = True

'''
FORMATTING_TRIGGERS = {
    # one of | none:
    'bold': str("_b_"),
    'italic': str("_i_"),
    'light': str("_l_"),
    # may be combined:
    'alt_color': str("a/"),
    'title': str("t/"),
    'newline': str("n/"),
    'nosplit': str('::')    # renders words together. applies formatting to all. useful for titles.
}
'''

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
            cf_maps: dict,
            cf_players: dict
        ):

        self.cf_global = cf_global
        self.cf_window = cf_window
        self.cf_timer = cf_timer
        self.cf_menu = cf_menu
        self.cf_maps = cf_maps
        self.cf_players = cf_players

        # store relevant global constants
        self.FPS_LIMIT = int(self.cf_global['fps_limit'])
        self.DEBUG_COLOR = Color(self.cf_global['debug_color'])
        self.DEBUG_COLOR_2 = Color(self.cf_global['debug_color_2'])

        # create a list of available map keys
        self.valid_cf_maps_keys = self.cf_maps.keys()
        self.valid_cf_player_keys = self.cf_players.keys()

        if INFO_PRINT:
            print(f'loaded maps (config map keys): {self.valid_cf_maps_keys}')
            print(f'loaded players (config map keys): {self.valid_cf_player_keys}')

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
        self.BUTTON_LIST = []
        self.DEFAULT_MENU_SUBCONTAINERS = []
        self.POSTGAME_MENU_SUBCONTAINERS = []

        self.menu_title_text = str("Coins In Space")
        self.curr_mouse_pos: tuple[int, int] = pg.mouse.get_pos()

        self.looping: bool = True
        self.map_loaded: bool = False
        self.selected_cf_player: str | None = None
        self.selected_cf_map: str| None = None
        self.post_map_looping = False
        self.post_map_menu_active = False

        self.set_up_menu()
        self.create_tooltip_container()

    def debug_start_map(self):
        self.selected_cf_player = self.cf_players['fighter']
        self.selected_cf_map = self.cf_maps['map_1']
        self.init_map()

    #### RUN-ONCE MENU SETUP METHODS ####

    def set_up_menu(self):
        ''' Set up self.MENU_WRAPPER and all children // objects that depend on it
        
            This function has a few constants / magic numbers / settings

            Originally tried doing this exclusively through config, but no way tbh.
            Callable references, etc, are for one not viable if that is done. Also, nearly 
            everything relies on calculating previous sizes.
            
            As a compromise, I chose to do the very size of the menu frame in config, then 
            dynamically position all the subcontainers within the set bounds,
        '''
        CF_BG_NONE = None
        N_SUBCONTAINERS = 5
        # subcontainers_left = int(N_SUBCONTAINERS)

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

        # calculate container size, assuming all are equally sized
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
        title_container_height = int(subcontainer_h / 1.2)
        unclaimed_height += int(subcontainer_h - title_container_height)

        # create text box within a single-container to keep it centered
        TITLE_CONTAINER = UI_Single_Centered_Container(
            CF_BG_NONE, None, (subcontainer_w, title_container_height), 0, 0,
            UI_Text_Box(
                cf_default_fonts['xlarge'], self.cf_global,
                None, '', self.btn_get_menu_title_text, None, (0, 0)
            )
        )
        self.MENU_WRAPPER.add_child(TITLE_CONTAINER)

        ### subcontainer 2 --> subtitle text ###
        subtitle_container_height = int(subcontainer_h / 1.8)
        unclaimed_height += int(subcontainer_h - subtitle_container_height)

        SUBTITLE_CONTAINER = UI_Single_Centered_Container(
            CF_BG_NONE, None, (subcontainer_w, subtitle_container_height), 0, 0,
            UI_Text_Box(
                cf_default_fonts['large'], self.cf_global,
                None, '', self.btn_get_menu_subtitle_text, None, (0, 0)
            )
        )
        self.MENU_WRAPPER.add_child(SUBTITLE_CONTAINER)

        ### subcontainer 3 --> button wrapper --> map selection || pause actions
        top_btn_wrapper_height = int(subcontainer_h / 2)
        top_button_wrapper_width = subcontainer_w
        unclaimed_height += int(subcontainer_h - top_btn_wrapper_height)

        top_btn_padding_x = int(self.MENU_WRAPPER.border_width)
        top_btn_padding_y = int(0)

        self.BTN_WRAPPER_TOP = UI_Container_Wrapper(
            CF_BG_NONE,
            dummy_pos, (top_button_wrapper_width, top_btn_wrapper_height),
            "left", int(-top_btn_padding_x), 0,
            "right", "container_centery",
            top_btn_padding_x, top_btn_padding_y
        )
        self.MENU_WRAPPER.add_child(self.BTN_WRAPPER_TOP)

        # create map selection buttons
        self.MAP_SELECT_BUTTONS = self.create_map_selection_buttons(
            top_button_wrapper_width, top_btn_wrapper_height,
            top_btn_padding_x, top_btn_padding_y
        )

        # create buttons to display instead of map selection when map is paused
        self.PAUSE_ACTION_BUTTONS = self.create_map_paused_buttons(
            subcontainer_w, top_btn_wrapper_height,
            top_btn_padding_x, top_btn_padding_y
        )

        # store in respective lists
        self.BUTTON_LIST.extend(self.MAP_SELECT_BUTTONS + self.PAUSE_ACTION_BUTTONS)
        # initialize with main menu buttons as children
        self.BTN_WRAPPER_TOP.add_child(self.MAP_SELECT_BUTTONS)

        ### subcontainer 4 --> button wrapper --> select desired player
        mid_button_wrapper_height = int(subcontainer_h + 40)
        mid_button_wrapper_width = subcontainer_w
        unclaimed_height += int(subcontainer_h - mid_button_wrapper_height)

        mid_btn_padding_x = int(self.MENU_WRAPPER.border_width)
        mid_btn_padding_y = int(0)

        self.BTN_WRAPPER_MID = UI_Container_Wrapper(
            CF_BG_NONE,
            dummy_pos, (mid_button_wrapper_width, mid_button_wrapper_height),
            "left", int(-mid_btn_padding_x), 0,
            "right", "container_centery",
            mid_btn_padding_x, mid_btn_padding_y
        )
        self.MENU_WRAPPER.add_child(self.BTN_WRAPPER_MID)

        self.PLAYER_SELECT_BUTTONS = self.create_player_selection_buttons(
            mid_button_wrapper_width, mid_button_wrapper_height,
            mid_btn_padding_x, mid_btn_padding_y
        )


        # store in respective lists
        self.BUTTON_LIST.extend(self.PLAYER_SELECT_BUTTONS)
        # initialize with main menu buttons 
        self.BTN_WRAPPER_MID.add_child(self.PLAYER_SELECT_BUTTONS)

        ### alternate subcontainer 4 --> post map summary text
        cf_post_game_c = self.cf_menu['post_game_text_container']
        self.POST_GAME_WRAPPER = UI_Text_Container(
            cf_post_game_c['cf_bg'],
            cf_post_game_c['cf_fonts'],
            cf_post_game_c['cf_formatting_triggers'],
            self.window,
            self.MENU_WRAPPER.rect.midtop,
            subcontainer_w,
            subcontainer_h,
            cf_post_game_c['child_padding_x'],
            cf_post_game_c['child_padding_y'],
            cf_post_game_c['title_padding_y'],
            str("post game wrapper test text")
        )

        ### subcontainer 5 --> button container --> start game || return to game

        bottom_btn_wrapper_height= int(subcontainer_h / 1.4)
        self.BTN_WRAPPER_BOT = UI_Container_Wrapper(
            None,
            dummy_pos, 
            (bottom_btn_wrapper_height, subcontainer_w),
            "left", 0, 0,
            "container_centerx", "container_centery",
            0, 0
        )
        self.MENU_WRAPPER.add_child(self.BTN_WRAPPER_BOT)
        
        # create a button for the container
        btn_start_game_width = int(subcontainer_w / 2.5)
        btn_start_game_height = int(bottom_btn_wrapper_height-10)

        self.BTN_START_GAME = UI_Text_Button(
            self.cf_menu['buttons']['start_game']['cf_button'],
            self.cf_global,
            ["START_GAME", "RETURN", "UNPAUSE", "BUTTON"],
            (btn_start_game_width, btn_start_game_height),
            dummy_pos,
            self.btn_onclick_start_map,
            None,
            self.btn_check_mouse_over,
            None,
            self.cf_menu['buttons']['start_game']['cf_fonts'],
            '',
            self.btn_get_start_map_text,
            None
        )
        self.swap_start_game_btn_state(False)

        # add the button to the relevant lists/groups
        self.BTN_WRAPPER_BOT.add_child(self.BTN_START_GAME)

        ### PIXEL PERFECT SIZE CORRECTIONS ###
        # update to get the actual positions
        self.menu_wrapper_group.update(self.window.surface)

        # sort the menu subctonainer states into lists
        self.DEFAULT_MENU_SUBCONTAINERS.extend(self.MENU_WRAPPER.children.sprites())
        self.POSTGAME_MENU_SUBCONTAINERS.extend(
            [TITLE_CONTAINER, SUBTITLE_CONTAINER, self.POST_GAME_WRAPPER, self.BTN_WRAPPER_BOT]
        )

        # correct last subcontainer height
        target_y_pos = int(
            self.MENU_WRAPPER.rect.bottom - self.MENU_WRAPPER.border_width - self.MENU_WRAPPER.CHILD_PADDING_Y
        )
        SUBC_LIST = self.MENU_WRAPPER.children.sprites()
        actual_y_pos = SUBC_LIST[len(SUBC_LIST)-1].rect.bottom
        SUBC_LIST[len(SUBC_LIST)-1].rect.height += (target_y_pos - actual_y_pos)

        # # correct btn width
        # last_btn_i = len(btn_list)-1
        # btn_list[last_btn_i].rect.width += int(self.BTN_WRAPPER_TOP.rect.right - btn_list[last_btn_i].rect.right)

    def create_player_selection_buttons(self, container_w, container_h, btn_padding_x, btn_padding_y):
        n_buttons = len(self.valid_cf_player_keys)

        # calculate size of map selection buttons
        btn_width = int((container_w - (btn_padding_x * (n_buttons - 1))) / n_buttons)
        btn_height = int(container_h - (btn_padding_y * 2))
        
        btn_image_padding_x = int(10)
        btn_image_padding_y = int(-40)

        PLAYER_SELECT_BUTTONS: list[UI_Button] = []

        for player_key in self.valid_cf_player_keys:
            tooltip_text = self.format_player_tooltip_text(player_key)
            trigger_func = self.btn_onclick_select_player
            trigger_parameter = player_key
            hover_bool_func = self.btn_check_mouse_over
            ref_id = player_key
            image_path = self.cf_players[player_key]['spritesheets']['idle']['path']

            BTN = UI_Image_Button(
                self.cf_menu['buttons']['player_selection']['cf_button'],
                self.cf_global,
                ref_id,
                (btn_width, btn_height),
                self.MENU_WRAPPER.rect.center,
                trigger_func,
                trigger_parameter,
                hover_bool_func,
                tooltip_text,
                image_path,
                btn_image_padding_x,
                btn_image_padding_y
            )
            PLAYER_SELECT_BUTTONS.append(BTN)

        return PLAYER_SELECT_BUTTONS

    def create_map_selection_buttons(self, container_w, container_h, btn_padding_x, btn_padding_y):
        n_buttons = len(self.valid_cf_maps_keys)

        # calculate size of map selection buttons
        btn_width = int((container_w - (btn_padding_x * (n_buttons - 1))) / n_buttons)
        btn_height = int(container_h - (btn_padding_y * 2))

        MAP_SELECT_BUTTONS: list[UI_Text_Button] = []

        for map_key in self.valid_cf_maps_keys:
            tooltip_text = self.format_map_tooltip_text(map_key)
            trigger_func = self.btn_onclick_select_map
            trigger_parameter = map_key
            btn_text = str(self.cf_maps[map_key]['name'])
            hover_bool_func = self.btn_check_mouse_over
            text_getter_func = None
            text_getter_param = map_key
            ref_id = map_key

            BTN = UI_Text_Button(
                self.cf_menu['buttons']['map_selection']['cf_button'],
                self.cf_global,
                ref_id,
                (btn_width, btn_height),
                self.MENU_WRAPPER.rect.center,
                trigger_func,
                trigger_parameter,
                hover_bool_func,
                tooltip_text,
                self.cf_menu['buttons']['map_selection']['cf_fonts'],
                btn_text,
                text_getter_func,
                text_getter_param
            )
            MAP_SELECT_BUTTONS.append(BTN)

        return MAP_SELECT_BUTTONS

    def create_map_paused_buttons(self, container_w, container_h, btn_padding_x, btn_padding_y):
        # recalculate width for the map pause buttons
        n_buttons = int(2)
        btn_width = int((container_w - (btn_padding_x * (n_buttons - 1))) / n_buttons)
        btn_height = int(container_h - (btn_padding_y * 2))

        cf_button = self.cf_menu['buttons']['map_paused_action']['cf_button']
        cf_fonts = self.cf_menu['buttons']['map_paused_action']['cf_fonts']

        # 1) main menu
        btn_return_tooltip = "Return to the main menu. n/t/Warning n/_b_All progress will be lost."
        BTN_RETURN = UI_Text_Button(
            cf_button,
            self.cf_global,
            ["BUTTON", "PAUSE_MENU", "RETURN"],
            (btn_width, btn_height),
            self.MENU_WRAPPER.rect.center,
            self.exit_map,
            False,
            self.btn_check_mouse_over,
            btn_return_tooltip,
            cf_fonts,
            str('Main Menu'),
            None,
            None
        )

        # 2) restart
        btn_reset_tooltip = "Reset the map. n/Map setup will be the same."
        BTN_RESET = UI_Text_Button(
            cf_button,
            self.cf_global,
            ["BUTTON", "PAUSE_MENU", "RESET"],
            (btn_width, btn_height),
            self.MENU_WRAPPER.rect.center,
            self.reset_map,
            None,
            self.btn_check_mouse_over,
            btn_reset_tooltip,
            cf_fonts,
            str('Reset'),
            None,
            None
        )

        # 3) unpause
        # btn_unpause_tooltip = str("Return to the game.")
        # BTN_UNPAUSE = UI_Text_Button(
        #     cf_button,
        #     self.cf_global,
        #     ["BUTTON", "PAUSE_MENU", "UNPAUSE"],
        #     (btn_width, btn_height),
        #     self.MENU_WRAPPER.rect.center,
        #     self.unpause_map,
        #     None,
        #     self.btn_check_mouse_over,
        #     btn_unpause_tooltip,
        #     cf_fonts,
        #     str('Unpause'),
        #     None,
        #     None
        # )

        # PAUSE_ACTION_BTNS: list[UI_Text_Button] = [BTN_RETURN, BTN_RESET, BTN_UNPAUSE]
        PAUSE_ACTION_BTNS: list[UI_Text_Button] = [BTN_RETURN, BTN_RESET]

        for btn in PAUSE_ACTION_BTNS:
            btn.toggle_state_duration = None

        return PAUSE_ACTION_BTNS

    def create_tooltip_container(self):
        ''' create a text container that will dynamically change its size to fit the given text '''
        cf_tooltip = self.cf_menu['tooltip_container']

        self.TOOLTIP = UI_Text_Container(
            cf_tooltip['cf_bg'],
            cf_tooltip['cf_fonts'],
            cf_tooltip['cf_formatting_triggers'],
            self.window,
            (0, 0),
            cf_tooltip['max_width'],
            cf_tooltip['max_height'],
            cf_tooltip['child_padding_x'],
            cf_tooltip['child_padding_y'],
            cf_tooltip['title_padding_y'],
            str("_H_This _N_is a _*_tooltip test. _N_Hello _N_World! 1234 abc")
        )

    def format_map_tooltip_text(self, map_key: str):
        return str(f'{map_key}')

    def format_player_tooltip_text(self, player_key: str):
        # TODO: format these constants as comparable percentages
        CF = self.cf_players[player_key]
        CF_g = CF['gameplay']
        CF_w = CF['physics']

        name = CF['name']
        descr = CF['description']
        description = descr.split()

        mass = CF_w['mass']
        handling = CF_w['handling']
        thrust = CF_w['thrust_magnitude']
        max_hp = int(CF_g['max_health'])
        max_fuel = int(CF_g['max_fuel'])

        text = f't/_b_{name}'
        text += f' n/'

        for word in description:
            text += f'_i_{word} '

        text += f' n/a/_b_Health: {max_hp} '
        text += f' n/a/_b_Fuel: {max_fuel} '
        text += f' n/a/_b_Mass: {mass} '
        text += f' n/a/_b_Handling: {handling} '
        text += f' n/a/_b_Thrust: {thrust} '

        return text

    #### CALLABLE BUTTON METHODS -- not directly called by the app ####

    def btn_get_menu_title_text(self):
        if self.map_loaded:
            return f'{self.menu_title_text} - {self.map.name}'
        return self.menu_title_text

    def btn_get_menu_subtitle_text(self):
        if (self.map_loaded):
            if (self.map.map_success != None):
                if (self.map.map_success == True):
                    return str('Map Completed')
                else:
                    return str('Map Failed')
            if (self.map.paused):
                return str("Map Paused. Select an Action")

        if (self.selected_cf_map and self.selected_cf_player):
            return str("Ready to Start?")
        elif (self.selected_cf_map):
            map_name = self.selected_cf_map['name']
            return f'{map_name} Selected. Select a Player!'
        elif (self.selected_cf_player):
            player_name = self.selected_cf_player['name']
            return f'{player_name} Selected. Select a Map!'

        return str("Select Map & Player")

    def btn_get_start_map_text(self):
        if self.map_loaded:
            if (self.map.map_success != None):
                return str("CONTINUE")
            return str("RETURN")
        return str("START MAP")

    def btn_onclick_start_map(self):
        if self.map_loaded:
            if (self.map.map_success != None):
                print(f'map_success="{self.map.map_success}"')
                self.swap_to_pause_menu()
                self.swap_start_game_btn_state(False)
                # self.exit_map(self.map.map_success)
            else:
                self.unpause_map()
        elif self.selected_cf_player and self.selected_cf_map:
            if INFO_PRINT:
                map_name = self.selected_cf_map['name']
                player_name = self.selected_cf_player['name']
                print(f'starting map "{map_name}" using player "{player_name}"')
            self.init_map()

    def btn_onclick_select_map(self, map_key: str | None):
        if (map_key == None):
            self.selected_cf_map = None
            self.swap_start_game_btn_state(False)
        else:
            self.selected_cf_map = self.cf_maps[map_key]
            if INFO_PRINT:
                print(f'selected map: cf_maps["{map_key}"]')
            if self.selected_cf_player:
                self.swap_start_game_btn_state(True)

    def btn_onclick_select_player(self, player_key: str | None):
        if (player_key == None):
            self.selected_cf_player = None
            self.swap_start_game_btn_state(False)
        else:
            self.selected_cf_player = self.cf_players[player_key]
            if INFO_PRINT:
                print(f'selected player: cf_players["{player_key}"]')
            if self.selected_cf_map:
                self.swap_start_game_btn_state(True)

    def btn_check_mouse_over(self, button: UI_Button):
        hovering = self.mouse_is_over(button)
        if (hovering):
            if (hasattr(button, "tooltip_text")):
                self.TOOLTIP.set_text(button.tooltip_text)
                self.TOOLTIP.move(self.curr_mouse_pos)
                self.tooltip_group.add(self.TOOLTIP)
        return hovering

    #### MAP STATE METHODS ####

    def init_map(self):
        # create the map object as an attribute of self
        self.map = PG_Map(self.cf_global, self.selected_cf_map, self.timer, self.window.map_surface)

        if INFO_PRINT:
            print(f'> Map object "{self.map.name}" created from config! Setting up map assets ...')

        # set up the map
        self.map.set_up_all()
        self.window.set_extended_caption(self.map.name)

        if INFO_PRINT:
            print(f'> succesfully created and set up map. Returning ...')

        self.map_loaded = True

        self.map.spawn_player(self.selected_cf_player)
        self.map.start()
        self.timer.activate_duration_text()

    def exit_map(self, map_completed: bool):
        self.window.set_extended_caption(None)
        # save segment if map was completed
        self.timer.new_segment("menu", map_completed)
        self.map_loaded = False
        self.selected_cf_map = None
        self.selected_cf_player = None

        if INFO_PRINT:
            print(f'[exit_map]: Cleaning up all map sprites ... ')

        for elem in self.map.ALL_SPRITES:
            elem.kill()
            del elem

        for projectile in self.map.global_projectile_group.sprites():
            projectile.kill()
            del projectile

        if INFO_PRINT:
            print(f'All sprites deleted. Deleting "{self.map.name}"')

        del self.map

        self.swap_to_main_menu()

    def reset_map(self):
        self.map.reset()
        if (self.map.paused):
            self.map.unpause()

    def unpause_map(self):
        self.map.unpause()

    #### MISC && MAIN LOOPS ####

    def mouse_is_over(self, has_rect):
        ''' check if curr_mouse_pos collides with an objects rect '''
        if has_rect.rect.collidepoint(self.curr_mouse_pos):
            return True
        return False

    def check_button_onclick(self, buttons: list[UI_Button]):
        ''' check if mouse is above a button when mouse1 clicked '''
        for btn in buttons:
            if self.mouse_is_over(btn):
                # check if button can be triggered
                if not btn.allow_trigger:
                    break
                # un-toggle if already clicked
                if btn.toggle_state_active:
                    btn.toggle_state_active = False
                    if btn.trigger_parameter:
                        btn.trigger_func(None)
                    break
                # turn off click state for other buttons in the list
                for _btn in buttons:
                    _btn.toggle_state_active = False
                btn.trigger()
                break

    def swap_to_pause_menu(self):
        self.MENU_WRAPPER.replace_children(self.DEFAULT_MENU_SUBCONTAINERS)
        self.BTN_WRAPPER_TOP.replace_children(self.PAUSE_ACTION_BUTTONS)
        self.BTN_WRAPPER_MID.kill_all_children()
        self.swap_start_game_btn_state(True)

    def swap_to_main_menu(self):
        self.MENU_WRAPPER.replace_children(self.DEFAULT_MENU_SUBCONTAINERS)
        self.BTN_WRAPPER_TOP.replace_children(self.MAP_SELECT_BUTTONS)
        self.BTN_WRAPPER_MID.replace_children(self.PLAYER_SELECT_BUTTONS)
        self.timer.kill_duration_text()

        self.selected_cf_map = None
        self.selected_cf_player = None

        for btn in self.BUTTON_LIST:
            btn.toggle_state_active = False
        self.swap_start_game_btn_state(False)

    def swap_start_game_btn_state(self, make_clickable: bool):
        if make_clickable:
            self.BTN_START_GAME.toggle_state_active = False
            self.BTN_START_GAME.allow_trigger = True
        else:
            self.BTN_START_GAME.toggle_state_active = True
            self.BTN_START_GAME.allow_trigger = False

    def check_events(self):
        for event in pg.event.get():
            match (event.type):
                case pg.MOUSEBUTTONUP:
                    # self.check_button_onclick(self.SHARED_BUTTONS)
                    self.check_button_onclick(self.BTN_WRAPPER_TOP.children.sprites())
                    self.check_button_onclick(self.BTN_WRAPPER_MID.children.sprites())
                    self.check_button_onclick(self.BTN_WRAPPER_BOT.children.sprites())
                case pg.KEYDOWN:
                    # TODO: MENU CONTROLS
                    match (event.key):
                        case pg.K_ESCAPE:
                            if (self.map_loaded):
                                if (self.map.paused) and (self.map.map_success == None):
                                    self.map.unpause()
                        case _:
                            pass
                case pg.QUIT:
                   self.looping = False
                case _:
                    pass

    def post_map_loop(self):
        self.post_map_looping = True
        self.swap_to_post_game_menu()
        self.map.paused = True

        death_frames_left = int(self.map.death_frames_left)

        while (self.looping and self.post_map_looping):
            self.timer.update_paused()

            if (death_frames_left > 0):
                death_frames_left -= 1
                self.map.draw_external()
                self.map.check_events()
                self.map.ui_container_group.update(self.map.surface)
                pg.display.update()
                self.map.coin_group.update()
                self.map.player_group.update()
                if (self.map.quit_called):
                    self.looping = False
            else:
                self.post_map_looping = False

    def loop(self):
        ''' main loop for drawing, checking events and updating the game '''
        self.window.fill_surface()

        # outer loop for the app
        while self.looping:
            self.curr_mouse_pos = pg.mouse.get_pos()
            self.timer.update_paused()
            self.timer.draw_ui(self.window.map_surface)
            self.menu_wrapper_group.update(self.window.surface)
            self.tooltip_group.update(self.window.surface)
            self.check_events()
            pg.display.update()
            self.tooltip_group.empty()

            # check whether a map is loaded
            if (self.map_loaded):
                # check whether there was an initialization, or if map is paused
                if not (self.map.paused):
                    if (self.map.map_success == None):
                        # ignore mouse events when map is active, then loop the map
                        self.timer.block_events(self.PG_MOUSE_EVENTS)
                        self.map.loop()

                        # map loop breakout: pause or program exit?
                        if (self.map.quit_called):
                            self.looping = False
                        else:
                            self.timer.allow_events(self.PG_MOUSE_EVENTS)
                            # check if map is completed or paused
                            if (self.map.paused):
                                self.swap_to_pause_menu()
                            else:
                                self.post_map_loop()
                else:
                    # map is paused. keep drawing it in the background,
                    # but do not update any game sprites
                    self.map.draw_external()
                    self.map.ui_container_group.update(self.map.surface)
            else:
                # main menu is loaded without any map. Clear the entire surface.
                self.window.fill_surface()

        if INFO_PRINT:
            print('[APP][loop] App exiting through main loop')

    def swap_to_post_game_menu(self):
        self.post_map_menu_active = True
        self.swap_start_game_btn_state(True)

        if (self.map.map_success == True):
            msg = f'n/a/_b_Time: {self.timer.get_segment_duration_formatted()} '
            msg += f'n/a/_b_Health: {self.map.player.health:.2f} '
            msg += f'n/a/_b_Fuel: {self.map.player.fuel:.2f} '
            self.POST_GAME_WRAPPER.set_text(msg)
        else:
            msg = f''
            if (self.map.player_death_source == 'Terrain'):
                msg += f't/_i_You::left::a::dent::in::the::terrain '
            elif (self.map.player_death_source == 'Projectile'):
                msg += f't/_i_You::ate::a::bullet::and::exploded '
            msg += 'n/Reset map to try again!'
            self.POST_GAME_WRAPPER.set_text(msg)

        self.MENU_WRAPPER.replace_children(self.POSTGAME_MENU_SUBCONTAINERS)
        self.timer.kill_duration_text()

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

    if run_app:
        # load the app
        APP = PG_App(CF_GLOBAL, CF_WINDOW, CF_TIMER, CF_MENU, CF_MAPS, CF_PLAYERS)
        APP.loop()

    pg.quit()


''' KNOWN BUGS:
    * occasionally, when collecting all coins, the "continue" button wont work.
        the weird thing, it then works for other players, but not that player -- until app restart
        when app is restarted, it typically works again. i have no clue.
'''
