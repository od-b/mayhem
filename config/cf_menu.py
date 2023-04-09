from .colors import RGB, RGBA
from .ui_components import CF_BARS, CF_TEXT_BOXES
from .cf_window import WINDOW_CENTER

menu_width = int(800)
menu_height = int(600)
menu_pos_x = int(WINDOW_CENTER[0] - int(menu_width / 2))
menu_pos_y = int(WINDOW_CENTER[1] - int(menu_height / 2))

N_SUBCONTAINERS = int(4)

WRAPPER = {
    'position': (menu_pos_x, menu_pos_y),
    'size': (menu_width, menu_height),
    'child_anchor': str("top"),
    'child_align': str("bottom"),
    'child_padding': int(14),
    'bg_color': RGB['blue_light'],
    'border_color': RGB['blue'],
    'border_width': int(6),
}

# subcontainer calculations must be changed/swapped in case of anchor/align change in wrapper
combined_padding_y = int(WRAPPER['child_padding'] * (N_SUBCONTAINERS + 1))
combined_padding_x = int(WRAPPER['child_padding'] * 2)
SUBCONTAINER_HEIGHT = int((menu_height - combined_padding_y) / (N_SUBCONTAINERS))
SUBCTONAINER_WIDTH = int(menu_width - combined_padding_x)

SUBCONTAINER = {
    'position': (menu_pos_x, menu_pos_y),
    'size': (SUBCTONAINER_WIDTH, SUBCONTAINER_HEIGHT),
    'child_anchor': str("left"),
    'child_align': str("right"),
    'child_padding': int(4),
    #### debug draw
    # 'bg_color': None,
    # 'border_color': None,
    # 'border_width': int(0)
    # 'bg_color': RGB['white'],
    # 'border_color': RGB['offblack'],
    # 'border_width': int(2)
}

CF_MENU = {
    'n_subcontainers': N_SUBCONTAINERS,
    'containers': {
        'wrapper': WRAPPER,
        'subcontainer': SUBCONTAINER
    },
    'text_box_styles': {
        'small': CF_TEXT_BOXES['regular_small_bone'],
        'alt_small': CF_TEXT_BOXES['semibold_small_dutchwhite'],
        'large': CF_TEXT_BOXES['semibold_large_blue'],
        'alt_large': CF_TEXT_BOXES['bold_large_darkblue'],
        'xlarge': CF_TEXT_BOXES['bold_xlarge_darkblue']
    }
}
