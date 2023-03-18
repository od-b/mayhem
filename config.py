
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
        RGB['pastel_red'],
        RGB['pastel_yellow'],
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
        # see PG_window.py for offset explanation
        'surface_offset_x': int(1),
        'surface_offset_y': int(1),
        'fill_color': RGB['offblack'],
    },
    'ui': {
        'apply_aa': True,
        'text_color_light': RGB['bone'],
        'text_color_dim': RGB['lightgray'],
        'default_border_color': RGB['yellow'],
        'default_bg_color': RGB['black'],
        'default_border_width': 2,
        'default_font_size': 20,
        'default_child_offset': 10,
    },
    'fonts': {
        'semibold': "media/fonts/JetBrainsMono-SemiBold.ttf",
        'bold': "media/fonts/JetBrainsMono-Bold.ttf",
    },
    'environment': {
        'n_obstacles': int(3),
        'obstacle': {
            'color_pool': [
                RGB['peach'],
                RGB['orange'],
                RGB['marygold'],
                RGB['dutchwhite']
            ],
            'min_height': int(10),
            'max_height': int(20),
            'min_width': int(8),
            'max_width': int(),
        },
    },
}
