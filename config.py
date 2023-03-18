
# RGB color tuples -- most sourced from <https://colorhunt.co/>
RGB = {
    'black': (0, 0, 0),
    'offblack': (24, 26, 31),
    'darkgray': (80, 80, 80),
    'gray': (128, 128, 128),
    'lightgray': (168, 168, 158),
    'bone': (237, 228, 201),
    'darkliver': (100, 83, 83),
    'sage': (200, 204, 146),
    'uranianblue': (185, 230, 255),
    'dutchwhite': (244, 228, 186),
    'marygold': (240, 162, 2),
    'orange': (255, 123, 84),
    'peach': (255, 178, 107),
    'peach': (255, 178, 107),
    'yellow': (255, 213, 111),
    'navy': (32, 82, 149),
    'purple': (164, 89, 209),
    'pastel_pink': (245, 234, 234),
    'pastel_red': (253, 138, 138),
    'pastel_red_dark': (241, 103, 103),
    'pastel_peach': (255, 212, 178),
    'pastel_orange': (255, 191, 169),
    'pastel_yellow': (241, 247, 181),
    'pastel_yellow_light': (255, 246, 189),
    'pastel_green': (158, 161, 212),
    'pastel_teal': (134, 200, 188),
    'pastel_blue': (158, 161, 212),
}

PALLETTES = {
    'PASTEL_LIGHT': [
        RGB['pastel_orange'],
        RGB['pastel_peach'],
        RGB['pastel_pink'],
        RGB['pastel_yellow'],
        RGB['pastel_red'],
        RGB['pastel_teal'],
        RGB['pastel_blue']
    ],
}

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
        'fill_color': RGB['offblack'],
        'bounds_padding': {
            'min_x': 1,
            'max_x': 1,
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
        'default_font_size': 20,
        'default_padding': 10,  # padding of the ui elements
    },
    'fonts': {
        'semibold': "media/fonts/JetBrainsMono-SemiBold.ttf",
        'bold': "media/fonts/JetBrainsMono-Bold.ttf",
    },
    'environment': {
        'n_obstacles': int(60),
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
            'color_pool': PALLETTES['PASTEL_LIGHT'],
            'min_height': int(10),
            'max_height': int(80),
            'min_width': int(8),
            'max_width': int(90),
        },
    },
    'spaceship': {
        'width': int(40),
        'height': int(40),
    }
}
