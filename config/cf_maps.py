from os.path import join as os_path_join

from .colors import RGB
from .cf_players import CF_PLAYERS
from .cf_blocks import CF_BLOCKS
from .cf_maps_common import UPDATE_INTERVALS, CONTAINERS, BARS, CF_COIN


CF_MAPS = {
    # a map is a setup config for the active part of the game surface
    'map_1': {
        'name':                 str('Map 1'),
        'available_time':       int(0),     # time before map is failed, in milliseconds
        'fill_color':           RGB['offblack'],
        ## physics-related weights that may differ between maps
        # these are read by other sprites on creation.
        # gravitational constants. gravity_c must not be 0, or division by zero may occur.
        'gravity_m':            float(0.004),      # gravity multiplier. range = [1.0, 2.0]
        'gravity_c':            float(0.003),      # gravitational constant. 0 = no gravity
        # misc difficulty related settings:
        'n_obstacles':          int(13),
        'n_coins':              int(20),
        'min_coin_offset':     int(6),      # min. offset to terrain
        'min_coin_spread':     int(0),    # min. distance to another coin
        # sprite settings:
        'upd_intervals': UPDATE_INTERVALS,
        'game_sprites': {
            'player': CF_PLAYERS['polygon'],
            'blocks': {
                'edge_outline':         CF_BLOCKS['small_gray_block'],
                'obstacle':             CF_BLOCKS['pastel_block'],
                'obstacle_outline':     CF_BLOCKS['adaptive_block'],
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
