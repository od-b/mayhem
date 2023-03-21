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
    # pastel
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
    'pastel_offwhite': (255, 242, 204),
    'pastel_yellow_vibrant': (255, 217, 102),
    'pastel_peach_2': (244, 177, 131),
    'pastel_brown': (223, 166, 123),
    # grays
    'darkgray_darker': (42, 42, 42),
    'darkgray_dark': (70, 70, 70),
    'darkgray': (80, 80, 80),
    'darkgray_light': (90, 90, 90),
    'gray_soft': (108, 108, 108),
    'gray_soft_2': (100, 100, 100),
    'gray': (128, 128, 128),
    'gray_medium': (148, 148, 148),
    'gray_light': (168, 168, 158),
    'gray_lighter': (178, 178, 168),
}
''' RGB color tuples -- most are sourced from <https://colorhunt.co> '''

PALLETTES = {
    'PASTEL_MIX': [
        RGB['pastel_orange'],
        RGB['pastel_peach'],
        RGB['pastel_pink'],
        RGB['pastel_yellow'],
        RGB['pastel_yellow_light'],
        RGB['pastel_red'],
        RGB['pastel_blue']
    ],
    'PASTEL_WARM': [
        RGB['pastel_offwhite'],
        RGB['pastel_yellow_vibrant'],
        RGB['pastel_orange'],
        RGB['pastel_peach_2'],
        RGB['pastel_brown'],
        RGB['pastel_red']
    ],
    'SHADES_OF_GRAY': [
        RGB['darkgray_darker'],
        RGB['darkgray_dark'],
        RGB['darkgray'],
        RGB['darkgray_light'],
        RGB['gray_soft'],
        RGB['gray'],
        RGB['gray_medium'],
        RGB['gray_light'],
        RGB['gray_lighter']
    ],
}
''' palletes are lists of colors, typically used for random color selection '''
