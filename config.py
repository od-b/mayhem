# RGB color tuples
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
    'yellow': (255, 213, 111),
    'navy': (32, 82, 149),
}

# types within the config is meant as a user guideline of the expected type value
CONFIG = {
    'misc': {
        'max_fps': int(60),
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
}
