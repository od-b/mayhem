from pygame import display
from modules.PG_shapes import PG_Rect
from random import randint

class PG_Window:
    ''' wrapper for the pygame window, containing the surface
        the surface bounds determine the effective game area
    '''
    def __init__(self, caption: str, w: int, h: int, bounds_padding: dict, fill_color, bounds_fill_color):
        self.fill_color = fill_color
        self.bounds_fill_color = bounds_fill_color
        self.bounds_padding = bounds_padding
        
        self.width = w
        self.height = h
        self.surface = display.set_mode((self.width, self.height))
        self.bounds: dict[str, int] = {
            'min_x': int(self.bounds_padding['min_x']),
            'max_x': int(self.width - self.bounds_padding['max_x']),
            'min_y': int(self.bounds_padding['min_y']),
            'max_y': int(self.height - self.bounds_padding['max_y']),
        }
        ''' bounds contain the surface area used by active game area\n
            Allows for separation of UI, etc.\n
            Keys: 
            * 'min_x'
            * 'max_x'
            * 'min_y'
            * 'max_y'
        '''
        bounds_width = (self.bounds['max_x'] - self.bounds['min_x'])
        bounds_height = (self.bounds['max_y'] - self.bounds['min_y'])
        self.bounds_rect = PG_Rect(
            self,
            self.bounds['min_x'],
            self.bounds['min_y'],
            bounds_width,
            bounds_height,
            0, self.bounds_fill_color, None
        )
        self.set_caption(caption)

    def set_caption(self, text):
        ''' sets the window caption '''
        display.set_caption(text)
    
    def get_bounds(self):
        return self.bounds

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

    def fill_surface(self, alt_color: tuple | None):
        ''' uses self.fill_color if alt color is set to None '''
        if alt_color:
            self.surface.fill(alt_color)
        else:
            self.surface.fill(self.fill_color)

    def __str__(self):
        msg = f'< PG_Window: width={self.width}, height={self.height},\n  bounds='+'{'
        for key, val in self.bounds.items():
            msg += f'\n\t"{key}": {val}'
        msg += '\n  }\n>'
        return msg
