
RGB: dict[str, tuple[int, int, int]] = {
    'bone':             (237, 228, 201),
    'darkliver':        (100, 83, 83),
    'sage':             (200, 204, 146),
    'uranianblue':      (185, 230, 255),
    'dutchwhite':       (244, 228, 186),
    'signal_red':       (252, 41, 71),
    'marygold':         (240, 162, 2),
    'orange':           (255, 123, 84),
    'orange_1':         (255, 111, 60),
    'orange_2':         (255, 154, 60),
    'orange_3':         (255, 201, 60),
    'peach':            (255, 178, 107),
    'yellow':           (255, 213, 111),
    'navy':             (32, 82, 149),
    'navy_black':       (21, 82, 99),
    'purple':           (164, 89, 209),
    # pastel colors
    'P_pink':           (255, 172, 172),
    'P_red':            (253, 138, 138),
    'P_red_dark':       (241, 103, 103),
    'P_orange':         (254, 98, 68),
    'P_green':          (158, 161, 212),
    'P_teal':           (134, 200, 188),
    'P_blue':           (158, 161, 212),
    'P_offwhite':       (255, 242, 204),
    'P_yellow':         (241, 247, 181),
    'P_yellow_light':   (255, 246, 189),
    'P_yellow_vibrant': (255, 217, 102),
    'P_peach':          (255, 212, 178),
    'P_peach_2':        (244, 177, 131),
    'P_brown':          (223, 166, 123),
    # grays / blacks
    'black':            (0, 0, 0),
    'offblack':         (24, 26, 31),
    'gray_42':          (42, 42, 42),
    'gray_70':          (70, 70, 70),
    'gray_80':          (80, 80, 80),
    'gray_90':          (90, 90, 90),
    'gray_108':         (108, 108, 108),
    'gray_100':         (100, 100, 100),
    'gray_128':         (128, 128, 128),
    'gray_148':         (148, 148, 148),
    'gray_mix_168':     (168, 168, 158),
    'gray_mix_178':     (178, 178, 168),
}
''' RGB color tuples -- most are sourced from [colorhunt.co](https://colorhunt.co)
    a lot of these are unused, 
'''


RGBA: dict[str, tuple[int, int, int, int]] = {
    'alpha_0':              (0, 0, 0, 0),
    'P_yellow_vibrant_127': (255, 217, 102, 127)
}
''' RGBAlpha color tuples '''


PALLETTES: dict[str, list[tuple[int, int, int]]]  = {
    'PASTEL_MIX': [
        RGB['P_orange'],
        RGB['P_peach'],
        RGB['P_yellow'],
        RGB['P_red'],
        RGB['P_blue']
    ],
    'PASTEL_WARM': [
        RGB['P_offwhite'],
        RGB['P_yellow_vibrant'],
        RGB['P_orange'],
        RGB['P_peach_2'],
        RGB['P_brown'],
        RGB['P_red']
    ],
    'ORANGES': [
        RGB['orange_1'],
        RGB['orange_2'],
        RGB['orange_3'],
        RGB['navy_black']
    ],
    'SHADES_OF_GRAY': [
        RGB['gray_42'],
        RGB['gray_70'],
        RGB['gray_80'],
        RGB['gray_90'],
        RGB['gray_108'],
        RGB['gray_128'],
        RGB['gray_148'],
        RGB['gray_mix_168'],
        RGB['gray_mix_178']
    ],
}
''' palletes are lists of colors, typically used for random color selection '''


def RGB_to_alpha(RGB_list: list[tuple[int, int, int]], alpha: int) -> list[tuple[int, int, int, int]]:
    ''' takes in a list of RGB color and adds an alpha value
        * returns the RGBA list in the same order as given list
        * does not mutate the original list
    '''
    RGBA_list = []

    for rgb in RGB_list:
        rgba = (rgb[0], rgb[1], rgb[2], alpha)
        RGBA_list.append(rgba)

    return RGBA_list
