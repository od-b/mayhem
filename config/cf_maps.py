from os.path import join as os_path_join

from .colors import RGB
from .cf_players import CF_PLAYERS
from .cf_blocks import CF_BLOCKS
from .cf_ui import CF_TEXT_BOXES, CF_BARS

UPDATE_INTERVALS = {
    'terrain': int(100),
}


UI_BAR_WIDTH = int(260)     # width of the bar, not including icon
UI_BAR_HEIGHT = int(32)     # this also determines the size of the icons, as they scale with height
UI_BAR_SIZE = (UI_BAR_WIDTH, UI_BAR_HEIGHT)
UI_BAR_ICON_OFFSET = int(3)
UI_BAR_ICON_BG = True

UI_BARS = {
    'health': {
        'cf_bar': CF_BARS['red'],
        'icon': os_path_join('assets','images','heart_3_lowres.png'),
        'ref_id': ["BAR", "CORE", "HEALTH"],
        'remove_when_empty': False,
        # defaults:
        'icon_offset': UI_BAR_ICON_OFFSET,
        'size': UI_BAR_SIZE,
        'copy_super_bg': UI_BAR_ICON_BG,
    },
    'fuel': {
        'cf_bar': CF_BARS['blue'],
        'icon': os_path_join('assets','images','fuel_can_1_lowres.png'),
        'ref_id': ["BAR", "CORE", "FUEL"],
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

CF_MAPS = {
    # a map is a setup config for the active part of the game surface
    'map_1': {
        'name':                 str('Map 1'),
        'available_time':       int(0),     # time before map is failed, in milliseconds
        'fill_color':           RGB['offblack'],
        'n_obstacles':          int(13),
        ## physics-related weights that may differ between maps
        # these are read by other sprites on creation.
        # gravitational constants. gravity_c must not be 0, or division by zero may occur.
        'gravity_m':            float(0.004),      # gravity multiplier. range = [1.0, 2.0]
        'gravity_c':            float(0.003),      # gravitational constant. 0 = no gravity
        # sprite settings:
        'upd_interval': UPDATE_INTERVALS,
        'player': CF_PLAYERS['polygon'],
        'blocks': {
            'edge_outline':         CF_BLOCKS['small_gray_block'],
            'obstacle':             CF_BLOCKS['pastel_block'],
            'obstacle_outline':     CF_BLOCKS['adaptive_block'],
        },
        'ui_containers': CONTAINERS,
        'ui_bars': UI_BARS
        # time between sprite updates, per type. Values are millisecs between updates
        # these values will typically have an applied variance of 0.5%
    }
}
