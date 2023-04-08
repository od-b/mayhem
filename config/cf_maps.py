from .colors import RGB
from .map_sprites import CF_PLAYERS, CF_BLOCKS, CF_COINS
from .map_common import MAP_UPDATE_INTERVALS, MAP_CONTAINERS, MAP_BARS


CF_MAPS = {
    # a map is a setup config for the active part of the game surface
    'map_1': {
        'name':            str('Map 1'),
        'fill_color':      RGB['offblack'],
        'overlap_color': RGB['signal_red'],  # used for visualizing overlapping masks / misc
        # gravitational constants. gravity_w must not be 0.
        # gravity_w stops being applied when terminal velocity is reached. gravity_c is always added.
        'gravity_c':       float(0.003),      # every frame gravitational incrementor
        'gravity_w':       float(0.004),      # gravity weight (percent multiplier), calced after curr_grav+constant
        # misc difficulty related settings:
        'player_fuel_consumption': float(0.02),
        'n_obstacles':     int(13),
        'n_coins':         int(20),
        'min_coin_offset': int(11),      # min. offset to terrain
        'min_coin_spread': int(120),    # min. distance to another coin
        # nested configs; sets the config dicts of "children". can be shared or unique
        'game_sprites': {
            'player': CF_PLAYERS['polygon'],
            'blocks': {
                'edge_outline':     CF_BLOCKS['small_gray_block'],
                'obstacle':         CF_BLOCKS['pastel_block'],
                'obstacle_outline': CF_BLOCKS['adaptive_block'],
            },
            'coin': CF_COINS['default']
        },
        'ui_sprites': {
            'containers': MAP_CONTAINERS,
            'bars': MAP_BARS
        },
        'upd_intervals': MAP_UPDATE_INTERVALS,
        # time between sprite updates, per type. Values are millisecs between updates
        # these values will typically have an applied variance of 0.5%
    }
}
