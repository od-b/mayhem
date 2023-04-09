from os.path import join as os_path_join
from .colors import RGB

#### FONTS ####
# shared default font paths
regular_path = os_path_join('assets','fonts','JetBrainsMono-Regular.ttf')
italic_path = os_path_join('assets','fonts','JetBrainsMono-Italic.ttf')
semibold_path = os_path_join('assets','fonts','JetBrainsMono-SemiBold.ttf')
semibold_italic_path = os_path_join('assets','fonts','JetBrainsMono-SemiBoldItalic.ttf')
bold_path = os_path_join('assets','fonts','JetBrainsMono-Bold.ttf')

# shared default font sizes
small_font_size = int(24)
large_font_size = int(30)
xlarge_font_size = int(40)

font_antialias = True

CF_FONTS = {
    'regular_regular_bone': {
        'path':      regular_path,
        'size':      small_font_size,
        'antialias': font_antialias,
        'color':     RGB['bone'],
        'bg_color':  None
    },
    'semibold_regular_bone': {
        'path':      semibold_path,
        'size':      small_font_size,
        'antialias': font_antialias,
        'color':     RGB['bone'],
        'bg_color':  None
    },
    'semibold_regular_dutchwhite': {
        'path':      semibold_path,
        'size':      small_font_size,
        'antialias': font_antialias,
        'color':     RGB['dutchwhite'],
        'bg_color':  None
    },
    'regular_large_bone': {
        'path':      regular_path,
        'size':      large_font_size,
        'antialias': font_antialias,
        'color':     RGB['bone'],
        'bg_color':  None
    },
    'semibold_large_blue': {
        'path':      semibold_path,
        'size':      large_font_size,
        'antialias': font_antialias,
        'color':     RGB['blue'],
        'bg_color':  None
    },
    'bold_large_bone': {
        'path':      bold_path,
        'size':      large_font_size,
        'antialias': font_antialias,
        'color':     RGB['bone'],
        'bg_color':  None
    },
    'bold_large_green': {
        'path':      bold_path,
        'size':      large_font_size,
        'antialias': font_antialias,
        'color':     RGB['green'],
        'bg_color':  None
    },
    'bold_large_darkblue': {
        'path':      bold_path,
        'size':      large_font_size,
        'antialias': font_antialias,
        'color':     RGB['blue_dark'],
        'bg_color':  None
    },
    'bold_xlarge_darkblue': {
        'path':      bold_path,
        'size':      40,
        'antialias': font_antialias,
        'color':     RGB['blue_dark'],
        'bg_color':  None
    }
}
''' Naming convention: <type_size_RGBcolorName>, e.g. <bold_small_orange>'''


#### BAR STYLES ####
CF_BARS = {
    'green': {
        'bg_color':             RGB['sage'],
        'bg_border_color':      RGB['sage'],
        'bar_color':            RGB['green'],
        'bar_border_color':     RGB['green'],
        'bg_alpha_key':         int(100),
        'bg_border_alpha_key':  int(210),
        'bar_alpha_key':        int(220),
        'bar_border_alpha_key': int(240),
        'bg_border_width':      int(2),
        'bar_border_width':     int(1),
        'internal_padding_x':   int(2),
        'internal_padding_y':   int(2)
    },
    'red': {
        'bg_color':             RGB['red_1'],
        'bg_border_color':      RGB['red_1'],
        'bar_color':            RGB['red_2'],
        'bar_border_color':     RGB['red_2'],
        'bg_alpha_key':         int(70),
        'bg_border_alpha_key':  int(210),
        'bar_alpha_key':        int(210),
        'bar_border_alpha_key': int(240),
        'bg_border_width':      int(2),
        'bar_border_width':     int(1),
        'internal_padding_x':   int(2),
        'internal_padding_y':   int(2)
    },
    'light_blue': {
        'bg_color':             RGB['blue'],
        'bg_border_color':      RGB['blue'],
        'bar_color':            RGB['blue_light'],
        'bar_border_color':     RGB['blue_light'],
        'bg_alpha_key':         int(70),
        'bg_border_alpha_key':  int(210),
        'bar_alpha_key':        int(210),
        'bar_border_alpha_key': int(240),
        'bg_border_width':      int(2),
        'bar_border_width':     int(1),
        'internal_padding_x':   int(2),
        'internal_padding_y':   int(2)
    },
    'beige_orange': {
        'bg_color':             RGB['orange'],
        'bg_border_color':      RGB['orange_1'],
        'bar_color':            RGB['beige'],
        'bar_border_color':     RGB['beige'],
        'bg_alpha_key':         int(70),
        'bg_border_alpha_key':  int(210),
        'bar_alpha_key':        int(210),
        'bar_border_alpha_key': int(240),
        'bg_border_width':      int(2),
        'bar_border_width':     int(1),
        'internal_padding_x':   int(2),
        'internal_padding_y':   int(2)
    },
}
