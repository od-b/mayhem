import pygame as pg
from .exceptions import LogicError

''' abstract root classes for pygame, typically extendeded '''

class PG_Rect:
    ''' wrapper for pygame rects '''
    def __init__(self, window, x: int, y: int, w: int, h: int, border_width: int,
                 bg_color: None | pg.Color, border_color: None | pg.Color):

        if (border_width < 0):
            raise LogicError('border width must be >=0')

        if (border_width > 0) and (not border_color):
            # use bg color as border color if width is set and not color
            border_color = bg_color

        self.window = window
        self.bg_color: pg.Color | None = bg_color
        self.border_width = border_width
        self.border_color: pg.Color | None = border_color

        self.border: pg.Rect | None = None
        # use window bounds as default bounds:
        self.bounds: dict[str, int] = window.get_bounds()
        self.re = pg.Rect(int(x), int(y), int(w), int(h))

        if (border_width > 0):
            self.replace_border_rect()
    
    def replace_border_rect(self):
        ''' create a border for the current rect. Store in self.border '''

        WIDTH_X_2 = int(2 * self.border_width)
        self.border = pg.Rect(
            self.re.x - self.border_width,
            self.re.y - self.border_width,
            self.re.w + WIDTH_X_2,
            self.re.h + WIDTH_X_2,
        )

    def adjust_rect_padding(self, rect: pg.Rect, x: int, y: int):
        ''' returns a rect with padding added to the size '''
        return rect.inflate(x, y)

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

    def set_bg_color(self, color: None | pg.Color):
        self.bg_color = color

    def set_border_color(self, color: None | pg.Color):
        self.border_color = color

    def set_border_width(self, width: int):
        self.border_width = width

    def set_border(self, width: int, color: pg.Color):
        ''' replaces the border settings. '''

        if (width <= 0):
            raise ValueError(f'(width={width}), must be > 0.\
                To remove, call .remove_border() instead')

        self.set_border_color(color)
        self.set_border_width(width)
        self.replace_border_rect()

    def remove_border(self):
        ''' removes the border (and its color) '''
        self.set_border_width(0)
        self.set_border_color(None)
        self.border = None

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
        self.re.y = parent.re.y

    def align_to_right_of(self, parent: pg.Rect, offset: int):
        self.re.left = parent.re.right + offset
        self.re.y = parent.re.y

    def align_to_top_of(self, parent: pg.Rect, offset: int):
        self.re.bottom = parent.re.top - offset
        self.re.x = parent.re.x

    def align_to_bottom_of(self, parent: pg.Rect, offset: int):
        self.re.top = parent.re.bottom + offset
        self.re.x = parent.re.x

    def draw_background_alt(self, color: pg.Color):
        ''' draw background of the rect with the given color '''
        pg.draw.rect(self.window.surface, color, self.re)

    def draw_border_alt(self, color: pg.Color):
        ''' draw border of rect the with the given color '''
        pg.draw.rect(self.window.surface, color, self.border)

    def draw_background(self):
        ''' draw background of the rect with the default color '''
        pg.draw.rect(self.window.surface, self.bg_color, self.re)

    def draw_border(self):
        ''' draw border of rect the with the default color '''
        pg.draw.rect(self.window.surface, self.border_color, self.border)

