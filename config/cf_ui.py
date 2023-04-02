from .colors import RGB

CF_BARS = {
    'default': {
        'bg_color':             RGB['purple'],
        'bg_alpha_key':         int(110),
        'bg_border_color':      RGB['purple'],
        'bg_border_alpha_key':  int(110),
        'bg_border_width':      int(1),
        'bar_color':            RGB['peach'],
        'bar_alpha_key':        int(210),
        'bar_border_color':     RGB['white'],
        'bar_border_alpha_key': int(240),
        'bar_border_width':     int(1),
        'internal_padding_x':   int(1),
        'internal_padding_y':   int(1)
    }
}

CF_TEXT_BOXES = {
    'default': {
        # default textbox style
        'text_bg_color':  RGB['offblack'],
        'font_size':      int(24),
        'font_path':      str("assets/fonts/JetBrainsMono-SemiBold.ttf"),
        'font_antialias': True,
        'font_color':     RGB['bone']
    }
}

CF_CONTAINERS = {
    # containers for ui elements
    'bottom_panel': {
        # default container style
        'children_padding': int(40),             # pixels of padding added between the containers children
        'children_styles': {
            'text_box': CF_TEXT_BOXES['default'],
            'bar':      CF_BARS['default']
        }
    },
    'test': {
        # default container style
        'children_padding': int(10),             # pixels of padding added between the containers children
        'children_styles': {
            'text_box': CF_TEXT_BOXES['default'],
            'bar':      CF_BARS['default']
        }
    },
}
