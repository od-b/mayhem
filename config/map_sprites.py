import pygame as pg
from os.path import join as os_path_join

from .colors import RGB, RGBA, PALLETTES

CF_TURRETS = {
    'default': {
        'spritesheet_path': os_path_join('assets','spritesheets','coin_1.png'),
        'image_variants': int(9),
        'image_scalar': float(0.1),
    }
}

CF_BLOCKS = {
    #   color_pool: list of one ore more RGB color values
    #   padding:
    #       integer ∈ (0 <= padding < min(max_width, max_height))
    #       sets pixels inbetween similar type blocks when placed
    #   mass: 
    #       how 'tough' the blocks are. Used for collision responses
    #       a block with mass of 0 will ignore all collision with controllables
    'pastel_block': {
        'mass':             float(0),
        'padding':          int(130),
        'min_height':       int(10),
        'max_height':       int(80),
        'min_width':        int(8),
        'max_width':        int(90),
        'color_pool':       PALLETTES['PASTEL_MIX'],
        'alpha_key':        int(255),
        'border_color':     None,
        'border_width':     int(0),
        # alt_surface may be None or a subdict as below
        'alt_surface': {
            'color':        RGB['signal_red'],
            'border_color': None,
            'duration':     int(3000),  # duration in ms once triggered
        },
    },
    'adaptive_block': {
        'mass':             float(0),
        'padding':          int(0),
        'min_height':       int(10),
        'max_height':       int(16),
        'min_width':        int(8),
        'max_width':        int(20),
        'color_pool':       None,
        'alpha_key':        int(255),
        'border_color':     None,
        'border_width':     int(0),
        'alt_surface': {
            'color':        RGB['signal_red'],
            'border_color': None,
            'duration':     int(3000),  # duration in ms once triggered
        },
    },
    'small_gray_block': {
        'mass':             float(0),
        'padding':          int(0),
        'min_height':       int(10),
        'max_height':       int(16),
        'min_width':        int(8),
        'max_width':        int(22),
        'color_pool':       PALLETTES['SHADES_OF_GRAY'],
        'alpha_key':        int(255),
        'border_color':     None,
        'border_width':     int(0),
        'alt_surface': {
            'color':        RGB['signal_red'],
            'border_color': None,
            'duration':     int(3000),  # duration in ms once triggered
        },
    },
}


CF_COINS = {
    'default': {
        'spritesheet_path': os_path_join('assets','spritesheets','coin_1.png'),
        'image_variants': int(9),
        'image_scalar': float(0.1),
        'min_img_iter_frequency': float(0.11),
        'max_img_iter_frequency': float(0.13)
    }
}


