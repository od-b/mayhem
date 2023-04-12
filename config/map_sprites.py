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
    #   spacing:
    #       integer ∈ (0 <= spacing < min(max_width, max_height))
    #       pixels inbetween similar type blocks when placed
    #   mass: 
    #       how 'tough' the blocks are. Used for collision responses
    #       a block with mass of 0 will ignore all collision with controllables
    'pastel_block': {
        'mass':             float(0),
        'spacing':          int(130),
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
        'spacing':          int(0),
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
        'spacing':          int(0),
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

