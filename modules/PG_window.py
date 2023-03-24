from pygame import display, Color, Rect
from random import randint

# class PG_Map:
    

class PG_Window:
    ''' wrapper for the main app surfaces

        Parameters
        ---
        config: dict with expected keys
            see CONFIG['window']

        map_config: dict with expected keys
            see CONFIG['map']
    '''

    def __init__(self, config, map_config):
        # set up window surface
        self.fill_color = Color(config['fill_color'])
        self.width = int(config['width'])
        self.height = int(config['height'])
        self.surface = display.set_mode((self.width, self.height), vsync=config['vsync'])
        self.fill_surface()

        # set up map surface
        self.map_fill_color = Color(map_config['fill_color'])
        self.map_bounds: dict[str, int] = {
            'min_x': int(map_config['padded_bounds']['min_x']),
            'max_x': int(self.width - map_config['padded_bounds']['max_x']),
            'min_y': int(map_config['padded_bounds']['min_y']),
            'max_y': int(self.height - map_config['padded_bounds']['max_y']),
        }
        ''' Dict containing the surface area used by active game area. '''

        map_rect = Rect(
            int(self.map_bounds['min_x']),
            int(self.map_bounds['min_y']),
            int((self.map_bounds['max_x'] - self.map_bounds['min_x'])),
            int((self.map_bounds['max_y'] - self.map_bounds['min_y']))
        )

        self.map_surface = self.surface.subsurface(map_rect)
        ''' subsurface from map_bounds_rect, containing the map surface area '''

        self.map_rect = self.map_surface.get_rect()
        ''' rect of the map surface '''

        self.set_caption(config['caption'])

    def set_caption(self, text):
        ''' sets the window caption '''
        display.set_caption(text)

    def get_bounds(self):
        return self.map_bounds

    def pixel_is_inbound(self, x: int, y: int):
        ''' boolean inbound check '''
        if ((x < self.map_bounds['min_x']) or
            (x > self.map_bounds['max_x']) or
            (y < self.map_bounds['min_y']) or 
            (y > self.map_bounds['max_y'])):
            return False
        return True

    def get_rand_x_inbound(self, width_adj: int):
        return randint(self.map_bounds['min_x'], self.map_bounds['max_x'] - width_adj)

    def get_rand_y_inbound(self, height_adj: int):
        return randint(self.map_bounds['min_y'], self.map_bounds['max_y'] - height_adj)

    def fill_surface_alt_color(self, color: Color | None):
        ''' uses self.fill_color if color is None '''
        if color:
            self.surface.fill(color)
        else:
            self.fill_surface()
    
    def fill_surface(self):
        self.surface.fill(self.fill_color)

    def fill_map_surface(self):
        self.map_surface.fill(self.map_fill_color)

    def __str__(self):
        msg = f'< PG_Window: width={self.width}, height={self.height},\n  map_bounds='+'{'
        for key, val in self.map_bounds.items():
            msg += f'\n\t"{key}": {val}'
        msg += '\n  }\n>'
        return msg
