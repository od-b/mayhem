from .colors import RGB

# adjust the size of the entire display window
window_width  = int(1400)
window_height = int(840)

# map_surf_offset refers to where to place the map surface within the window w and h
map_surf_offset = {
    'left':   int(6),
    'right':  int(6),
    'top':    int(6),
    'bottom': int(6)
}

# map size is calculated at config level to allow other configs to read them pre window-creation
# there's no reason to change the dict below directly. set dimensions through map surface offset
MAP_RECT_INFO = {
    'x': map_surf_offset['left'],
    'y': map_surf_offset['top'],
    'w': int(window_width - map_surf_offset['left'] - map_surf_offset['right']),
    'h': int(window_height - map_surf_offset['top'] - map_surf_offset['bottom']),
}

# some definitions to make it easy to position other configs dynamically
WINDOW_CENTER = (int(window_width / 2), int(window_height / 2))
MAP_TOPLEFT_POS = (map_surf_offset['left'], map_surf_offset['top'])
MAP_TOPRIGHT_POS = ((map_surf_offset['left'] + MAP_RECT_INFO['w']), (map_surf_offset['top']))
MAP_BOTTOMLEFT_POS = (map_surf_offset['left'], (map_surf_offset['top'] + MAP_RECT_INFO['h']))
MAP_BOTTOMRIGHT_POS = ((map_surf_offset['left'] + MAP_RECT_INFO['w']), (map_surf_offset['top'] + MAP_RECT_INFO['h']))
MAP_MIDTOP_POS = ((map_surf_offset['left'] + int(MAP_RECT_INFO['w'] / 2)), map_surf_offset['top'])
MAP_MIDBOTTOM_POS = ((map_surf_offset['left'] + int(MAP_RECT_INFO['w'] / 2)), (map_surf_offset['top'] + MAP_RECT_INFO['h']))

# configure misc window settings
CF_WINDOW = {
    'caption':    str('< app >'),
    'fill_color': RGB['gray_100'],
    'vsync':      int(0), # bool, 0/1
    'fullscreen': False,  # warning: it works, but not great. big fps losses, also
    'width':      window_width,
    'height':     window_height,
    'map_rect_info': MAP_RECT_INFO
}
