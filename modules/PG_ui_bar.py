from typing import Callable

## import needed pygame modules
from pygame import Surface, Rect, Color, transform, image
from pygame.math import lerp
from pygame.sprite import Sprite
from pygame.draw import rect as draw_rect


class UI_Bar(Sprite):
    def __init__(self,
            cf_bar: dict,
            cf_global: dict,
            ref_id,
            position: tuple[int, int],
            size: tuple[int, int]
        ):
        Sprite.__init__(self)

        self.cf_bar = cf_bar
        self.cf_global = cf_global
        self.ref_id = ref_id
        self.position = position
        self.size = size

        self.bg_color               = Color(cf_bar['bg']['color'])
        self.bg_alpha_key           = int(cf_bar['bg']['alpha'])
        self.bg_border_color        = Color(cf_bar['bg']['border_color'])
        self.bg_border_width        = int(cf_bar['bg']['border_width'])
        self.bg_border_alpha_key    = int(cf_bar['bg']['border_alpha'])

        self.bar_color              = Color(cf_bar['bar']['color'])
        self.bar_alpha_key          = int(cf_bar['bar']['alpha'])
        self.bar_border_color       = Color(cf_bar['bar']['border_color'])
        self.bar_border_width       = int(cf_bar['bar']['border_width'])
        self.bar_border_alpha_key   = int(cf_bar['bar']['border_alpha'])

        self.internal_padding_x     = int(cf_bar['internal_padding_x'])
        self.internal_padding_y     = int(cf_bar['internal_padding_y'])

        self.convert_color_alpha()

        # create a root surface 
        self.ROOT_SURF = Surface(self.size).convert_alpha()
        self.ROOT_RECT = self.ROOT_SURF.get_rect()
        # self.ROOT_SURF.fill((0, 0, 0, 0))

        # bg image with border drawn on it, can be blitted to the surface to clear it
        # if this is alpha, root surf needs to be filled with alpha as well
        self.BG_IMAGE = Surface(self.size).convert_alpha()
        # self.BG_IMAGE.fill((0, 0, 0, 0))
        self.BG_IMAGE.fill(self.bg_color)
        if (self.bg_border_width):
            draw_rect(self.BG_IMAGE, self.bg_border_color, self.ROOT_RECT, width=self.bg_border_width)

        # create bar area as a rect
        bar_surf_rect = Rect(
            (self.ROOT_RECT.x + self.internal_padding_x + self.bg_border_width),
            (self.ROOT_RECT.y + self.internal_padding_y + self.bg_border_width),
            (self.ROOT_RECT.w - (2 * (self.internal_padding_x + self.bg_border_width))),
            (self.ROOT_RECT.h - (2 * (self.internal_padding_y + self.bg_border_width)))
        )

        # assign areas of the root surface to the different parts for easy blitting
        self.BG_SURF = self.ROOT_SURF.subsurface(self.ROOT_RECT)
        self.BAR_SURF = self.ROOT_SURF.subsurface(bar_surf_rect)

        self.BG_SURF_RECT = self.BG_SURF.get_rect()
        self.BAR_SURF_RECT = self.BAR_SURF.get_rect()

        # set image to the root surface
        self.image = self.ROOT_SURF
        self.rect = self.ROOT_RECT
        self.rect.topleft = position
        
        if (self.bg_alpha_key != 255):
            self.FILL_WITH_ALPHA = True
        else:
            self.FILL_WITH_ALPHA = False
        
        self.FULL_ALPHA = Color(0,0,0,0)

    def convert_color_alpha(self):
        ''' convert all colors to rgba '''
        self.bg_color = Color((self.bg_color.r, self.bg_color.g, self.bg_color.b, self.bg_alpha_key))
        self.bar_color = Color((self.bar_color.r, self.bar_color.g, self.bar_color.b, self.bar_alpha_key))
        self.bg_border_color = Color((self.bg_border_color.r, self.bg_border_color.g,
                                       self.bg_border_color.b, self.bg_border_alpha_key))
        self.bar_border_color = Color((self.bar_border_color.r, self.bar_border_color.g,
                                       self.bar_border_color.b, self.bar_border_alpha_key))

    def draw_horizontal_bar(self, fill_weight: float):
        # clear the background
        if (self.FILL_WITH_ALPHA):
            self.ROOT_SURF.fill(self.FULL_ALPHA)
        self.BG_SURF.blit(self.BG_IMAGE, (0, 0))

        # if (fill_weight <= 0.0):
        #     # if there's no bar to draw, return (also avoids negative lerp)
        #     if (fill_weight < 0.0):
        #         print(f'{self}[draw_horizontal_bar]: fill_weight={fill_weight} < 0.0. returning.')
        #     return
        # elif (fill_weight > 1.0):
        #     print(f'{self}[draw_horizontal_bar]: fill_weight={fill_weight} > 1.0. treating as 1.0.')
        #     fill_weight = 1.0

        # create the bar rect using a midpoint value through lerp. this is faster than python math.
        BAR_WIDTH = lerp(0, self.BAR_SURF_RECT.w, fill_weight)
        BAR_RECT = Rect(0, 0, BAR_WIDTH, self.BAR_SURF_RECT.h)

        self.BAR_SURF.fill(self.bar_color, BAR_RECT)

        if (self.bar_border_width):
            draw_rect(self.BAR_SURF, self.bar_border_color, BAR_RECT, width=self.bar_border_width)

    def draw_vertical_bar(self, fill_weight: float):
        ''' vertical bar fill. top to bottom '''
        # clear the background
        if (self.FILL_WITH_ALPHA):
            self.ROOT_SURF.fill(self.FULL_ALPHA)
        self.BG_SURF.blit(self.BG_IMAGE, (0, 0))

        # if (fill_weight <= 0.0):
        #     # if there's no bar to draw, return (also avoids negative lerp)
        #     if (fill_weight < 0.0):
        #         print(f'{self}[draw_vertical_bar]: fill_weight={fill_weight} < 0.0. returning.')
        #     return
        # elif (fill_weight > 1.0):
        #     print(f'{self}[draw_vertical_bar]: fill_weight={fill_weight} > 1.0. treating as 1.0.')
        #     fill_weight = 1.0


        # create the bar rect using a midpoint value through lerp. this is faster than python math.
        BAR_HEIGHT = lerp(0, self.BAR_SURF_RECT.h, fill_weight)
        BAR_RECT = Rect(
            0, (self.BAR_SURF_RECT.h - BAR_HEIGHT),
            self.BAR_SURF_RECT.w, BAR_HEIGHT
        )

        self.BAR_SURF.fill(self.bar_color, BAR_RECT)

        if (self.bar_border_width):
            draw_rect(self.BAR_SURF, self.bar_border_color, BAR_RECT, width=self.bar_border_width)

    def __str__(self):
        msg = f'[{super().__str__()} : '
        msg += f'rect="{self.rect}", ref_id={self.ref_id}]'
        return msg


