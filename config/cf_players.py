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
            'max_health': float(150),       # maximum and initial health
            'max_fuel':   float(150),       # maximum and initial mana
            'min_collision_health_loss': float(15),
            'max_collision_health_loss': float(60),
            'fuel_consumption': float(0.01)
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
            'mass':                     float(1.25),  # M;  more mass => more gravity, faster
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

# i've expanded on the term NPC to include any 'active' sprite that has velocity and/or interactive features
CF_NPCS = {
    'small_turret': {
        'width': int(100),
        'height': int(40),
    },
}
