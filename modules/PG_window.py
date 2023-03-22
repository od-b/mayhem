from pygame import display, Color
from modules.PG_shapes import PG_Rect
from random import randint

class PG_Window:
    ''' wrapper for the pygame window, containing the surface
        * the surface bounds determine the effective game area
        * bounds_padding is a dict controlling the padding of each bound 
          (e.g. 'min_x': 50 will create game bounds 50 pixels from the left edge)
    '''
    def __init__(self, caption: str, width: int, height: int, bounds_padding: dict,
                 fill_color: Color, bounds_fill_color: Color, use_vsync: bool,):

        self.fill_color = Color(fill_color)
        self.bounds_fill_color = Color(bounds_fill_color)
        self.bounds_padding = bounds_padding
        self.width = width
        self.height = height

        self.surface = display.set_mode((self.width, self.height), vsync=use_vsync)
        self.bounds: dict[str, int] = {
            'min_x': int(self.bounds_padding['min_x']),
            'max_x': int(self.width - self.bounds_padding['max_x']),
            'min_y': int(self.bounds_padding['min_y']),
            'max_y': int(self.height - self.bounds_padding['max_y']),
        }
        ''' Dict containing the surface area used by active game area\n
            Allows for separation of UI, etc.\n
            Keys: 
            * 'min_x'
            * 'max_x'
            * 'min_y'
            * 'max_y'
        '''
        self.bounds_rect = PG_Rect(
            self,
            self.bounds['min_x'],
            self.bounds['min_y'],
            (self.bounds['max_x'] - self.bounds['min_x']),
            (self.bounds['max_y'] - self.bounds['min_y']),
            0, self.bounds_fill_color, None
        )
        
        self.set_caption(caption)

    def set_caption(self, text):
        ''' sets the window caption '''
        display.set_caption(text)
    
    def get_bounds(self):
        return self.bounds

    def get_bounds_rect(self):
        ''' returns a copy of the bounds as a pygame rect '''
        return self.bounds_rect.copy()

    def pixel_is_inbound(self, x: int, y: int):
        ''' boolean inbound check '''
        if ((x < self.bounds['min_x']) or
            (x > self.bounds['max_x']) or
            (y < self.bounds['min_y']) or 
            (y > self.bounds['max_y'])):
            return False
        return True

    def get_rand_x_inbound(self, width_adj: int):
        return randint(self.bounds['min_x'], self.bounds['max_x'] - width_adj)

    def get_rand_y_inbound(self, height_adj: int):
        return randint(self.bounds['min_y'], self.bounds['max_y'] - height_adj)

    def fill_surface_alt_color(self, color: Color | None):
        ''' uses self.fill_color if color is None '''
        if color:
            self.surface.fill(color)
        else:
            self.fill_surface()
    
    def fill_surface(self):
        self.surface.fill(self.fill_color)

    def __str__(self):
        msg = f'< PG_Window: width={self.width}, height={self.height},\n  bounds='+'{'
        for key, val in self.bounds.items():
            msg += f'\n\t"{key}": {val}'
        msg += '\n  }\n>'
        return msg
