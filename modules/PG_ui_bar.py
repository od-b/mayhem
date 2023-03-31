from typing import Callable

## import needed pygame modules
from pygame import Surface, Rect, Color, SRCALPHA
from pygame.math import lerp
from pygame.sprite import Sprite, Group
from pygame.draw import rect as draw_rect
from pygame.draw import line as draw_line
from .PG_ui_text_box import Text_Box

class UI_Bar(Sprite):
    def __init__(self,
            cf_bar_style: dict,
            position: tuple[int, int],
            size: tuple[int, int] 
        ):
        Sprite.__init__(self)

        self.FULL_ALPHA = Color(0,0,0,0)
        self.cf_bar_style = cf_bar_style
        self.position = position
        self.size = size
        self.width = size[0]
        self.height = size[1]

        self.bg_alpha_key       = int(cf_bar_style['bg_alpha_key'])
        self.bg_color           = Color(cf_bar_style['bg_color'])
        self.bg_border_color    = Color(cf_bar_style['bg_border_color'])
        self.bg_border_width    = int(cf_bar_style['bg_border_width'])

        self.bar_alpha_key      = int(cf_bar_style['bar_alpha_key'])
        self.bar_color          = Color(cf_bar_style['bar_color'])
        self.bar_border_color   = Color(cf_bar_style['bar_border_color'])
        self.bar_border_width   = int(cf_bar_style['bar_border_width'])

        self.internal_padding_x = int(cf_bar_style['internal_padding_x'])
        self.internal_padding_y = int(cf_bar_style['internal_padding_y'])

        self.convert_color_alpha()

        # create a root surface 
        SURF = Surface(self.size, flags=SRCALPHA)
        # draw border onto the root surface
        if (self.bg_border_width):
            draw_rect(SURF, self.bg_border_color, SURF.get_rect(), width=self.bg_border_width)

        self.ROOT_SURF = SURF
        self.ROOT_RECT = SURF.get_rect()

        # create background area as a rect
        self.bg_surf_rect = Rect(
            (self.ROOT_RECT.x + self.bg_border_width),
            (self.ROOT_RECT.y + self.bg_border_width),
            (self.ROOT_RECT.w - (2 * self.bg_border_width)),
            (self.ROOT_RECT.h - (2 * self.bg_border_width))
        )

        # create bar area as a rect
        self.bar_surf_rect = Rect(
            (self.bg_surf_rect.x + self.internal_padding_x),
            (self.bg_surf_rect.y + self.internal_padding_y),
            (self.bg_surf_rect.w - (2 * self.internal_padding_x)),
            (self.bg_surf_rect.h - (2 * self.internal_padding_y))
        )

        # assign areas of the root surface to the different parts
        self.BG_SURF = self.ROOT_SURF.subsurface(self.bg_surf_rect)
        self.BAR_SURF = self.ROOT_SURF.subsurface(self.bar_surf_rect)

        # set image to the root surface
        self.image = self.ROOT_SURF
        self.rect = self.ROOT_RECT
        self.rect.topleft = position

    def update(self):
        pass

    def convert_color_alpha(self):
        # convert colors to rgba
        if (self.bg_alpha_key < 255):
            self.bg_color = Color((self.bg_color.r, self.bg_color.g, self.bg_color.b, self.bg_alpha_key))
        if (self.bar_alpha_key < 255):
            self.bar_color = Color((self.bar_color.r, self.bar_color.g, self.bar_color.b, self.bar_alpha_key))

    def draw_horizontal_bar(self, fill_weight: float):
        # clear the background
        self.BG_SURF.fill(self.bg_color)

        if (fill_weight <= 0):
            # if there's no bar to draw, return (also avoids negative lerp)
            return

        # create the bar rect using a midpoint value through lerp. this is faster than python math.
        bar_rect = Rect(0, 0, lerp(0, self.bar_surf_rect.w, fill_weight), self.bar_surf_rect.h)

        self.BAR_SURF.fill(self.bar_color, bar_rect)

        if (self.bar_border_width):
            draw_rect(self.BAR_SURF, self.bar_border_color, bar_rect, width=self.bar_border_width)

    def draw_vertical_bar(self, fill_weight: float):
        pass
    
    def update(self):
        pass


# class UI_Bar_Timed_Horizontal(Sprite):
#     def __init__(self,
#             cf_duration_bar: dict,
#             ref_id,
#             position: tuple,
#         ):
#         self.
