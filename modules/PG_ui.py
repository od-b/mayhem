from typing import Callable     # type hint for function pointers
import pygame as pg

from pygame.sprite import Sprite
from pygame import Surface, Rect, Color


class Container(Sprite):
    ''' Sprite serving as a surface container for UI objects
        the container surface will be subsurface of window.surface
        * alpha is an integer between 0 and 255, where 0 is transparent
        * if alpha == 0, color is set to alpha colorkey instead
        * ignores border color and width if alpha == 0
        * ignores border_color if border_width == 0
    '''
    def __init__(self,
            surface: Surface,
            size: tuple[int, int],
            position: tuple[int, int],
            align_content_x: str,
            align_content_y: str,
            alpha: int,
            color: Color,
            border_width: int,
            border_color: Color,
        ):

        Sprite().__init__(self)

        self.align_func: tuple[Callable[[Rect, int], None],Callable[[Rect, int], None]]\
            = self.get_align_func(align_content_x, align_content_y)

        self.content = []
        self.alpha = alpha
        self.size = size
        self.position = position
        ''' top left position of container '''

        # create root surface
        IMG = pg.Surface(self.size)

        if (self.alpha > 0):
            self.visible = True
            self.color = color
            self.border_width = border_width
            IMG.fill(self.color)
            if (self.border_width > 0):
                self.border_color = border_color
            if (self.alpha == 255):
                new_img = IMG.convert()
                IMG = new_img
            else:
                IMG.set_alpha(self.alpha)
        else:
            self.visible = False
            IMG.set_alpha(0)
            IMG.set_colorkey(self.color)

        # store originals
        self.ORIGINAL_IMAGE = IMG
        # create rect from the surface
        self.ORIGINAL_RECT = self.ORIGINAL_IMAGE.get_rect()
        
        # set current surface and rect
        self.image = self.ORIGINAL_IMAGE
        self.rect = self.ORIGINAL_RECT.copy()
        self.rect.topleft = self.position

    def fill_surface(self):
        ''' fill the image '''
        if (self.visible):
            self.image.fill(self.color)

    # def draw_surface_border(self):
    #     ''' draw border of rect the with the default color '''
    #     p_list = [self.rect.topleft, self.rect.topright, self.rect.bottomright, self.rect.bottomleft, self.rect.topleft]
    #     pg.draw.lines(self.window.surface, self.border_color, True, self.rect)

    def align_to_center_x_of(self, parent: Rect, offset: int):
        self.rect.centerx = parent.centerx + offset

    def align_to_center_y_of(self, parent: Rect, offset: int):
        self.rect.centery = parent.centery + offset

    def align_to_left_of(self, parent: Rect, offset: int):
        self.rect.right = parent.re.left - offset
        self.rect.y = parent.re.y

    def align_to_right_of(self, parent: Rect, offset: int):
        self.rect.left = parent.re.right + offset
        self.rect.y = parent.re.y

    def align_to_top_of(self, parent: Rect, offset: int):
        self.rect.bottom = parent.re.top - offset
        self.rect.x = parent.re.x

    def align_to_bottom_of(self, parent: Rect, offset: int):
        self.rect.top = parent.re.bottom + offset
        self.rect.x = parent.re.x

    def get_align_func(self, children_align_x: str, children_align_y: str):
        ''' get the correct alignment function for positioning children '''

        match (children_align_x):
            case 'left':
                align_x = self.align_to_left_of
            case 'right':
                align_x = self.align_to_right_of
            case 'center':
                align_x = self.align_to_center_x_of
            case _:
                raise ValueError(f'children_align_x expected "left", "right",\
                    or "centerx". Found "{children_align_x}"')

        match (children_align_x):
            case 'top':
                align_y = self.align_to_top_of
            case 'bottom':
                align_y = self.align_to_bottom_of
            case 'center':
                align_y = self.align_to_center_y_of
            case _:
                raise ValueError(f'children_align_y expected "top", "bottom", "left", "right",\
                    "centerx" or "centery". Found "{children_align_y}"')
        
        return (align_x, align_y)


class Text_Box(Sprite):
    ''' Sprite for rendering and displaying text
        * must have a container
        * If border_width is set, a color must also be set.
        * apply_aa is whether or not to apply antialiasing when rendering
        * will auto get string if not static and provided a getter function

        For objects with a getter_func, the initial string serves as a 'pre-text'
        and will consist even when self.content is updated.
        For no pre-text, simply pass content as an empty string -> ''
    '''

    def __init__(self, 
            container: Container, 
            container_offset_x: int, 
            container_offset_y: int,
            text: str, 
            font_path: str,
            font_size: int, 
            font_color: pg.Color,
            font_antialas: bool, 
            getter_func: Callable | None,
            is_static: bool
        ):

        Sprite().__init__(self)

        # load the font, then render the text and create rect
        self.font = pg.font.Font(str(font_path), int(font_size))
        self.render: pg.Surface

        # initialize the rendering, and then get its rect
        self.replace_rendered_text()
        self.replace_rect()

    def render_content(self) -> pg.Surface:
        ''' replaces self.render with a text render of the self.content text '''
        self.render = self.font.render(
            self.content,
            self.font_antialas,
            self.font_color,
            self.txt_bg_color
        )

    def update_blit_position(self):
        ''' update the blit position according to the rect position + padding '''
        self.blit_pos = ((self.re.left + self.blit_adjust_x), (self.re.top + self.blit_adjust_y))

    def replace_rect(self):
        ''' replaces self.re with a rect from the rendering. Correct its size and position. '''
        new_rect = self.get_adjusted_rect()
        # reposition, then replace
        new_rect.topleft = ((self.re.x, self.re.y))
        self.re = new_rect
        self.update_blit_position()

    def update_content(self, new_content: str):
        ''' update the string (or pretext, if getter exists) to display '''
        self.content = new_content

    def update(self):
        ''' update content if a getter exists. Does nothing if object is static
            * Recreates text rendering, rect and border to fit the new content '''

        if not self.is_static:
            # auto-get new string if a getter is provided
            if self.getter_func:
                self.content = f'{self.pretext}{self.getter_func()}'

            # re-render and get the new rect
            self.window.surface.blit(self.render, self.blit_pos)
            self.replace_rendered_text()
            self.replace_rect()

            # re-create the border if its set to be displayed
            if self.border:
                self.replace_border_rect()
