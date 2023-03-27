from .cf_colors import RGB

UI_SPRITES = {
    'CONTAINERS': {
        # containers for ui elements
        'default': {
            # default container style
            'color':            RGB['offblack'],
            'border_color':     RGB['yellow'],
            'border_width':     int(2),
            'children_padding': int(40),             # pixels of padding added between the containers children
            'separator_width':  int(2),              # draw a separating line between children
            'separator_color':  RGB['yellow'],       # draw border between children
            # TODO: flex padding option, using available space instead of a constang value
        },
    },
    'TEXTBOXES': {
        # textboxes, typically children of containers
        'default': {
            # default textbox style
            'text_bg_color':       RGB['offblack'],
            'font_size':      int(24),
            'font_path':      str("media/fonts/JetBrainsMono-SemiBold.ttf"),
            'font_antialias': True,
            'font_color':     RGB['bone'],
        },
    },
}
