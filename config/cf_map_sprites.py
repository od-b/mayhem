from .colors import RGB, PALLETTES
import pygame as pg     # to access defined constants such as keyboard input keys

# map-related 'static' type sprites, with no velocity or interactive features
BLOCKS = {
    #   texture: not yet implemented. Leave as None
    #   color_pool: list of one ore more RGB color values
    #   padding:
    #       integer ∈ (0 <= padding < min(max_width, max_height))
    #       sets pixels inbetween similar type blocks when placed
    #   mass: 
    #       how 'tough' the blocks are. Used for collision responses
    #       a block with mass of 0 will ignore all collision with controllables
    'pastel_block': {
        'texture':      None,
        'color_pool':   PALLETTES['PASTEL_MIX'],
        'mass':         float(0),
        'padding':      int(130),
        'min_height':   int(10),
        'max_height':   int(80),
        'min_width':    int(8),
        'max_width':    int(90),
    },
    'small_orange_block': {
        'texture':      None,
        'color_pool':   PALLETTES['ORANGES'],
        'mass':         float(0),
        'padding':      int(0),
        'min_height':   int(10),
        'max_height':   int(16),
        'min_width':    int(8),
        'max_width':    int(20),
    },
    'small_gray_block': {
        'texture':      None,
        'color_pool':   PALLETTES['SHADES_OF_GRAY'],
        'mass':         float(0),
        'padding':      int(0),
        'min_height':   int(10),
        'max_height':   int(16),
        'min_width':    int(8),
        'max_width':    int(22),
    },
}

## key cheatsheet docref: https://www.pygame.org/docs/ref/key.html
PLAYERS = {
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
        # gravity is controlled by the map, see .cf_maps.py
        'weights': {
            'max_health':           int(150),       # maximum and initial health
            'max_mana':             int(150),       # maximum and initial mana
            'handling':             float(0.05),    # how effective rotation will be
            'velocity_falloff':     float(0.985),   # change to velocity per frame when not thrusting (multiplier)
            'mass':                 float(0.2),     # mass increases terminal velocity (positive y-max)
            'max_velocity':         float(0.7),     # regular max velocity (pixels per frame)
            'min_velocity':         float(0.001),   # the lowest value velocity can reach
            't_velo':               float(1.4),     # magnitude of velocity during thrust (pixels per frame)
            't_handling':           float(0.05),    # how effective rotation will be during thrust
            't_transition_time':    float(0.7),     # how quickly the added velocity will fall off after thrusting (seconds)
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
NPCS = {
    'small_turret': {
        'width': int(100),
        'height': int(40),
    },
}