class UI_Icon_Bar_Horizontal(UI_Bar):
    def __init__(self,
            cf_icon_bar: dict,
            cf_global: dict,
            position: tuple[int, int],
            bar_size: tuple[int, int],
        ):

        # bar_width = size[0] - icon_offset - size[1]
        super().__init__(cf_icon_bar['cf_bar'], cf_global, cf_icon_bar['ref_id'], position, bar_size)

        self.icon_path = cf_icon_bar['icon_path']
        self.icon_offset = cf_icon_bar['icon_offset']
        self.icon_bg = cf_icon_bar['icon_bg']

        self.icon_size = (self.rect.h, self.rect.h)
        ICON_IMG = image.load(self.icon_path).convert_alpha()

        if (self.icon_bg):
            # create background/border for icon
            ICON_BG_SURF = Surface((self.icon_size)).convert_alpha()
            ICON_BG_SURF.fill(self.bg_color)
            if (self.bg_border_width):
                draw_rect(ICON_BG_SURF, self.bg_border_color, ICON_BG_SURF.get_rect(), width=self.bg_border_width)

            # scale down icon by border width and a pixel clearing
            # self.icon_size = ((self.icon_size[0] - self.bg_border_width), (self.icon_size[1] - self.bg_border_width))
            self.ICON_BG = ICON_BG_SURF
            self.ICON_BG_RECT = ICON_BG_SURF.get_rect()
        else:
            self.ICON_BG = None

        self.ICON = transform.scale(ICON_IMG, self.icon_size)
        self.ICON_RECT = self.ICON.get_rect()

        # replace super root surf with the extended one
        new_root_width = (self.rect.w + self.rect.h + self.icon_offset)
        new_root_height = self.rect.h
        self.ROOT_SURF = Surface((new_root_width, new_root_height)).convert_alpha()
        self.ROOT_SURF.fill((0, 0, 0, 0))

        self.rect = self.ROOT_SURF.get_rect()

        # reposition rects
        self.BG_SURF_RECT.left += (self.ICON_RECT.w + self.icon_offset)
        self.BAR_SURF_RECT.left += (self.ICON_RECT.w + self.icon_offset + self.bg_border_width + self.internal_padding_y)
        self.BAR_SURF_RECT.top += (self.bg_border_width + self.internal_padding_y)
        # self.ICON_RECT.topleft = self.rect.topleft

        # update subsurfaces from super
        self.BG_SURF = self.ROOT_SURF.subsurface(self.BG_SURF_RECT)
        self.BAR_SURF = self.ROOT_SURF.subsurface(self.BAR_SURF_RECT)
        self.ICON_SURF = self.ROOT_SURF.subsurface(self.ICON_RECT)

        self.rect.topleft = self.position
        self.image = self.ROOT_SURF

    def draw_horizontal_bar(self, fill_weight: float):
        super().draw_horizontal_bar(fill_weight)
        if (self.ICON_BG):
            self.ICON_SURF.blit(self.ICON_BG, self.ICON_BG_RECT)
        self.ICON_SURF.blit(self.ICON, self.ICON_RECT)


class UI_Auto_Icon_Bar_Horizontal(UI_Icon_Bar_Horizontal):
    ''' uses a max value and a getter instead of weight between <0.0, 1.0] '''
    def __init__(self,
            cf_auto_icon_bar: dict,
            cf_global: dict,
            position: tuple[int, int],
            max_val: float,
            getter_func: Callable[[None], float],
        ):
        super().__init__(cf_auto_icon_bar['cf_icon_bar'], cf_global, position, cf_auto_icon_bar['size'])

        self.remove_when_empty = cf_auto_icon_bar['remove_when_empty']
        self.max_val = max_val
        self.GETTER_FUNC = getter_func

    def update(self):
        NEW_VAL = self.GETTER_FUNC()
        weight = (NEW_VAL / self.max_val)

        if (weight <= 0.0):
            if (self.remove_when_empty):
                self.kill()
                return
            else:
                weight = 0.0
        elif (weight > 1.0):
            self.max_val = self.GETTER_FUNC()
            weight = 1.0

        super().draw_horizontal_bar(weight)
