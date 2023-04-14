from .colors import RGB
from .map_sprites import CF_BLOCKS, CF_COINS, CF_TURRETS
from .map_ui import MAP_CONTAINERS, PLAYER_STATUS_BARS
from os.path import join as os_path_join

MAP_UPDATE_INTERVALS = {
    'terrain': int(100),
    'player_img_cycle': int(30)
    # 'coin_img_cycle': int(10),
}

CF_MAPS = {
    # a map is a setup config for the active part of the game surface
    'map_1': {
        'name':            str('Map 1'),
        'fill_color':      RGB['offblack'],    # fill color, if bg_image is set to None
        'bg_image':        os_path_join('assets','backgrounds','bg_nebula_blue_green.png'),
        'overlap_color':   RGB['white'],  # used for visualizing overlapping masks / misc
        # 'gravity_c':       float(0),     # every frame gravitational incrementor
        'gravity_c':       float(0.003),     # every frame gravitational incrementor
        'cf_spawning': {
            # map-specific sprite settings and parameters related to their spawning process
            'coins': {
                'n_coins':            int(13),
                'min_terrain_offset': int(11),  # min. offset to terrain
                'min_spread':         int(160), # min. distance to another coin
                'cf_coin':            CF_COINS['default'],
            },
            'turrets': {
                'n_turrets':          int(3),
                'min_edge_offset_x':  int(140),
                'min_edge_offset_y':  int(140),
                'min_spacing_x':      int(350),  # spacing between other turrets
                'min_spacing_y':      int(250),  # spacing between other turrets
                'cf_turrets': [
                    # list of available turrets that the map can spawn
                    # map spawns one of each, in order, until/if n_turrets is reached, then picks a random one
                    CF_TURRETS['missile_launcher_x4'],
                    CF_TURRETS['missile_launcher_x1'],
                    CF_TURRETS['missile_launcher_x2'],
                ],
            },
            'obstacle_blocks': {
                'n_obstacles':   int(8),
                # min/max distance inbetween generated obstacles
                'min_spacing_x': int(165),
                'min_spacing_y': int(100),
                'min_height':    int(10),
                'max_height':    int(80),
                'min_width':     int(8),
                'max_width':     int(90),
                'cf_block':      CF_BLOCKS['pastel_mix'],
                'outline_blocks': {
                    'min_width':    int(8),
                    'max_width':    int(20),
                    'min_height':   int(10),
                    'max_height':   int(16),
                    'facing':       int(1),  # -1 is along inner axis, 0 is centered, 1 is outwards
                    'padding':      int(0),
                    'cf_block':     CF_BLOCKS['no_pallette'],
                }
            },
            'map_outline_blocks': {
                'facing':     int(-1),  # -1 is along inner axis, 0 is centered, 1 is outwards
                'min_width':  int(8),
                'max_width':  int(22),
                'min_height': int(10),
                'max_height': int(16),
                'padding':    int(0),  # space between each block
                'cf_block':   CF_BLOCKS['shades_of_gray']
            },
            'player': {
                # how close to an existing sprite the player can spawn
                # values are padded ON TOP OF players idle image bounding rect
                'min_terrain_offset_x': int(30),
                'min_terrain_offset_y': int(30)
            }
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
    },
    'map_2': {
        'name':            str('Map 2'),
        'fill_color':      RGB['offblacker'],    # fill color, if bg_image is set to None
        'bg_image':        os_path_join('assets','backgrounds','bg_planets_dark.png'),
        'overlap_color':   RGB['white'],  # used for visualizing overlapping masks / misc
        # 'gravity_c':       float(0),     # every frame gravitational incrementor
        'gravity_c':       float(0.0015),     # every frame gravitational incrementor
        # nested configs; sets the config dicts of "children". can be shared or unique
        'cf_spawning': {
            # map-specific sprite settings and parameters related to their spawning process
            'coins': {
                'n_coins':            int(20),
                'min_terrain_offset': int(14),  # min. offset to terrain
                'min_spread':         int(200), # min. distance to another coin
                'cf_coin':            CF_COINS['default'],
            },
            'turrets': {
                'n_turrets':          int(5),
                'min_edge_offset_x':  int(140),
                'min_edge_offset_y':  int(140),
                'min_spacing_x':      int(200),  # spacing between other turrets
                'min_spacing_y':      int(150),  # spacing between other turrets
                'cf_turrets': [
                    # list of available turrets that the map can spawn
                    # map spawns one of each, in order, until/if n_turrets is reached, then picks a random one
                    CF_TURRETS['missile_launcher_x4'],
                    CF_TURRETS['missile_launcher_x4'],
                    CF_TURRETS['missile_launcher_x1'],
                    CF_TURRETS['missile_launcher_x2'],
                ],
            },
            'obstacle_blocks': {
                'n_obstacles':   int(16),
                # min/max distance inbetween generated obstacles
                'min_spacing_x': int(165),
                'min_spacing_y': int(160),
                'min_height':    int(10),
                'max_height':    int(30),
                'min_width':     int(8),
                'max_width':     int(80),
                'cf_block':      CF_BLOCKS['orange_mix'],
                'outline_blocks': {
                    'min_width':    int(8),
                    'max_width':    int(20),
                    'min_height':   int(7),
                    'max_height':   int(16),
                    'facing':       int(0),  # -1 is along inner axis, 0 is centered, 1 is outwards
                    'padding':      int(0),
                    'cf_block':     CF_BLOCKS['no_pallette'],
                }
            },
            'map_outline_blocks': {
                'facing':     int(-1),  # -1 is along inner axis, 0 is centered, 1 is outwards
                'min_width':  int(8),
                'max_width':  int(22),
                'min_height': int(10),
                'max_height': int(16),
                'padding':    int(1),  # space between each block
                'cf_block':   CF_BLOCKS['shades_of_gray']
            },
            'player': {
                # how close to an existing sprite the player can spawn
                # values are padded ON TOP OF players idle image bounding rect
                'min_terrain_offset_x': int(30),
                'min_terrain_offset_y': int(30)
            }
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
