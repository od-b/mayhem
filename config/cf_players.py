from .colors import RGB, RGBA
import pygame as pg     # to access defined constants such as keyboard input keys

## key cheatsheet docref: https://www.pygame.org/docs/ref/key.html
CF_PLAYERS = {
    'polygon': {
        # settings that determine how the sprite will look
        'surface': {
            # width / height determines size of the polygon
            'width':            int(30),
            'height':           int(40),
            'color':            RGB['P_yellow_vibrant'],   # color, if image is not set
            'color_post_crash': RGBA['P_yellow_vibrant_127'],
            'thrusters_color':  RGB['dutchwhite'],              # thrust color
        },
        'gameplay': {
            'max_health':       int(150),       # maximum and initial health
            'max_mana':         int(150),       # maximum and initial mana
        },
        # weights that will affect physics and/or steering capability
        # general gravity is also affected by the map, see .cf_maps.py
        'weights': {
            'mass':                     float(1.4),     # more mass == more gravity. No mass (1.0) == no gravity & no collisions
            'handling':                 float(0.025),   # how responsive steering will be
            'thrust_handling':          float(0.05),    # how responsive steering will be, during thrust
            'max_acceleration':         float(0.7),     # regular max acceleration
            'thrust_acceleration':      float(1.4),     # magnitude of acceleration during thrust
            'acceleration_multiplier':  float(0.985),   # multiplier for to acceleration, per frame when not thrusting
            'max_velocity':             float(0.7),     # general max velocity
            'terminal_velocity':        float(1.0),     # max velocity towards the positive y-axis
        },
        'phase_durations': {
            'thrust_end':               int(1000),     # transition between thrust accel and normal
            'collision_cooldown':       int(1000),     # seconds of 
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
