from .colors import RGB, PALLETTES

CONFIG = {
    'general': {
        'req_pygame_version': str('2.1.2'),
        # placement_attempt_limit:
        # how many failed attempts to allow when performing pseudorandom loops
        # intercepts forever-loops and prints out how close the algorithm was to success
        'loop_limit': int(10000),
    },
    'exceptions': {
        'version_error_fatal': True,  # whether to warn or quit if version is wrong
    },
    'timing': {
        'fps_limit': int(60),  # frames per second, None == uncapped
    },
    'window': {
        'caption': str('< caption >'),
        'height': int(840),
        'width': int(1400),
        'fill_color': RGB['gray_soft_2'],
        'bounds_fill_color': RGB['offblack'],
        'bounds_padding': {
            'min_x': int(40),
            'max_x': int(40),
            'min_y': int(40),
            'max_y': int(60),
        }
    },
    'ui': {
        'default': {
            # multipurpose general values
            'padding': 6,
        },
        'textbox': {
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
        # gravitational constant to avoid standstill of objects with mass and 0 velocity
        # also prevents potential division by zero
        'gravity': float(0.0001),
    },
    'environment': {
        # starting number of obstacles to spawn
        'n_obstacles': int(10),
        # customize the obstacle / terrain blocks
        'obstacle_block': {
            'color_pool': PALLETTES['PASTEL_LIGHT'],
            'min_height': int(10),
            'max_height': int(80),
            'min_width': int(8),
            'max_width': int(90),
            'padding': int(50),
        },
        'terrain_block': {
            'color_pool': PALLETTES['SHADES_OF_GRAY'],
            'min_height': int(10),
            'max_height': int(16),
            'min_width': int(8),
            'max_width': int(22),
            'padding': int(0),
        },
    },
    'player': {
        'color': RGB['black'],
        'image': None,
        'width': int(40),
        'height': int(40),
        'mass': float(0.1),
        'max_health': int(150),
        'max_mana': int(150),
        'max_velocity_x': float(1),
        'max_velocity_y': float(1),
        'initial_vectors': {
            'health': int(100),
            'mana': int(100),
            'pos_x': int(400),
            'pos_y': int(400),
            'angle': float(0),
            'velocity_x': float(0),
            'velocity_y': float(0),
        },
    }
}
''' config dict containing various constants and parameter weights.
    * type conversions within the config is mainly a guideline of the expected type value
    * colors and pallettes within the config refer to a different dict @ ./colors.py
'''
