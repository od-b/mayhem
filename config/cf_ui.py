from os.path import join as os_path_join
from .colors import RGB

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

CF_TEXT_BOXES = {
    'default': {
        # default textbox style
        'text_bg_color':  RGB['offblack'],
        'font_size':      int(24),
        'font_path':      os_path_join('assets','fonts','JetBrainsMono-SemiBold.ttf'),
        'font_antialias': True,
        'font_color':     RGB['bone']
    }
}
