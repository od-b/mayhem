import pygame as pg

''' abstract root classes for pygame, typically extendeded '''

class PG_Rect:
    ''' wrapper for pygame rects '''
    def __init__(self, window, x: int, y: int, w: int, h: int, border_width: int,
                 bg_color: None | tuple, border_color: None | tuple):
        
        if (border_width > 0) and (not border_color):
            raise ValueError('border needs a color when set')
            # however, border color without width is allowed
            # means the width can be adjusted later to display,
            # without considering color
        if (border_width < 0):
            raise ValueError('border width must be >=0')

        self.window = window
        self.border_width: int = border_width
        self.border_color: None | tuple = border_color
        self.bg_color: None | tuple = bg_color
        self.border: pg.Rect | None = None
        self.bounds: dict[str, int] = window.get_bounds()
        self.re = pg.Rect(int(x), int(y), int(w), int(h))

        if (border_width > 0):
            self.create_border()
    
    def set_bounds(self, min_x: int, max_x: int, min_y: int, max_y: int):
        ''' for setting bounds to something other than the window surface '''
        self.bounds = {
            'min_x': min_x,
            'max_x': max_x,
            'min_y': min_y,
            'max_y': max_y,
        }

    def is_inbound(self):
        ''' boolean inbound check '''
        if ((self.re.x < self.bounds['min_x']) or
            ((self.re.x + self.re.w) > self.bounds['max_x']) or
            (self.re.y < self.bounds['min_y']) or 
            ((self.re.y + self.re.h) > self.bounds['max_y'])):
            return False
        return True
    
    def x_out_of_bounds(self):
        ''' returns 0 if inbound, otherwise returns how much out of x-bound (left:- / right:+)'''
        if (self.re.x < self.bounds['min_x']):
            # out of bounds on the left (-)
            return int(self.bounds['min_x'] - self.re.x)

        if ((self.re.x + self.re.w) > self.bounds['max_x']):
            # out of bounds on the right (+)
            return int((self.re.x + self.re.w) - self.bounds['max_x'])

        return 0

    def y_out_of_bounds(self):
        ''' returns 0 if inbound, otherwise returns how much out of y-bound (top:+ / bottom:-)'''
        if (self.re.y < self.bounds['min_y']):
            # out of bounds on the top (-)
            return int(self.bounds['min_y'] - self.re.y)

        if ((self.re.y + self.re.h) > self.bounds['max_y']):
            # out of bounds on the bottom (+)
            return int((self.re.y + self.re.h) - self.bounds['max_y'])

        return 0

    def set_x(self, x: int):
        ''' set top left x pos '''
        self.re.x = x

    def set_y(self, y: int):
        ''' set top left y pos '''
        self.re.y = y

    def set_bg_color(self, color: None | tuple):
        self.bg_color = color

    def set_border_color(self, color: None | tuple):
        self.border_color = color

    def align_to_bounds_center_x(self, offset: int):
        ''' sets centerx relative to bounds center '''
        BOUND_CENTER_X = int((self.bounds['max_x'] - self.bounds['min_x']) / 2)
        self.re.centerx = BOUND_CENTER_X + offset

    def align_to_bounds_center_y(self, offset: int):
        ''' sets centery relative to bounds center '''
        BOUND_CENTER_Y = int((self.bounds['max_y'] - self.bounds['min_y']) / 2)
        self.re.centery = BOUND_CENTER_Y + offset

    def align_to_center_x_of(self, parent: pg.Rect, offset: int):
        self.re.centerx = parent.centerx + offset

    def align_to_center_y_of(self, parent: pg.Rect, offset: int):
        self.re.centery = parent.centery + offset

    def align_to_left_of(self, parent: pg.Rect, offset: int):
        self.re.right = parent.re.left - offset
        self.set_y(parent.re.y)

    def align_to_right_of(self, parent: pg.Rect, offset: int):
        self.re.left = parent.re.right + offset
        self.set_y(parent.re.y)

    def align_to_top_of(self, parent: pg.Rect, offset: int):
        self.re.bottom = parent.re.top - offset
        self.set_x(parent.re.x)

    def align_to_bottom_of(self, parent: pg.Rect, offset: int):
        self.re.top = parent.re.bottom + offset
        self.set_x(parent.re.x)

    def create_border(self):
        ''' create a border for the current rect '''
        WIDTH_X_2 = int(2 * self.border_width)

        self.border = pg.Rect(
            self.re.x - self.border_width,
            self.re.y - self.border_width,
            self.re.w + WIDTH_X_2,
            self.re.h + WIDTH_X_2,
        )

    def draw_border(self):
        pg.draw.rect(self.window.surface, self.border_color, self.border)

    def draw(self):
        pg.draw.rect(self.window.surface, self.bg_color, self.re)
