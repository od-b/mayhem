from .colors import RGB
from .map_sprites import CF_BLOCKS, CF_COINS
from .map_ui import MAP_CONTAINERS, PLAYER_STATUS_BARS

#### MISC ####

MAP_UPDATE_INTERVALS = {
    'terrain': int(100),
    'player_img_cycle': int(30),
    'coin_img_cycle': int(10),
}


CF_MAPS = {
    # a map is a setup config for the active part of the game surface
    'map_1': {
        'name':            str('Map 1'),
        'fill_color':      RGB['offblack'],
        'overlap_color':   RGB['signal_red'],  # used for visualizing overlapping masks / misc
        # 'gravity_c':       float(0),     # every frame gravitational incrementor
        'gravity_c':       float(0.003),     # every frame gravitational incrementor
        # nested configs; sets the config dicts of "children". can be shared or unique
        'cf_spawning': {
            'coins': {
                'n_coins':         int(20),
                'min_terrain_offset': int(11),      # min. offset to terrain
                'min_spread': int(120),     # min. distance to another coin
            },
            'obstacles': {
                'n_obstacles':     int(13),
                # min/max distance inbetween generated obstacles
                'min_spacing_x': int(45),
                'min_spacing_y': int(45)
            },
            'player': {
                # how close to an existing sprite the player can spawn
                # values are padded ON TOP OF players idle image bounding rect
                'min_terrain_offset_x': int(20),
                'min_terrain_offset_y': int(20)
            }
        },
        'map_sprites': {
            'blocks': {
                'edge_outline':     CF_BLOCKS['small_gray_block'],
                'obstacle':         CF_BLOCKS['pastel_block'],
                'obstacle_outline': CF_BLOCKS['adaptive_block'],
            },
            'coin': CF_COINS['default']
        },
        'ui_sprites': {
            'containers': MAP_CONTAINERS,
            'bars': {
                'player_status': PLAYER_STATUS_BARS
            }
        },
        'upd_intervals': MAP_UPDATE_INTERVALS,
        # time between sprite updates, per type. Values are millisecs between updates
        # these values will typically have an applied variance of 0.5%
    }
}
