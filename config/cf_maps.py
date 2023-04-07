from os.path import join as os_path_join

from .colors import RGB
from .cf_players import CF_PLAYERS
from .cf_blocks import CF_BLOCKS
from .cf_maps_common import UPDATE_INTERVALS, CONTAINERS, BARS, CF_COIN


CF_MAPS = {
    # a map is a setup config for the active part of the game surface
    'map_1': {
        'name':            str('Map 1'),
        'fill_color':      RGB['offblack'],
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
        'upd_intervals': UPDATE_INTERVALS,
        'game_sprites': {
            'player': CF_PLAYERS['polygon'],
            'blocks': {
                'edge_outline':     CF_BLOCKS['small_gray_block'],
                'obstacle':         CF_BLOCKS['pastel_block'],
                'obstacle_outline': CF_BLOCKS['adaptive_block'],
            },
            'coin': CF_COIN
        },
        'ui_sprites': {
            'containers': CONTAINERS,
            'bars': BARS
        }
        # time between sprite updates, per type. Values are millisecs between updates
        # these values will typically have an applied variance of 0.5%
    }
}
