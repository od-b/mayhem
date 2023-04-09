from os.path import join as os_path_join
from .colors import RGB

# bar styles
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


# default, shared font paths. can be replaced individually
regular_path = os_path_join('assets','fonts','JetBrainsMono-Regular.ttf')
italic_path = os_path_join('assets','fonts','JetBrainsMono-Italic.ttf')
semibold_path = os_path_join('assets','fonts','JetBrainsMono-SemiBold.ttf')
semibold_italic_path = os_path_join('assets','fonts','JetBrainsMono-SemiBoldItalic.ttf')
bold_path = os_path_join('assets','fonts','JetBrainsMono-Bold.ttf')

small_font_size = int(24)
large_font_size = int(30)

# text box styles
CF_TEXT_BOXES = {
    'regular_small_bone': {
        'text_bg_color':  None,
        'font_size':      small_font_size,
        'font_path':      regular_path,
        'font_antialias': True,
        'font_color':     RGB['bone']
    },
    'semibold_small_bone': {
        'text_bg_color':  None,
        'font_size':      small_font_size,
        'font_path':      semibold_path,
        'font_antialias': True,
        'font_color':     RGB['bone']
    },
    'semibold_small_dutchwhite': {
        'text_bg_color':  None,
        'font_size':      small_font_size,
        'font_path':      semibold_path,
        'font_antialias': True,
        'font_color':     RGB['dutchwhite']
    },
    'regular_large_bone': {
        'text_bg_color':  None,
        'font_size':      large_font_size,
        'font_path':      regular_path,
        'font_antialias': True,
        'font_color':     RGB['bone']
    },
    'semibold_large_blue': {
        'text_bg_color':  None,
        'font_size':      large_font_size,
        'font_path':      semibold_path,
        'font_antialias': True,
        'font_color':     RGB['blue']
    },
    'bold_large_bone': {
        'text_bg_color':  None,
        'font_size':      large_font_size,
        'font_path':      bold_path,
        'font_antialias': True,
        'font_color':     RGB['bone']
    },
    'bold_large_green': {
        'text_bg_color':  None,
        'font_size':      large_font_size,
        'font_path':      bold_path,
        'font_antialias': True,
        'font_color':     RGB['green']
    },
    'bold_large_darkblue': {
        'text_bg_color':  None,
        'font_size':      large_font_size,
        'font_path':      bold_path,
        'font_antialias': True,
        'font_color':     RGB['blue_dark']
    },
    'bold_xlarge_darkblue': {
        'text_bg_color':  None,
        'font_size':      40,
        'font_path':      bold_path,
        'font_antialias': True,
        'font_color':     RGB['blue_dark']
    }
}
