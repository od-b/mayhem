from .colors import RGB
import pygame as pg     # to access defined constants such as keyboard input keys

## key cheatsheet docref: https://www.pygame.org/docs/ref/key.html
CF_PLAYERS = {
    'polygon': {
        # settings that determine how the sprite will look
        'surface': {
            'color':            RGB['P_yellow_vibrant'],   # color, if image is not set
            'thrust_color':     RGB['dutchwhite'],              # thrust color
            'texture':          None,       # not yet implemented. Leave as None
            'image':            None,       # not yet implemented. Leave as None
            'width':            int(30),    # width of object surface
            'height':           int(40),    # height of object surface
        },
        # weights that will affect physics and/or gameplay
        # general gravity is also affected by the map, see .cf_maps.py
        'weights': {
            'max_health':           int(150),       # maximum and initial health
            'max_mana':             int(150),       # maximum and initial mana
            'mass':                 float(1.8),     # more mass = more gravity
            'handling':             float(0.05),    # how effective rotation will be
            'accel_falloff':        float(0.98),    # change to velocity per frame when not thrusting (multiplier)
            'max_accel':            float(0.7),     # regular max velocity (pixels per frame)
            't_accel':              float(1.4),     # magnitude of velocity during thrust (pixels per frame)
            't_handling':           float(0.05),    # how effective rotation will be during thrust
            't_transition_time':    float(1.0),     # how quickly the added velocity will fall off after thrusting (seconds)
            'max_velocity':         float(0.7),
            'terminal_velocity':    float(1.0)      # max velocity towards the positive y-axis
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
