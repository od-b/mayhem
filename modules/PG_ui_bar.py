from typing import Callable

## import needed pygame modules
from pygame import Surface, Rect, Color, SRCALPHA, transform
from pygame.math import lerp, clamp
from pygame.sprite import Sprite, Group
from pygame.draw import rect as draw_rect
from pygame.draw import line as draw_line


class UI_Bar(Sprite):
    def __init__(self,
            cf_bar_style: dict,
            cf_global: dict,
            ref_id,
            position: tuple[int, int],
            size: tuple[int, int]
        ):
        Sprite.__init__(self)

        self.cf_bar_style = cf_bar_style
        self.cf_global = cf_global
        self.ref_id = ref_id
        self.position = position
        self.size = size

        self.bg_color               = Color(cf_bar_style['bg_color'])
        self.bg_alpha_key           = int(cf_bar_style['bg_alpha_key'])
        self.bg_border_color        = Color(cf_bar_style['bg_border_color'])
        self.bg_border_alpha_key    = int(cf_bar_style['bg_border_alpha_key'])
        self.bg_border_width        = int(cf_bar_style['bg_border_width'])

        self.bar_color              = Color(cf_bar_style['bar_color'])
        self.bar_alpha_key          = int(cf_bar_style['bar_alpha_key'])
        self.bar_border_color       = Color(cf_bar_style['bar_border_color'])
        self.bar_border_alpha_key   = int(cf_bar_style['bar_border_alpha_key'])
        self.bar_border_width       = int(cf_bar_style['bar_border_width'])

        self.internal_padding_x     = int(cf_bar_style['internal_padding_x'])
        self.internal_padding_y     = int(cf_bar_style['internal_padding_y'])

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
        
        self.fill_weight = 1.0

    def update(self):
        # self.fill_weight += 0.1
        # self.draw_horizontal_bar(self.fill_weight)
        pass

    def convert_color_alpha(self):
        ''' convert all colors to rgba '''
        self.bg_color = Color((self.bg_color.r, self.bg_color.g, self.bg_color.b, self.bg_alpha_key))
        self.bar_color = Color((self.bar_color.r, self.bar_color.g, self.bar_color.b, self.bar_alpha_key))
        self.bg_border_color = Color((self.bg_border_color.r, self.bg_border_color.g,
                                       self.bg_border_color.b, self.bar_border_alpha_key))
        self.bar_border_color = Color((self.bar_border_color.r, self.bar_border_color.g,
                                       self.bar_border_color.b, self.bar_border_alpha_key))

    def draw_horizontal_bar(self, fill_weight: float):
        # clear the background
        self.BG_SURF.fill(self.bg_color)

        if (fill_weight <= 0.0):
            # if there's no bar to draw, return (also avoids negative lerp)
            # if (fill_weight < 0.0):
            #     print(f'{self}[draw_horizontal_bar]: fill_weight={fill_weight} < 0.0. returning.')
            return
        elif (fill_weight > 1.0):
            # print(f'{self}[draw_horizontal_bar]: fill_weight={fill_weight} > 1.0. treating as 1.0.')
            fill_weight = 1.0

        # create the bar rect using a midpoint value through lerp. this is faster than python math.
        bar_width = lerp(0, self.bar_surf_rect.w, fill_weight)
        bar_rect = Rect(0, 0, bar_width, self.bar_surf_rect.h)

        self.BAR_SURF.fill(self.bar_color, bar_rect)

        if (self.bar_border_width):
            draw_rect(self.BAR_SURF, self.bar_border_color, bar_rect, width=self.bar_border_width)

    def draw_vertical_bar(self, fill_weight: float):
        ''' vertical bar fill. top to bottom '''
        # clear the background
        self.BG_SURF.fill(self.bg_color)

        if (fill_weight <= 0.0):
            # if there's no bar to draw, return (also avoids negative lerp)
            if (fill_weight < 0.0):
                print(f'{self}[draw_vertical_bar]: fill_weight={fill_weight} < 0.0. returning.')
            return
        elif (fill_weight > 1.0):
            print(f'{self}[draw_vertical_bar]: fill_weight={fill_weight} > 1.0. treating as 1.0.')
            fill_weight = 1.0


        # create the bar rect using a midpoint value through lerp. this is faster than python math.
        bar_height = lerp(0, self.bar_surf_rect.h, fill_weight)
        bar_rect = Rect(
            0, (self.bar_surf_rect.h - bar_height),
            self.bar_surf_rect.w, bar_height
        )

        self.BAR_SURF.fill(self.bar_color, bar_rect)

        if (self.bar_border_width):
            draw_rect(self.BAR_SURF, self.bar_border_color, bar_rect, width=self.bar_border_width)
    
    def update(self):
        pass

    def __str__(self):
        msg = f'[{super().__str__()} : '
        msg += f'rect="{self.rect}", ref_id={self.ref_id}]'
        return msg


class UI_Icon_Bar(UI_Bar):
    def __init__(self,
            cf_bar_style: dict,
            cf_global: dict,
            ref_id,
            position: tuple[int, int],
            size: tuple[int, int],
            icon_path: str
        ):
        super().__init__(cf_bar_style, cf_global, ref_id, position, size)
        
        self.icon_path = icon_path
        
    


class UI_Auto_Bar(UI_Bar):
    def __init__(self,
            cf_bar_style: dict,
            cf_global: dict,
            ref_id,
            position: tuple[int, int],
            size: tuple[int, int],
            min_val: float,
            max_val: float,
            getter_func: Callable[[None], float],
            fill_direction: str,
            auto_adjust_max_val: bool
        ):
        super().__init__(cf_bar_style, cf_global, ref_id, position, size)

        self.min_val = min_val
        self.max_val = max_val
        self.auto_adjust_max_val = auto_adjust_max_val

        self.getter_func = getter_func
        self.fill_direction = fill_direction

        if (fill_direction == 'horizontal'):
            self.bar_draw_func = super().draw_horizontal_bar
        elif (fill_direction == 'vertical'):
            self.bar_draw_func = super().draw_vertical_bar
        else:
            raise ValueError(f'"horizontal" or "vertical". Found "{fill_direction}"')

    def update(self):
        fill_val = self.getter_func()
        if (fill_val > self.min_val):
            if (fill_val > self.max_val):
                if (self.auto_adjust_max_val):
                    self.max_val = fill_val
                else:
                    fill_weight = 1.0
            else:
                fill_weight = (fill_val/self.max_val)
            self.bar_draw_func(
                lerp(
                    self.min_val,
                    self.max_val,
                    fill_weight
                )
            )
