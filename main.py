# import cProfile

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
from modules.PG_ui_bar import UI_Bar

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
        print(f'loaded maps (config map keys): {self.valid_cf_maps_keys}')

        # create the window
        self.window = PG_Window(self.cf_global, self.cf_window)
        ''' object containing main surface window and bounds '''

        # create the timer
        self.timer = PG_Timer(self.cf_global['fps_limit'], self.cf_global['accurate_timing'])
        ''' pygame specific timer object '''

        self.map_UI = Group()
        ''' group of ui sprites that may only be run during a map '''

        self.app_UI = Group()
        ''' group of ui sprites that may be run at any point '''

        # init core app features
        self.timer.block_events(self.cf_global['blocked_events'])
        self.set_up_update_intervals()
        self.set_up_ui_bottom_panel()
        self.fetch_menu_controls()

        self.app_is_running = True
        self.map_is_active = False

    def set_up_update_intervals(self):
        cf_intervals = self.cf_global['update_intervals']

        # set the UI to be updated 4 times per second, through the event queue
        self.EVENT_UPDATE_UI = self.timer.create_event_timer(cf_intervals['ui'], 0)
        ''' custom pygame event call to update ui '''
        self.EVENT_UPDATE_BLOCKS = self.timer.create_event_timer(cf_intervals['blocks'], 0)
        ''' custom pygame event call to update blocks '''

    def set_up_ui_bottom_panel(self):
        ''' specialized, run-once function for creating the map ui
            * these do NOT need to be recreated on map change
        '''

        # create bottom info panel container
        # set width to the size of the map
        # set size and pos to match the available padded bottom space
        width = self.window.map_rect.w
        height = (self.window.height - self.window.map_rect.h - self.window.map_rect.top)
        if (height < 40):
            print("not enough vertical padding to fit the BOTTOM_PANEL.\
                Increase ['map']['padded_bounds'] to display the UI.")
            return

        BOTTOM_PANEL = UI_Container(
            self.cf_ui_containers['bottom_panel'],
            self.window.surface,
            self.window.map_rect.bottomleft,
            (width, height),
            "right",
            "left_right"
        )
        self.map_UI.add(BOTTOM_PANEL)

        # create FPS text
        BOTTOM_PANEL.add_child(
            UI_Text_Box(
                BOTTOM_PANEL.get_child_cf('text_box'),
                self.cf_global,
                ["APP", "TEXT_BOX", "FPS"],
                "FPS: ",
                self.timer.get_fps_int,
                BOTTOM_PANEL.rect.center
            )
        )

        # create time text
        BOTTOM_PANEL.add_child(
            UI_Text_Box(
                BOTTOM_PANEL.get_child_cf('text_box'),
                self.cf_global,
                ["APP", "TEXT_BOX", "TIME"],
                "Time: ",
                self.timer.get_segment_duration_formatted,
                BOTTOM_PANEL.rect.center
            )
        )

    def fetch_menu_controls(self):
        ''' fetch and store player controls from the global config '''
        cf_controls = self.cf_global['menu_controls']
        self.MENU_UP      = int(cf_controls['up'])
        self.MENU_LEFT    = int(cf_controls['left'])
        self.MENU_DOWN    = int(cf_controls['down'])
        self.MENU_RIGHT   = int(cf_controls['right'])
        self.MENU_CONFIRM = int(cf_controls['confirm'])
        self.MENU_BACK    = int(cf_controls['back'])

    def fetch_player_controls(self):
        ''' fetch and store player controls from the map '''
        cf_controls = self.map.get_player_controls()
        self.STEER_UP    = int(cf_controls['steer_up'])
        self.STEER_LEFT  = int(cf_controls['steer_left'])
        self.STEER_DOWN  = int(cf_controls['steer_down'])
        self.STEER_RIGHT = int(cf_controls['steer_right'])
        self.THRUST      = int(cf_controls['thrust'])

    def init_map(self, cf_maps_key: str, player_pos: tuple[int, int]):
        ''' bundle of function calls to initialize the map, player and controls '''

        if not str(cf_maps_key) in self.valid_cf_maps_keys:
            raise ValueError(f'map "{cf_maps_key}" not found')

        self.map = PG_Map(
            self.cf_global,
            self.cf_maps[cf_maps_key],
            self.cf_ui_bar_styles,
            self.cf_ui_containers,
            self.window.map_surface,
            self.timer
        )
        self.map.set_up_terrain()
        self.map.spawn_player(player_pos)
        self.window.set_extended_caption(self.map.name)
        self.fetch_player_controls()

        if not (self.timer.first_init_done):
            self.timer.start_first_segment(self.map.name)
        else:
            self.timer.new_segment(self.map.name, True)

        self.map_is_active = True

    def check_app_events(self):
        ''' events that are not dependand on a map 
            * may share key constants with map_events
        '''

        for event in pg.event.get():
            match (event.type):
                case pg.QUIT:
                   self.app_is_running = False
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
                case self.EVENT_UPDATE_UI:
                    self.app_UI.update()
                case _:
                    pass

    def check_map_events(self):
        ''' events that require a map & player to function '''

        for event in pg.event.get():
            # check if event type matches any triggers
            match (event.type):
                case pg.KEYDOWN:
                    match (event.key):
                        case self.STEER_UP:
                            self.map.player.direction.y -= 1.0
                        case self.STEER_DOWN:
                            self.map.player.direction.y += 1.0
                        case self.STEER_LEFT:
                            self.map.player.direction.x -= 1.0
                        case self.STEER_RIGHT:
                            self.map.player.direction.x += 1.0
                        case self.THRUST:
                            self.map.player.init_begin_thrust()
                        case _:
                            pass
                case pg.KEYUP:
                    match (event.key):
                        case self.STEER_UP:
                            self.map.player.direction.y += 1.0
                        case self.STEER_DOWN:
                            self.map.player.direction.y -= 1.0
                        case self.STEER_LEFT:
                            self.map.player.direction.x += 1.0
                        case self.STEER_RIGHT:
                            self.map.player.direction.x -= 1.0
                        case self.THRUST:
                            self.map.player.init_end_thrust()
                        case _:
                            pass
                case pg.QUIT:
                    self.app_is_running = False
                    self.map_is_active = False
                case self.EVENT_UPDATE_UI:
                    self.map_UI.update()
                    # self.app_UI.update()
                case self.EVENT_UPDATE_BLOCKS:
                    self.map.block_group.update()
                case _:
                    pass

    def loop(self):
        ''' main loop for drawing, checking events and updating the game '''
        
        self.DEBUG_INIT = True

        while (self.app_is_running):
            if (self.DEBUG_INIT):
                self.timer.post_event(self.EVENT_UPDATE_UI)
                self.init_map('map_1', (400, 400))

            # if a map was initiated by the menu, launch the main loop
            while (self.map_is_active):
                # self.window.fill_surface()
                self.map.draw_sprites()
                self.map.check_player_block_collision()
                # loop through events before the display update
                self.check_map_events()
                pg.display.update()

                self.map.player_group.update()
                # update the timer. Also limits the framerate if set to do so
                self.timer.update()

            # check if app was exited or just the map
            if (self.app_is_running):
                # the map is not active, but the app is. this keeps the program active until exited
                self.window.fill_surface()
                self.app_UI.update()
                pg.display.update()

                # loop through menu/app events
                self.check_app_events()


if __name__ == '__main__':
    # initialize pygame and verify the version before anything else
    pg.init()

    if (pg.__version__ != CF_GLOBAL['req_pg_version']):
        msg = 'run "pip install pygame --upgrade" to upgrade, or change the  '
        msg += 'config (_global.py) to your installed version to try anyway.'
        raise VersionError("Pygame", pg.__version__,
            CF_GLOBAL['req_pg_version'], msg
        )

    # load the game
    GAME = PG_App(CF_GLOBAL, CF_WINDOW, CF_MAPS, CF_CONTAINERS, CF_BAR_STYLES)
    # cProfile.run('GAME.loop()')
    GAME.loop()
    pg.quit()
