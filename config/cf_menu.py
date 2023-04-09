from .colors import RGB
from .ui_components import CF_BARS, CF_FONTS
from .cf_window import WINDOW_CENTER

menu_width = 800
menu_height = 600
menu_pos_x = WINDOW_CENTER[0] - int(menu_width / 2)
menu_pos_y = WINDOW_CENTER[1] - int(menu_height / 2)
menu_border_width = 6

CF_MENU = {
    'wrapper': {
        # root menu wrapper. subcontainers are by nescessity setup within app.py
        'position': (int(menu_pos_x), int(menu_pos_y)),
        'size': (int(menu_width), int(menu_height)),
        'child_anchor': str("top"),
        'child_anchor_offset_x': int(menu_border_width),
        'child_anchor_offset_y': int(menu_border_width),
        'child_align_x': str("container_centerx"),
        'child_align_y': str("bottom"),
        'child_padding_x': int(0),
        'child_padding_y': int(10),
        'bg_color': RGB['blue_light'],
        'border_color': RGB['blue'],
        'border_width': int(menu_border_width),
    },
    'fonts': {
        'regular':      CF_FONTS['regular_regular_bone'],
        'alt_regular':  CF_FONTS['semibold_regular_dutchwhite'],
        'large':        CF_FONTS['semibold_large_blue'],
        'alt_large':    CF_FONTS['bold_large_darkblue'],
        'xlarge':       CF_FONTS['bold_xlarge_darkblue']
    }
}
