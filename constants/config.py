from .colors import RGB, PALLETTES
import pygame as pg     # to access constants such as keys


CONFIG = {
    'general': {
        # req_pygame_version:
        #   the required pygame version for the app. will be verified on init.
        #   set this value to your installed version if you would like to try running anyways
        'req_pygame_version': str('2.1.2'),
        # loop_limit:
        #   General loop limit, mainly for debugging and configuration purposes.
        #   In effect, set how many failed attempts to allow when performing pseudorandom
        #   algorithms that have a chance to not being capable of success, depending on settings.
        #   Avoids program crash by breaking out of loops that would never finish,
        #   and can be useful to print how close an algorithm was to success.
        'loop_limit': int(10000),
        # debug_color: high contrast color used for visualizing certain screen elements
        #   should not occur anywhere else on the screen. 
        #   Do not use black as screen defaults to black.
        'debug_color': RGB['uranianblue'],
    },
    'timer': {
        # fps_limit:
        #   due to how tick works with sync limitations, especially at higher values,
        #   fps should be set to one of the following values: [30, 62, 125, 200, 250]
        #   any value will work, but in essence, it will not actually sync correctly to other values
        #   this can be checked by setting accurate_timing to true
        #   for example, when trying to set an FPS of 220, it will automatically snap to 250 instead.
        #   (i'm not entirely sure why this happens, but it's not really an issue.)
        #   setting FPS to 0 will leave it uncapped
        'fps_limit': int(125),      # default: 125
        # accurate_timing:
        #   how strict the time tick function should be.
        #   Uses more resources if set to true
        #   docref: https://www.pygame.org/docs/ref/time.html#pygame.time.Clock.tick_busy_loop
        'accurate_timing': True,    # default: True
    },
    'window': {
        'caption':      str('< app >'),
        'height':       int(840),
        'width':        int(1400),
        'fill_color':   RGB['gray_soft_2'],
        'vsync':        False,
    },
    'map': {
        # adjust the fill color and rect bounds of the active game map
        'fill_color': RGB['offblack'],
        # padded_bounds:
        #   size of the effective game surface
        #   defined using positive padding values with reference to window width/height
        #   e.g. all valyes set to 0 will create a map as large as the entire window surface
        'padded_bounds': {
            'min_x': int(20),
            'max_x': int(20),
            'min_y': int(20),
            'max_y': int(60),
        },
        # number of obstacles to spawn (randomly positioned floating blocks)
        'n_obstacles': int(13),
    },
    'ui': {
        'CONTAINERS': {
            'default': {
                # default container style
                'color':            RGB['offblack'],
                'border_color':     RGB['yellow'],
                'border_width':     int(2),
                'children_padding': int(40),             # pixels of padding added between the containers children
                'separator_width':  int(2),              # draw a separating line between children
                'separator_color':  RGB['yellow'],       # draw border between children
                # TODO: flex padding option, using available space instead of a constang value
            },
        },
        'TEXTBOXES': {
            'default': {
                # default textbox style
                'bg_color':       RGB['offblack'],
                'font_size':      int(24),
                'font_path':      str("media/fonts/JetBrainsMono-SemiBold.ttf"),
                'font_antialias': True,
                'font_color':     RGB['bone'],
            },
        },
    },
    'physics': {
        ## global physics-related constants
        #   increment and reduce these extremely carefully. Change object weights such as mass instead
        # gravity, gravity_direct:
        #   gravitational constants to avoid standstill of objects with mass and 0 velocity
        'gravity': float(0.015),
        # gravity_direct:
        #   literally just adds y-velocity on every frame
        #   avoids complete standstills
        #   also prevents potential division by zero
        'gravity_direct': float(0.002),
    },
    'sprites': {
        'BLOCKS': {
            # <BLOCK>:
            #   texture: not yet implemented. Leave as None
            #   color_pool: list of one ore more RGB color values
            #   padding:
            #       integer ∈ (0 <= padding < min(max_width, max_height))
            #       sets pixels inbetween similar type blocks when placed
            #   mass: how tough the blocks are. Used for collision responses
            'obstacle': {
                'texture':      None,
                'color_pool':   PALLETTES['PASTEL_MIX'],
                'mass':         float(0),
                'padding':      int(130),
                'min_height':   int(10),
                'max_height':   int(80),
                'min_width':    int(8),
                'max_width':    int(90),
            },
            'obstacle_outline': {
                'texture': None,
                'color_pool':   PALLETTES['ORANGES'],
                'mass':         float(0),
                'padding':      int(0),
                'min_height':   int(10),
                'max_height':   int(16),
                'min_width':    int(8),
                'max_width':    int(20),
            },
            'terrain': {
                'texture': None,
                'color_pool':   PALLETTES['SHADES_OF_GRAY'],
                'mass':         float(0),
                'padding':      int(0),
                'min_height':   int(10),
                'max_height':   int(16),
                'min_width':    int(8),
                'max_width':    int(22),
            },
        },
        'UNIQUE': {
            ## key cheatsheet docref: https://www.pygame.org/docs/ref/key.html
            'player': {
                # settings that determine how the sprite will look
                'surface': {
                    'color':    RGB['pastel_yellow_vibrant'],   # color, if image is not set
                    'texture':  None,       # not yet implemented. Leave as None
                    'image':    None,       # not yet implemented. Leave as None
                    'width':    int(30),    # width of object surface
                    'height':   int(40),    # height of object surface
                },
                # weights that will affect physics and/or gameplay
                'weights': {
                    'max_health':       int(150),       # maximum and initial health
                    'max_mana':         int(150),       # maximum and initial mana
                    'handling':         float(0.07),    # how effective steering will be
                    'breaking':         float(0.07),    # how fast the player will come to a halt upon break
                    'mass':             float(0.1),     # mass increases terminal velocity (mass * max_velo.y)
                    'max_velocity':     float(1.5),     # default: 1.5
                },
                # configure player keyboard controls
                'controls': {
                    'steer_up':     pg.K_w,
                    'steer_left':   pg.K_a,
                    'steer_down':   pg.K_s,
                    'steer_right':  pg.K_d,
                    'halt':         pg.K_SPACE,     # slows rate of movement
                    'lock':         pg.K_c,         # lock angle in place
                },
            }
        }
    }
}
''' 
    config dict containing various constants and parameter weights.
    * type conversions within the config is mainly a guideline of the expected type value
    * colors and pallettes within the config refer to a different dict @ ./colors.py
    
    any deletion and/or modification within the dict could completely break the program.
    However, adding additional dict entries will never break anything, as the program only
    accesses the configs internal dicts or values directly, never iteratively
    
    key values that are in caps symbolise a generalized entry pattern.
    For example, all subdictionaries within CONFIG['environment']['BLOCK']
    should follow the pattern of:
    
    '<block_type>': {
        'texture': <pg.Surface>,
        'color_pool': <list: containing minimum one RGB color tuple>,
        'min_height': <int>,
        'max_height': <int>,
        'min_width': <int>,
        'max_width': <int>,
        'padding': <int>,
    },

    This design allows functions to be generalized, reused and modified without
    core changes to the internal algorithm.
    
    For example, if one wants to add a new type of block and use
    spawn_axis_outline to spawn it on the perimeter of a rect, simply add a block type within
    CONFIG['environment']['BLOCK'] following the above specifications, and pass the config reference
    to the function. 
    
    Note: ['special_sprites']['UNIQUE_CONTROLLABLE'] share required entries, but differ from say BLOCKS, 
    in the way that two entries must not share keyboard controls or initial position.
'''
