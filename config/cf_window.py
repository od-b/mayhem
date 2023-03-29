from .colors import RGB

CF_WINDOW = {
    'caption':      str('< app >'),
    'height':       int(840),
    'width':        int(1400),
    'fill_color':   RGB['gray_100'],
    'vsync':        int(0), # bool, 0/1
    # map_bounds:
    #   size of the surface dedicated to the map
    #   defined using positive padding values with reference to the width/height set above
    #   e.g. all valyes set to 0 will create a map as large as the entire window surface
    #   (this will not leave any room for the UI, which currently requires 'max_y'-padding >= 40)
    'map_bounds': {
        'min_x': int(20),
        'max_x': int(20),
        'min_y': int(20),
        'max_y': int(60),
    },
}
