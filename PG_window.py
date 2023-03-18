from pygame import display
from random import randint

class PG_Window:
    ''' wrapper for the pygame window, containing the surface
        * offset>0 creates a buffer for detecting if mouse is off the surface
        ** i.e., offset=1 will create a surface 1 pixel larger than the effective bounds
    '''
    def __init__(self, caption: str, w: int, h: int, offset_x: int, offset_y: int, fill_color):
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.fill_color = fill_color
        
        self.width = w + (2 * offset_x)
        self.height = h + (2 * offset_y)
        self.surface = display.set_mode((self.width, self.height))
        self.bounds: dict[str, int] = {
            'min_x': int(self.offset_x),
            'max_x': int(self.width - self.offset_x),
            'min_y': int(self.offset_y),
            'max_y': int(self.height - self.offset_y),
        }
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

    def get_rand_x(self, adjustment: int):
        return randint(adjustment, self.width - adjustment)
        
    def get_rand_y(self, adjustment: int):
        return randint(adjustment, self.height - adjustment)

    def fill(self):
        ''' fills the surface with a set color '''
        self.surface.fill(self.fill_color)
    
    def update(self):
        ''' refreshes display surface '''
        display.update()

    def __str__(self):
        msg = f'[PG_Window]:\nwidth={self.width}, height={self.height}\nbounds = '+'{'
        for key, val in self.bounds.items():
            msg += f'\n\t"{key}": {val}'
        msg += '\n}\n'
        return msg
