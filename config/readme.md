''' 
    config dict containing various constants and parameter weights.
    * type conversions within the config is mainly a guideline of the expected type value
    * colors and pallettes within the config refer to a different dict @ ./colors.py
    
    any deletion and/or modification within the dict could completely break the program.
    However, adding additional dict entries will never break anything, as the program only
    accesses the configs internal dicts or values directly, never iteratively
    
    key values that are in caps symbolise a generalized entry pattern.
    For example, all subdictionaries within CONFIG['environment']['BLOCK']
    should follow the pattern of:
    
    '<block_type>': {
        'texture': <pg.Surface>,
        'color_pool': <list: containing minimum one RGB color tuple>,
        'min_height': <int>,
        'max_height': <int>,
        'min_width': <int>,
        'max_width': <int>,
        'padding': <int>,
    },

    This design allows functions to be generalized, reused and modified without
    core changes to the internal algorithm.
    
    For example, if one wants to add a new type of block and use
    spawn_axis_outline to spawn it on the perimeter of a rect, simply add a block type within
    CONFIG['environment']['BLOCK'] following the above specifications, and pass the config reference
    to the function. 
    
    Note: ['special_sprites']['UNIQUE_CONTROLLABLE'] share required entries, but differ from say BLOCKS, 
    in the way that two entries must not share keyboard controls or initial position.
'''
