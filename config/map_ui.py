#### MAP CONFIG SHARED BETWEEN ALL MAPS ####
from os.path import join as os_path_join
from .rect_styles import CF_FILLED_RECT
from .fonts import cf_font
from .cf_window import MAP_TOPLEFT_POS, MAP_MIDTOP_POS

#### UI CONFIG #####

# BARS -- SHARED VALUES
UI_BAR_WIDTH = int(260)     # width of the bar, not including icon
UI_BAR_HEIGHT = int(32)     # this also determines the size of the icons, as they scale with height
UI_BAR_SIZE = (int(260), int(32))

PLAYER_STATUS_BARS = {
    'health': {
        'cf_icon_bar': {
            'cf_bar': {
                'bg': CF_FILLED_RECT['red_on_red'],
                'bar': CF_FILLED_RECT['darkred_on_darkred'],
                'internal_padding_x': int(2),
                'internal_padding_y': int(2),
            },
            'ref_id': ["BAR", "CONST", "HEALTH"],
            'icon_path': os_path_join('assets','images','heart_1.png'),
            'icon_offset': int(3),
            'icon_bg': True,
        },
        'remove_when_empty': False,
        'size': UI_BAR_SIZE
    },
    'fuel': {
        'cf_icon_bar': {
            'cf_bar': {
                'bg': CF_FILLED_RECT['orange_on_orange'],
                'bar': CF_FILLED_RECT['beige_on_beige'],
                'internal_padding_x': int(2),
                'internal_padding_y': int(2),
            },
            'ref_id': ["BAR", "CONST", "FUEL"],
            'icon_path': os_path_join('assets','images','fuel_can_1_lowres.png'),
            'icon_offset': int(3),
            'icon_bg': True,
        },
        'remove_when_empty': False,
        'size': UI_BAR_SIZE
    },
    'shield': {
        'cf_icon_bar': {
            'cf_bar': {
                'bg': CF_FILLED_RECT['sage_on_sage'],
                'bar': CF_FILLED_RECT['green_on_green'],
                'internal_padding_x': int(2),
                'internal_padding_y': int(2),
            },
            'ref_id': ["BAR", "TEMP", "SHIELD"],
            'icon_path': os_path_join('assets','images','protection.png'),
            'icon_offset': int(3),
            'icon_bg': True,
        },
        'remove_when_empty': True,
        'size': UI_BAR_SIZE
    },
    'ghost': {
        'cf_icon_bar': {
            'cf_bar': {
                'bg': CF_FILLED_RECT['blue_on_blue'],
                'bar': CF_FILLED_RECT['lightblue_on_lightblue'],
                'internal_padding_x': int(2),
                'internal_padding_y': int(2),
            },
            'ref_id': ["BAR", "TEMP", "GHOST"],
            'icon_path': os_path_join('assets','images','ghost_modif.png'),
            'icon_offset': int(3),
            'icon_bg': True,
        },
        'remove_when_empty': True,
        'size': UI_BAR_SIZE
    },
}

# size the bar containers width to fit bars, plus a margin of 10
bar_container_width = int(UI_BAR_WIDTH + UI_BAR_HEIGHT + int(3) + 10)
bar_container_height = int(300)
bar_container_pos_x = int(MAP_TOPLEFT_POS[0] + 26)
bar_container_pos_y = int(MAP_TOPLEFT_POS[1] + 11)

text_box_container_width = int(120)
text_box_container_height = int(200)
text_box_pos_x = int(MAP_MIDTOP_POS[0] - int(text_box_container_width/2))
text_box_pos_y = int(MAP_MIDTOP_POS[1])


MAP_CONTAINERS = {
    'bar_container': {
        'size':             (bar_container_width, bar_container_height),
        'position':         (bar_container_pos_x, bar_container_pos_y),
        'child_anchor':     str("top"),
        'child_anchor_offset_x': int(0),
        'child_anchor_offset_y': int(0),
        'child_align_x':    str("container_left"),
        'child_align_y':    str("bottom"),
        'child_padding_x':  int(0),
        'child_padding_y':  int(10),
    },
    'text_container': {
        'text_box_style':   cf_font('large', 'green', 'bold', None),
        'size':             (text_box_container_width, text_box_container_height),
        'position':         (text_box_pos_x, text_box_pos_y),
        'child_anchor':     str("top"),
        'child_anchor_offset_x': int(0),
        'child_anchor_offset_y': int(0),
        'child_align_x':    str("centerx"),
        'child_align_y':    str("bottom"),
        'child_padding_x':  int(0),
        'child_padding_y':  int(10),
    }
}
