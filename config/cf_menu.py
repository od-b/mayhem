from .colors import RGB, RGBA
from .fonts import cf_font, get_path, FONT_ANTIALIAS, FONT_RECT_BG_COLOR, FORMATTING_TRIGGERS
from .cf_window import WINDOW_CENTER
from .rect_styles import CF_FILLED_RECT

menu_width = 800
menu_height = 600
menu_pos_x = WINDOW_CENTER[0] - int(menu_width / 2)
menu_pos_y = WINDOW_CENTER[1] - int(menu_height / 2)
menu_border_width = 4

CF_MENU = {
    'wrapper': {
        # root menu wrapper. subcontainers are by nescessity setup within app.py
        'cf_bg': CF_FILLED_RECT['lightblue_on_blue'],
        'position': (int(menu_pos_x), int(menu_pos_y)),
        'size': (int(menu_width), int(menu_height)),
        'child_anchor': str("top"),
        'child_anchor_offset_x': int(menu_border_width),
        'child_anchor_offset_y': int(menu_border_width),
        'child_align_x': str("container_centerx"),
        'child_align_y': str("bottom"),
        'child_padding_x': int(0),
        'child_padding_y': int(10)
    },
    'fonts': {
        'regular':      cf_font('normal', 'bone', 'regular', None),
        'alt_regular':  cf_font('normal', 'dutchwhite', 'semibold', None),
        'large':        cf_font('large', 'blue', 'semibold', None),
        'alt_large':    cf_font('large', 'blue_dark', 'bold', None),
        'xlarge':       cf_font('xlarge', 'blue_dark', 'bold', None)
    },
    'tooltip_container': {
        'cf_bg': CF_FILLED_RECT['offblack_on_beige'],
        'max_width': int(300),
        'max_height': int(300),
        'child_padding_x': int(10),
        'child_padding_y': int(10),
        'cf_formatting_triggers': FORMATTING_TRIGGERS,
        'title_padding_y': int(4),
        'cf_fonts': {
            'bg_color': FONT_RECT_BG_COLOR,
            'antialias': FONT_ANTIALIAS,
            'color': RGB['bone'],
            'alt_color': RGB['blue_light'],
            'size': int(20),
            'title_size': int(26),
            'paths': {
                'light': get_path('light', None),
                'default': get_path('regular', None),
                'italic': get_path('regular', 'italic'),
                'bold': get_path('bold', None),
            }
        }
    },
    # buttons combine two backgrounds and two fonts
    'buttons': {
        'map_selection': {
            'default': {
                'bg':   CF_FILLED_RECT['beige_on_orange'],
                'font': cf_font(24, 'bone', 'bold', None)
            },
            'alt': {
                'bg':   CF_FILLED_RECT['orange_on_beige'],
                'font': cf_font(26, 'bone', 'bold', None)
            }
        },
    }
}
