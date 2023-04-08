#### MAP CONFIG SHARED BETWEEN ALL MAPS ####
from os.path import join as os_path_join
from .ui_components import CF_BARS


#### MISC ####

MAP_UPDATE_INTERVALS = {
    'terrain': int(100),
}


#### UI CONFIG #####

# BARS -- SHARED
UI_BAR_WIDTH = int(260)     # width of the bar, not including icon
UI_BAR_HEIGHT = int(32)     # this also determines the size of the icons, as they scale with height
UI_BAR_SIZE = (UI_BAR_WIDTH, UI_BAR_HEIGHT)
UI_BAR_ICON_OFFSET = int(3)
UI_BAR_ICON_BG = True

MAP_BARS = {
    'icon_bar_health': {
        'cf_bar': CF_BARS['red'],
        'icon': os_path_join('assets','images','heart_1.png'),
        'ref_id': ["BAR", "CONST", "HEALTH"],
        'remove_when_empty': False,
        # defaults:
        'icon_offset': UI_BAR_ICON_OFFSET,
        'size': UI_BAR_SIZE,
        'copy_super_bg': UI_BAR_ICON_BG,
    },
    'icon_bar_fuel': {
        'cf_bar': CF_BARS['beige_orange'],
        'icon': os_path_join('assets','images','fuel_can_1_lowres.png'),
        'ref_id': ["BAR", "CONST", "FUEL"],
        'remove_when_empty': False,
        # defaults:
        'icon_offset': UI_BAR_ICON_OFFSET,
        'size': UI_BAR_SIZE,
        'copy_super_bg': UI_BAR_ICON_BG,
    },
    'icon_bar_shield': {
        'cf_bar': CF_BARS['green'],
        'icon': os_path_join('assets','images','protection.png'),
        'ref_id': ["BAR", "TEMP", "SHIELD"],
        'remove_when_empty': True,
        # defaults:
        'icon_offset': UI_BAR_ICON_OFFSET,
        'size': UI_BAR_SIZE,
        'copy_super_bg': UI_BAR_ICON_BG,
    },
    'icon_bar_ghost': {
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

# size the bar containers width to fit bars, plus a margin of 10
bar_container_width = int(UI_BAR_WIDTH + UI_BAR_HEIGHT + UI_BAR_ICON_OFFSET + 10)
# its height doesnt really matter as long as it can fit all the bars
bar_container_height = int(300)

MAP_CONTAINERS = {
    'bar_container': {
        'size':          (int(bar_container_width), int(bar_container_height)),
        'child_anchor':  str("top"),
        'child_align':   str("bottomleft"),
        'child_padding': int(10), # pixels of padding added between the containers children, bars in this case
    },
    # 'text_box_container': {
        
    # }
}
