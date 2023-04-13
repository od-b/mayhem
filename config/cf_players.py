from os.path import join as os_path_join
import pygame as pg
from .colors import RGB, RGBA

# MIN_MAX_PHYSICS = {
#     'mass':                   (0.8, 1.15),    # M;  more mass => more & faster gravity, slower acceleration
#     'handling':               (, 0.022),   # W;  how responsive steering will be
#     'thrust_handling_m':      (, 1.6),     # M;  handling multiplier during thrust. may reduce or increase handling.
#     'max_acceleration':       (, 0.3),     # M;  non-thrust only => limit non-thrust movement (links controls to accel)
#     'thrust_magnitude':       (, 1.4),     # R;  max magnitude of acceleration during thrust
#     'max_velocity':           (, 0.7),     # R;  general max velocity
#     'collision_recoil_w':     (, 0.3),     # W;  how drastic the bounce-back of a crash will be
# }

# README: physics / phase_durations
#   Constants that will affect movement, controls, gravity, acceleration, velocity, ..., etc
#   the values below should allround be set very low rather than to 0. Avoids div by zero, etc.
#   general gravity is also affected by the map, see .cf_maps.py
#   W = Weight     -> Typical range in [0.01, 1]. _May_ work for values > 1. Never == 0.
#   M = Multiplier -> Relative to 1
#   R = Raw value  -> may be pixels per frame, or similar
#   S = Seconds    -> Real time +- 0.005ms (if busy loop). Minval is one frame equivalent + epsilon

CF_PLAYERS = {
    'corvette': {
        'name': str("Corvette"),
        'description': str("Tanky, with great Fuel Capacity. Large and Heavy."),
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
        'gameplay': {
            'fuel_consumption': float(0.02),
            'max_health': float(200),       # maximum and initial health
            'max_fuel':   float(200),       # maximum and initial mana
            'min_collision_health_loss': float(30),
            'max_collision_health_loss': float(40)
        },
        'physics': {
            'mass':                     float(1.25),  # M;  more mass => more gravity, faster
            'handling':                 float(0.018), # W;  how responsive steering will be
            'thrust_handling_m':        float(1.6),   # M;  handling multiplier during thrust. may reduce or increase handling.
            'max_acceleration':         float(0.3),   # M;  non-thrust only => limit non-thrust movement (links controls to accel)
            'thrust_magnitude':         float(1.2),   # R;  max magnitude of acceleration during thrust
            'max_velocity':             float(0.7),   # R;  general max velocity
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
    'bomber': {
        'name': str("Bomber"),
        'description': str("All-Rounder, Balanced and Versatile."),
        'spritesheets': {
            'image_scalar': float(0.5),
            'idle': {
                'path': os_path_join('assets','spritesheets','spaceships','Bomber','Idle.png'),
                'n_images': int(1),
            },
            'shield': {
                'path': os_path_join('assets','spritesheets','spaceships','Bomber','Evasion.png'),
                'n_images': int(9),
            },
            ### three phases of thrust -> a:init, b:full thrust, c:falloff ###
            'thrust_a': {
                'path': os_path_join('assets','spritesheets','spaceships','Bomber','Move.png'),
                'n_images': int(6),
            },
            'thrust_b': {
                'path': os_path_join('assets','spritesheets','spaceships','Bomber','Boost.png'),
                'n_images': int(6),
            },
            'thrust_c': {
                'path': os_path_join('assets','spritesheets','spaceships','Bomber','Move.png'),
                'n_images': int(6),
            },
            'destroyed': {
                'path': os_path_join('assets','spritesheets','spaceships','Bomber','Destroyed.png'),
                'n_images': int(10),
            }
        },
        'gameplay': {
            'fuel_consumption': float(0.02),
            'max_health': float(150),       # maximum and initial health
            'max_fuel':   float(150),       # maximum and initial mana
            'min_collision_health_loss': float(35),
            'max_collision_health_loss': float(50)
        },
        'physics': {
            'mass':                     float(1.0),  # M;  more mass => more gravity, faster
            'handling':                 float(0.023), # W;  how responsive steering will be
            'thrust_handling_m':        float(1.6),   # M;  handling multiplier during thrust. may reduce or increase handling.
            'max_acceleration':         float(0.3),   # M;  non-thrust only => limit non-thrust movement (links controls to accel)
            'thrust_magnitude':         float(1.3),   # R;  max magnitude of acceleration during thrust
            'max_velocity':             float(0.7),   # R;  general max velocity
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
    'fighter': {
        'name': str("Fighter"),
        'description': str("Light, Agile and Fast. Low Health and Fuel Capacity."),
        'spritesheets': {
            'image_scalar': float(0.5),
            'idle': {
                'path': os_path_join('assets','spritesheets','spaceships','Fighter','Idle.png'),
                'n_images': int(1),
            },
            'shield': {
                'path': os_path_join('assets','spritesheets','spaceships','Fighter','Evasion.png'),
                'n_images': int(8),
            },
            ### three phases of thrust -> a:init, b:full thrust, c:falloff ###
            'thrust_a': {
                'path': os_path_join('assets','spritesheets','spaceships','Fighter','Move.png'),
                'n_images': int(6),
            },
            'thrust_b': {
                'path': os_path_join('assets','spritesheets','spaceships','Fighter','Boost.png'),
                'n_images': int(5),
            },
            'thrust_c': {
                'path': os_path_join('assets','spritesheets','spaceships','Fighter','Move.png'),
                'n_images': int(6),
            },
            'destroyed': {
                'path': os_path_join('assets','spritesheets','spaceships','Fighter','Destroyed.png'),
                'n_images': int(15),
            }
        },
        'gameplay': {
            'fuel_consumption': float(0.02),
            'max_health': float(100),       # maximum and initial health
            'max_fuel':   float(100),       # maximum and initial mana
            'min_collision_health_loss': float(45),
            'max_collision_health_loss': float(60)
        },
        'physics': {
            'mass':                     float(0.8),     # M;  more mass => more gravity, faster
            'handling':                 float(0.03), # W;  how responsive steering will be
            'thrust_handling_m':        float(1.45),   # M;  handling multiplier during thrust. may reduce or increase handling.
            'max_acceleration':         float(0.3),   # M;  non-thrust only => limit non-thrust movement (links controls to accel)
            'thrust_magnitude':         float(1.5),   # R;  max magnitude of acceleration during thrust
            'max_velocity':             float(0.7),   # R;  general max velocity
            'collision_recoil_w':       float(0.3),   # W;  how drastic the bounce-back of a crash will be
        },
        'phase_durations': {
            'thrust_begin':             float(0.4), # M(S); links startin accel, fps and max accel. (longer time to reach max thrust)
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

TEST_POLYGON =  {
    #### TEST SPRITE, NOT USABLE WITHOUT ALTERING CODE ####
    'surface': {
        # width / height determines size of the polygon
        # alpha colors must not have an alpha key below 127 without increasing maskcollide threshhold
        'colors': {
            'default':            RGB['P_yellow_vibrant'],
            'collision_cooldown': RGBA['blue_gray_128'],
        }
    },
    'gameplay': {
        'fuel_consumption': float(0.02),
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
}