CF_PLAYERS = {
    'polygon': {
        # settings that determine how the sprite will look
        'surface': {
            'spritesheets': None,
            # width / height determines size of the polygon
            'width':  int(30),
            'height': int(40),
            # alpha colors must not have an alpha key below 127 without increasing maskcollide threshhold
            'colors': {
                'default':            RGB['P_yellow_vibrant'],
                'collision_cooldown': RGBA['blue_gray_128'],
            }
        },
        'gameplay': {
            'max_health': float(150),       # maximum and initial health
            'max_fuel':   float(150),       # maximum and initial mana
            'min_collision_health_loss': float(15),
            'max_collision_health_loss': float(60)
        },
        # README: physics / phase_durations
        #   Constants that will affect movement, controls, gravity, acceleration, velocity, ..., etc
        #   the values below should allround be set very low rather than to 0. Avoids div by zero, etc.
        #   general gravity is also affected by the map, see .cf_maps.py
        #   W = Weight     -> Typical range in [0.01, 1]. _May_ work for values > 1. Never == 0.
        #   M = Multiplier -> Relative to 1
        #   R = Raw value  -> may be pixels per frame, or similar
        #   S = Seconds    -> Real time +- 0.005ms (if busy loop). Minval is one frame equivalent + epsilon
        'physics': {
            'mass':                     float(1.15),  # M;  more mass => more gravity, faster
            'handling':                 float(0.022), # W;  how responsive steering will be
            'thrust_handling_m':        float(1.6),   # M;  handling multiplier during thrust. may reduce or increase handling.
            'max_acceleration':         float(0.3),   # M;  non-thrust only => limit non-thrust movement (links controls to accel)
            'thrust_magnitude':         float(1.4),   # R;  max magnitude of acceleration during thrust
            'max_velocity':             float(0.7),   # R;  general max velocity
            'terminal_velocity':        float(1.0),   # R;  max velocity, but for falling. (grav constant from map still accumulates)
            'collision_recoil_w':       float(0.3),   # W;  how drastic the bounce-back of a crash will be
        },
        'phase_durations': {
            'thrust_begin':             float(0.6), # M(S); links startin accel, fps and max accel. (longer time to reach max thrust)
            'thrust_end':               float(2.0), # S;    transition between thrust and normal accel (retain thrust longer)
            'collision_recoil_m':       float(0.3), # S(S); links crash velocity, fps and n. recoil frames. (longer impearment)
            'collision_cooldown':       float(1.0), # S;    min time between terrain collision (longer crash immunity)
        },
        # keyboard controls
        'controls': {
            'steer_up':     pg.K_w,
            'steer_left':   pg.K_a,
            'steer_down':   pg.K_s,
            'steer_right':  pg.K_d,
            'thrust':       pg.K_SPACE,
        },
    },
    'corvette': {
        # settings that determine how the sprite will look
        'surface': {
            'spritesheets': {
                'image_scalar': float(0.4),
                'idle': {
                    'path': os_path_join('assets','spritesheets','spaceships','Corvette','Idle.png'),
                    'n_images': int(1),
                },
                'shield': {
                    'path': os_path_join('assets','spritesheets','spaceships','Corvette','Shield.png'),
                    'n_images': int(6),
                },
                ### three phases of thrust -> a:init, b:full thrust, c:falloff ###
                'thrust_a': {
                    'path': os_path_join('assets','spritesheets','spaceships','Corvette','Move.png'),
                    'n_images': int(6),
                },
                'thrust_b': {
                    'path': os_path_join('assets','spritesheets','spaceships','Corvette','Boost.png'),
                    'n_images': int(5),
                },
                'thrust_c': {
                    'path': os_path_join('assets','spritesheets','spaceships','Corvette','Move.png'),
                    'n_images': int(6),
                },
                'destroyed': {
                    'path': os_path_join('assets','spritesheets','spaceships','Corvette','Destroyed.png'),
                    'n_images': int(21),
                }
            },
            # width / height determines size of the polygon
            'width':  int(30),
            'height': int(40),
            # alpha colors must not have an alpha key below 127 without increasing maskcollide threshhold
            'colors': {
                'default':            RGB['P_yellow_vibrant'],
                'collision_cooldown': RGBA['blue_gray_128'],
            }
        },
        'gameplay': {
            'max_health': float(150),       # maximum and initial health
            'max_fuel':   float(150),       # maximum and initial mana
            'min_collision_health_loss': float(15),
            'max_collision_health_loss': float(60)
        },
        'physics': {
            'mass':                     float(1.15),  # M;  more mass => more gravity, faster
            'handling':                 float(0.022), # W;  how responsive steering will be
            'thrust_handling_m':        float(1.6),   # M;  handling multiplier during thrust. may reduce or increase handling.
            'max_acceleration':         float(0.3),   # M;  non-thrust only => limit non-thrust movement (links controls to accel)
            'thrust_magnitude':         float(1.4),   # R;  max magnitude of acceleration during thrust
            'max_velocity':             float(0.7),   # R;  general max velocity
            'terminal_velocity':        float(1.0),   # R;  max velocity, but for falling. (grav constant from map still accumulates)
            'collision_recoil_w':       float(0.3),   # W;  how drastic the bounce-back of a crash will be
        },
        'phase_durations': {
            'thrust_begin':             float(0.6), # M(S); links startin accel, fps and max accel. (longer time to reach max thrust)
            'thrust_end':               float(2.0), # S;    transition between thrust and normal accel (retain thrust longer)
            'collision_recoil_m':       float(0.3), # S(S); links crash velocity, fps and n. recoil frames. (longer impearment)
            'collision_cooldown':       float(1.0), # S;    min time between terrain collision (longer crash immunity)
        },
        # keyboard controls
        'controls': {
            'steer_up':     pg.K_w,
            'steer_left':   pg.K_a,
            'steer_down':   pg.K_s,
            'steer_right':  pg.K_d,
            'thrust':       pg.K_SPACE,
        },
    },
}
