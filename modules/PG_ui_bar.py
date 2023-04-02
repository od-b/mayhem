from typing import Callable

## import needed pygame modules
from pygame import Surface, Rect, Color, SRCALPHA, transform, image
from pygame.math import lerp, clamp
from pygame.sprite import Sprite, Group
from pygame.draw import rect as draw_rect
from pygame.draw import line as draw_line, lines as draw_lines


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

        self.bg_surf_rect = self.BG_SURF.get_rect()
        self.bar_surf_rect = self.BAR_SURF.get_rect()

        # set image to the root surface
        self.image = self.ROOT_SURF
        self.rect = self.ROOT_RECT
        self.rect.topleft = position

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
        if (self.bg_alpha_key != 255):
            self.ROOT_SURF.fill((0, 0, 0, 0))
        self.BG_SURF.blit(self.BG_IMAGE, (0, 0))

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
            # bar_rect.inflate(-self.bar_border_width, -self.bar_border_width)
            # draw_lines(self.BAR_SURF, self.bar_border_color, False, coords, self.bar_border_width)
            draw_rect(self.BAR_SURF, self.bar_border_color, bar_rect, width=self.bar_border_width)

    def draw_vertical_bar(self, fill_weight: float):
        ''' vertical bar fill. top to bottom '''
        # clear the background
        if (self.bg_alpha_key != 255):
            self.ROOT_SURF.fill((0, 0, 0, 0))
        self.BG_SURF.blit(self.BG_IMAGE, (0, 0))

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
            # coords = [bar_rect.topleft, bar_rect.topright, bar_rect.bottomright, bar_rect.bottomleft]
            # draw_lines(self.BAR_SURF, self.bar_border_color, False, coords, self.bar_border_width)
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
            bar_size: tuple[int, int],
            icon_path: str,
            icon_offset: int,
            copy_super_bg: bool
        ):

        # bar_width = size[0] - icon_offset - size[1]
        super().__init__(cf_bar_style, cf_global, ref_id, position, bar_size)

        self.icon_path = icon_path
        self.icon_offset = icon_offset
        self.copy_super_bg = copy_super_bg

        self.icon_size = (self.rect.h, self.rect.h)
        ICON_IMG = image.load(icon_path).convert_alpha()

        if (self.copy_super_bg):
            # create background/border for icon
            ICON_BG_SURF = Surface((self.icon_size)).convert_alpha()
            ICON_BG_SURF.fill(self.bg_color)
            if (self.bg_border_width):
                draw_rect(ICON_BG_SURF, self.bg_border_color, ICON_BG_SURF.get_rect(), width=self.bg_border_width)

            # scale down icon by border width and a pixel clearing
            # self.icon_size = ((self.icon_size[0] - self.bg_border_width), (self.icon_size[1] - self.bg_border_width))
            self.ICON_BG = ICON_BG_SURF
            self.icon_bg_rect = ICON_BG_SURF.get_rect()
        else:
            self.ICON_BG = None

        self.ICON = transform.scale(ICON_IMG, self.icon_size)
        self.icon_rect = self.ICON.get_rect()

        # replace super root surf with the extended one
        new_root_width = (self.rect.w + self.rect.h + self.icon_offset)
        new_root_height = self.rect.h
        self.ROOT_SURF = Surface((new_root_width, new_root_height)).convert_alpha()
        self.ROOT_SURF.fill((0, 0, 0, 0))

        self.rect = self.ROOT_SURF.get_rect()

        # reposition rects
        self.bg_surf_rect.left += (self.icon_rect.w + self.icon_offset)
        self.bar_surf_rect.left += (self.icon_rect.w + self.icon_offset + self.bg_border_width + self.internal_padding_y)
        self.bar_surf_rect.top += (self.bg_border_width + self.internal_padding_y)
        # self.icon_rect.topleft = self.rect.topleft

        # update subsurfaces from super
        self.BG_SURF = self.ROOT_SURF.subsurface(self.bg_surf_rect)
        self.BAR_SURF = self.ROOT_SURF.subsurface(self.bar_surf_rect)
        self.ICON_SURF = self.ROOT_SURF.subsurface(self.icon_rect)

        self.rect.topleft = self.position
        self.image = self.ROOT_SURF

    def draw_horizontal_bar(self, fill_weight: float):
        super().draw_horizontal_bar(fill_weight)
        if (self.ICON_BG):
            self.ICON_SURF.blit(self.ICON_BG, self.icon_bg_rect)
        self.ICON_SURF.blit(self.ICON, self.icon_rect)


class UI_Icon_Auto_Bar(UI_Icon_Bar):
    def __init__(self,
            cf_bar_style: dict,
            cf_global: dict,
            ref_id,
            position: tuple[int, int],
            bar_size: tuple[int, int],
            icon_path: str,
            icon_offset: int,
            copy_super_bg: bool,

            min_val: float,
            max_val: float,
            getter_func: Callable[[None], float],
            fill_direction: str
        ):

        # bar_width = size[0] - icon_offset - size[1]
        super().__init__(cf_bar_style, cf_global, ref_id, position, bar_size, icon_path, icon_offset, copy_super_bg)

        self.min_val = min_val
        self.max_val = max_val

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
        print(fill_val, self.max_val)
        if (fill_val > self.min_val):
            if (fill_val > self.max_val):
                self.max_val = fill_val
            fill_weight = (fill_val/self.max_val)
            self.bar_draw_func(lerp(self.min_val, self.max_val, fill_weight))


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
            fill_direction: str
        ):
        super().__init__(cf_bar_style, cf_global, ref_id, position, size)

        self.min_val = min_val
        self.max_val = max_val

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
        print(fill_val, self.max_val)
        if (fill_val > self.min_val):
            if (fill_val > self.max_val):
                self.max_val = fill_val
            fill_weight = (fill_val/self.max_val)
            self.bar_draw_func(lerp(self.min_val, self.max_val, fill_weight))
