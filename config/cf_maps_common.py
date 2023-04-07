#### MAP CONFIG SHARED BETWEEN ALL MAPS ####
from os.path import join as os_path_join
from pygame import Surface, init as pg_init
from .cf_ui import CF_BARS


#### MISC ####

UPDATE_INTERVALS = {
    'terrain': int(100),
}


#### GENERIC SPRITES ####

CF_COIN = {
    'spritesheet_path': os_path_join('assets','spritesheets','coin_1.png'),
    'image_variants': int(9),
    'image_scalar': float(0.1),
    'min_img_iter_frequency': float(0.11),
    'max_img_iter_frequency': float(0.13),
    'width': int(60),
    'height': int(60)
}


#### UI CONFIG #####

UI_BAR_WIDTH = int(260)     # width of the bar, not including icon
UI_BAR_HEIGHT = int(32)     # this also determines the size of the icons, as they scale with height
UI_BAR_SIZE = (UI_BAR_WIDTH, UI_BAR_HEIGHT)
UI_BAR_ICON_OFFSET = int(3)
UI_BAR_ICON_BG = True

BARS = {
    'health': {
        'cf_bar': CF_BARS['red'],
        'icon': os_path_join('assets','images','heart_1.png'),
        'ref_id': ["BAR", "CONST", "HEALTH"],
        'remove_when_empty': False,
        # defaults:
        'icon_offset': UI_BAR_ICON_OFFSET,
        'size': UI_BAR_SIZE,
        'copy_super_bg': UI_BAR_ICON_BG,
    },
    'fuel': {
        'cf_bar': CF_BARS['beige_orange'],
        'icon': os_path_join('assets','images','fuel_can_1_lowres.png'),
        'ref_id': ["BAR", "CONST", "FUEL"],
        'remove_when_empty': False,
        # defaults:
        'icon_offset': UI_BAR_ICON_OFFSET,
        'size': UI_BAR_SIZE,
        'copy_super_bg': UI_BAR_ICON_BG,
    },
    'shield': {
        'cf_bar': CF_BARS['green'],
        'icon': os_path_join('assets','images','protection.png'),
        'ref_id': ["BAR", "TEMP", "SHIELD"],
        'remove_when_empty': True,
        # defaults:
        'icon_offset': UI_BAR_ICON_OFFSET,
        'size': UI_BAR_SIZE,
        'copy_super_bg': UI_BAR_ICON_BG,
    },
    'ghost': {
        'cf_bar': CF_BARS['light_blue'],
        'icon': os_path_join('assets','images','ghost_modif.png'),
        'ref_id': ["BAR", "TEMP", "GHOST"],
        'remove_when_empty': True,
        # defaults:
        'icon_offset': UI_BAR_ICON_OFFSET,
        'size': UI_BAR_SIZE,
        'copy_super_bg': UI_BAR_ICON_BG,
    },
}

BAR_CONTAINER_WIDTH = UI_BAR_WIDTH + UI_BAR_HEIGHT + UI_BAR_ICON_OFFSET + 10
BAR_CONTAINER_HEIGHT = 300

CONTAINERS = {
    'bar_container': {
        'size': (int(BAR_CONTAINER_WIDTH), int(BAR_CONTAINER_HEIGHT)),
        ''
        'child_padding': int(10), # pixels of padding added between the containers children, bars in this case
    }
}