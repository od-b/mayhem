from .colors import RGB

CF_BAR_STYLES = {
    'default': {
        'bg_alpha_key': int(100),
        'bg_color': RGB['purple'],
        'bg_border_color': RGB['purple'],
        'bg_border_width': int(2),
        'bar_alpha_key': int(200),
        'bar_color': RGB['peach'],
        'bar_border_color': RGB['peach'],
        'bar_border_width': int(2),
        'internal_padding_x': int(3),
        'internal_padding_y': int(3)
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
        'color':            RGB['offblack'],
        'border_color':     RGB['yellow'],
        'border_width':     int(2),
        'bg_alpha_key':     int(255),
        'children_padding': int(40),             # pixels of padding added between the containers children
        'separator_width':  int(2),              # draw a separating line between children
        'separator_color':  RGB['yellow'],       # draw border between children
        'children_styles': {
            'text_box': CF_TEXT_BOXES['default']
        }
    }
}
