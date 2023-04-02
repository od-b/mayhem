from .colors import RGB
from .cf_players import CF_PLAYERS
from .cf_blocks import CF_BLOCKS

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
        'player':               CF_PLAYERS['polygon'],
        'blocks': {
            'edge_outline':         CF_BLOCKS['small_gray_block'],
            'obstacle':             CF_BLOCKS['pastel_block'],
            'obstacle_outline':     CF_BLOCKS['adaptive_block'],
        },
        # time between sprite updates, per type. Values are millisecs between updates
        # these values will in reality typically have a variance of 0.5%
        'upd_interval': {
            'ui_core':  int(100),
            'ui_temp':   int(100),
            'terrain':   int(100),
        }
    }
}
