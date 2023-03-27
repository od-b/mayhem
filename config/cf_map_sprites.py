from .cf_colors import RGB, PALLETTES
import pygame as pg     # to access defined constants such as keyboard input keys

# map-related 'static' type sprites, with no velocity or interactive features
BLOCKS = {
    #   texture: not yet implemented. Leave as None
    #   color_pool: list of one ore more RGB color values
    #   padding:
    #       integer ∈ (0 <= padding < min(max_width, max_height))
    #       sets pixels inbetween similar type blocks when placed
    #   mass: how tough the blocks are. Used for collision responses
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
            'velocity_falloff': float(0.001),    # general decrease in velocity per frame 1-val
            'handling':         float(0.07),    # how effective steering will be
            # 'breaking':         float(0.07),    # how fast the player will come to a halt upon break
            'mass':             float(0.1),     # mass increases terminal velocity (mass * max_velo.y)
            'max_velocity':     float(1.0),     # default: 1.5
        },
        # keyboard controls
        'controls': {
            'steer_up':     pg.K_w,
            'steer_left':   pg.K_a,
            'steer_down':   pg.K_s,
            'steer_right':  pg.K_d,
            'halt':         pg.K_SPACE,     # slows rate of movement
            'lock':         pg.K_c,         # lock angle in place
        },
    },
}

# i've expanded on the term NPC to include any 'active' sprite that has movement/interactive features
NPCS = {
    'small_turret': {
        'width': int(100),
        'height': int(40),
    },
}
