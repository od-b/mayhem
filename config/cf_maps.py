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
        'gravity_m':            float(1.005),      # gravity multiplier. range = [1.0, 2.0]
        'gravity_c':            float(0.007),     # added to the velocity.y or position of sprites every frame
        # sprite settings:
        'player':               CF_PLAYERS['polygon'],
        'blocks': {
            'edge_outline':         CF_BLOCKS['small_gray_block'],
            'obstacle':             CF_BLOCKS['pastel_block'],
            'obstacle_outline':     CF_BLOCKS['adaptive_block'],
        }
    }
}
