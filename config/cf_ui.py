from .colors import RGB

CF_BAR_STYLES = {
    'default': {
        'bg_color':             RGB['purple'],
        'bg_alpha_key':         int(110),
        'bg_border_color':      RGB['purple'],
        'bg_border_alpha_key':  int(150),
        'bg_border_width':      int(2),
        'bar_color':            RGB['peach'],
        'bar_alpha_key':        int(210),
        'bar_border_color':     RGB['peach'],
        'bar_border_alpha_key': int(240),
        'bar_border_width':     int(2),
        'internal_padding_x':   int(3),
        'internal_padding_y':   int(3)
    }
}

CF_TEXT_BOXES = {
    'default': {
        # default textbox style
        'text_bg_color':  RGB['offblack'],
        'font_size':      int(24),
        'font_path':      str("media/fonts/JetBrainsMono-SemiBold.ttf"),
        'font_antialias': True,
        'font_color':     RGB['bone']
    }
}

CF_CONTAINERS = {
    # containers for ui elements
    'bottom_panel': {
        # default container style
        'bg_color':         RGB['offblack'],
        'bg_alpha_key':     int(255),
        'border_color':     RGB['yellow'],
        'border_width':     int(2),
        'children_padding': int(40),             # pixels of padding added between the containers children
        'separator_width':  int(2),              # draw a separating line between children
        'separator_color':  RGB['yellow'],       # draw border between children
        'children_styles': {
            'text_box': CF_TEXT_BOXES['default'],
            'bar':      CF_BAR_STYLES['default']
        }
    }
}
