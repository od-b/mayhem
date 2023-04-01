from .colors import RGB, RGBA
import pygame as pg     # to access defined constants such as keyboard input keys

## key cheatsheet docref: https://www.pygame.org/docs/ref/key.html
CF_PLAYERS = {
    'polygon': {
        # settings that determine how the sprite will look
        'surface': {
            # width / height determines size of the polygon
            'width':  int(30),
            'height': int(40),
            # alpha colors must not have an alpha key below 127 without increasing maskcollide threshhold
            'colors': {
                'default':            RGB['P_yellow_vibrant'],
                'collision_cooldown': RGBA['P_yellow_vibrant_128'],
            }
        },
        'gameplay': {
            'max_health': int(150),       # maximum and initial health
            'max_mana':   int(150),       # maximum and initial mana
        },
        # weights that will affect physics and/or steering capability
        # general gravity is also affected by the map, see .cf_maps.py
        'weights': {
            'mass':                     float(1.4),     # more mass == more gravity. The player must have some mass, or code breaks.
            'handling':                 float(0.025),   # how responsive steering will be
            'thrust_handling_m':          float(2.0),    # handling multiplier during thrust
            'collision_cooldown_handling_m': float(1.0),    # handling multiplier during collision cooldown
            'max_acceleration':         float(0.7),     # regular max acceleration
            'thrust_acceleration':      float(1.4),     # magnitude of acceleration during thrust
            'acceleration_multiplier':  float(0.985),   # multiplier for to acceleration, per frame when not thrusting
            'max_velocity':             float(0.7),     # general max velocity
            'terminal_velocity':        float(1.0),     # max velocity towards the positive y-axis
            'collision_recoil_force':   float(0.3),     # max velocity towards the positive y-axis
        },
        # WARNING: the values below must not be set too low without adding a bunch of if-conditions
        # try and see.
        'phase_durations': {
            'collision_recoil':         float(0.3),     # weight<0,1]; links crash velocity, fps and n. recoil frames. 0 == death
            'thrust_begin':             float(0.6),     # weight<0,1]; links startin accel, fps and max accel. 0 == instant thrust
            'thrust_end':               float(1.0),     # seconds; transition between thrust and normal accel
            'collision_cooldown':       float(1.0),    # seconds; min time between terrain collision
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

# i've expanded on the term NPC to include any 'active' sprite that has velocity and/or interactive features
CF_NPCS = {
    'small_turret': {
        'width': int(100),
        'height': int(40),
    },
}
