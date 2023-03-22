from .colors import RGB, PALLETTES
import pygame as pg     # to access constants such as keys


CONFIG = {
    'general': {
        'req_pygame_version': str('2.1.2'),
        # general loop limit, mainly for debugging and configuration purposes:
        # how many failed attempts to allow when performing pseudorandom loops
        # breaks out of forever-loops, and useful to print how close the algorithm was to success
        'loop_limit': int(10000),
    },
    'timing': {
        'fps_limit': int(120),  # frames per second, 0 == uncapped
        'accurate_timing': True   # how strict the time tick function should be. True uses a lot more cpu
    },
    'window': {
        'caption': str('< caption >'),
        'height': int(840),
        'width': int(1400),
        'fill_color': RGB['gray_soft_2'],
        'bounds_fill_color': RGB['offblack'],
        # adjust the bounds of the active game board
        'bounds_padding': {
            'min_x': int(0),
            'max_x': int(0),
            'min_y': int(0),
            'max_y': int(60),
        }
    },
    'ui': {
        'container_padding': 6,
        'CONTAINER': {
            # create the bottom 
        },
        'TEXTBOX': {
            # default textbox option
            'default': {
                'font_path': "media/fonts/JetBrainsMono-SemiBold.ttf",
                'apply_aa': True,
                'font_color': RGB['bone'],
                'border_color': RGB['yellow'],
                'bg_color': RGB['offblack'],
                'border_width': int(1),
                'font_size': int(24),
                # pixels added between the text and its box edges. should be even values (0,2,...):
                'internal_padding_w': int(32),
                'internal_padding_h': int(14),
                'parent_padding': int(8),  # pixels of padding added between a child and its parent
            },
        },
    },
    'physics': {
        # global physics
        # increment and reduce these extremely carefully. Change mass of objects instead
        # gravity: gravitational constant to avoid standstill of objects with mass and 0 velocity
        # also prevents potential division by zero
        'gravity': float(0.02),             # default: 0.02
        # controls the relation multiplier between mass, max velocity and terminal velocity
        'gravity_multiplier': float(0.01)   # default: 0.01
    },
    'environment': {
        # number of obstacles to spawn (center blocks)
        'n_obstacles': int(20),
        # customize the obstacle / terrain blocks
        # padding must be positive
        'BLOCK': {
            'obstacle': {
                'color_pool': PALLETTES['PASTEL_MIX'],
                'min_height': int(10),
                'max_height': int(80),
                'min_width': int(8),
                'max_width': int(90),
                'padding': int(50),
            },
            'obstacle_outline': {
                'color_pool': PALLETTES['ORANGES'],
                'min_height': int(10),
                'max_height': int(16),
                'min_width': int(8),
                'max_width': int(20),
                'padding': int(0),
            },
            'terrain': {
                'color_pool': PALLETTES['SHADES_OF_GRAY'],
                'min_height': int(10),
                'max_height': int(16),
                'min_width': int(8),
                'max_width': int(22),
                'padding': int(0),
            },
        },
    },
    'special_sprites': {
        'UNIQUE_CONTROLLABLE': {
            # key cheatsheet <https://www.pygame.org/docs/ref/key.html>
            # create the main player sprite
            'player': {
                'color': RGB['pastel_yellow_vibrant'],
                'image': None,
                'width': int(30),
                'height': int(40),
                'mass': float(0.1),             # default: 0.1, 0 < mass < 1
                'max_health': int(150),
                'max_mana': int(150),
                'max_velocity_x': float(2.5),   # default: 2.5
                # note: max velocity_y is also affected by mass/gravity
                'max_velocity_y': float(2.5),   # default: 2.5
                # set initial position
                'initial_vectors': {
                    'health': int(100),
                    'mana': int(100),
                    'pos_x': int(400),
                    'pos_y': int(400),
                    'angle': float(0),
                    'velocity_x': float(0),
                    'velocity_y': float(0),
                },
                # configure player keyboard controls
                'controls': {
                    'rotate_c_clockwise': pg.K_a,       # rotate counter-clockwise // steer left
                    'rotate_clockwise':   pg.K_d,       # rotate clockwise // steer right
                    'rotate_c_clockwise': pg.K_LEFT,    # rotate counter-clockwise // steer left
                    'rotate_clockwise':   pg.K_RIGHT,   # rotate clockwise // steer right
                    'accelerate_forward': pg.K_SPACE,   # accelerate towards facing angle
                    'accelerate_reverse': pg.K_c,       # accelerate away from facing angle
                }
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
