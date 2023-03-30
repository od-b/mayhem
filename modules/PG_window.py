
## simplify some imports for readability:
from pygame import display, Color, Rect, FULLSCREEN


class PG_Window:
    ''' wrapper for the main app surfaces / subsurfaces

    Noteworthy Attributes
    ---
    surface: 
        the entire window surface
    map_surface: 
        subsurface designated to the active game area
    map_Rect: 
        Rect of the subsurface
    map_surface_position:
        map surface topleft, relative to the main surface
    '''

    def __init__(self, cf_global: dict, cf_window: dict):
        # set up window surface
        self.cf_global = cf_global
        self.cf_window = cf_window

        self.fill_color = Color(cf_window['fill_color'])
        self._vsync = int(cf_window['vsync'])
        self.fullscreen: bool = cf_window['fullscreen']
        self.width = int(cf_window['width'])
        self.height = int(cf_window['height'])
        self.caption = str(cf_window['caption'])

        if (self.fullscreen):
            self.surface = display.set_mode((self.width, self.height), vsync=self._vsync, flags=FULLSCREEN)
        else:
            self.surface = display.set_mode((self.width, self.height), vsync=self._vsync)

        self.fill_surface()
        self.set_extended_caption(None)

        ''' set up the map area of the surface '''

        self.map_width = int(self.width - cf_window['map_bounds']['max_x'] - cf_window['map_bounds']['min_x'])
        self.map_height = int(self.height - cf_window['map_bounds']['max_y'] - cf_window['map_bounds']['min_y'])
        self.map_pos_x = int(cf_window['map_bounds']['min_x'])
        self.map_pos_y = int(cf_window['map_bounds']['min_y'])

        self.map_surface_position = (self.map_pos_x, self.map_pos_y)
        ''' map subsurface topleft[x,y] position, relative to the main surface '''

        self.map_size = (self.map_width, self.map_height)
        ''' map size[w,h] '''

        self.map_rect = Rect((self.map_surface_position), (self.map_size))
        ''' rect describing the to-be-created map subsurface '''
        
        self.map_surface = self.surface.subsurface(self.map_rect)
        ''' subsurface of the main surface dedicated to the map area '''

    def set_extended_caption(self, extension: str | None):
        ''' append a text to the window caption
            * set text to none to only use caption
        '''
        if (extension):
            display.set_caption(f'{self.caption}: {extension}')
        else:
            display.set_caption(self.caption)

    def fill_surface_alt_color(self, color: Color | None):
        ''' uses self.fill_color if color is None '''
        if color:
            self.surface.fill(color)
        else:
            self.fill_surface()
    
    def fill_surface(self):
        self.surface.fill(self.fill_color)

    def __str__(self):
        msg = f'< PG_Window: width={self.width}, height={self.height}'
        if (self._vsync == 0):
            msg += f'vsync = True'
        else:
            msg += f'vsync = False'
        return msg

