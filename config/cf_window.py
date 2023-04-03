from .colors import RGB

CF_WINDOW = {
    'caption':      str('< app >'),
    'height':       int(840),
    'width':        int(1400),
    'fill_color':   RGB['gray_100'],
    'vsync':        int(0), # bool, 0/1
    'fullscreen':   False,  # warning -> it works, but not great
    # map_bounds:
    #   size of the surface dedicated to the map
    #   defined using positive padding values with reference to the width/height set above
    'map_bounds': {
        'min_x': int(6),
        'max_x': int(6),
        'min_y': int(6),
        'max_y': int(6),
    },
}
