''' config file containing various constants and parameter weights '''
from colors import RGB, PALLETTES

# types within the config is meant as a user guideline of the expected type value
CONFIG = {
    'misc': {
        'max_fps': int(60),
        'req_pygame_version': str('2.1.2'),
    },
    'window': {
        'caption': str('< caption >'),
        'height': int(840),
        'width': int(1400),
        'fill_color': RGB['gray_soft_2'],
        'bounds_fill_color': RGB['offblack'],
        'bounds_padding': {
            'min_x': 0,
            'max_x': 0,
            'min_y': 1,
            'max_y': 60,
        }
    },
    'ui': {
        'apply_aa': True,
        'text_color_light': RGB['bone'],
        'text_color_dim': RGB['lightgray'],
        'default_border_color': RGB['yellow'],
        'default_bg_color': RGB['black'],
        'default_border_width': 2,
        'default_font_size': 24,
        'default_padding': 13,  # padding of the ui elements
    },
    'fonts': {
        'semibold': "media/fonts/JetBrainsMono-SemiBold.ttf",
        'bold': "media/fonts/JetBrainsMono-Bold.ttf",
    },
    'physics': {
        'gravity': float(0.001),
    },
    'environment': {
        'n_obstacles': int(10),
        'obstacle_padding': int(50),  # extra padding for the obstacles, on top of spaceship size
        # how many failed attempts to allow when generating obstacles:
        # intercepts forever-loops and prints out how close the algorithm was to success
        'obstacle_placement_attempt_limit': int(10000),
        # customize the obstacle / terrain blocks
        'obstacle_block': {
            'color_pool': PALLETTES['PASTEL_LIGHT'],
            'min_height': int(10),
            'max_height': int(80),
            'min_width': int(8),
            'max_width': int(90),
        },
        'terrain_block': {
            'color_pool': PALLETTES['SHADES_OF_GRAY'],
            'min_height': int(10),
            'max_height': int(16),
            'min_width': int(8),
            'max_width': int(22),
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
