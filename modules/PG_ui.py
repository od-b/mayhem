from typing import Callable
from pygame import Surface, Rect, Color
from pygame.sprite import Sprite, Group
from pygame.draw import rect as draw_rect
from pygame.font import Font


class Container(Sprite):
    ''' Sprite serving as a surface container for UI objects.
        The container .image will be subsurface of the given surface

        * alpha is an integer between 0 and 255, where 0 is transparent
        * ignores border color and width if alpha == 0
        * if alpha == 0, color is used to set alpha colorkey(color)
        * align_content_x   :   str[ "left" | "right" | "center" ]
        * align_content_y   :   str[ "top" | "bottom" | "center" ]
    '''

    def __init__(self,
            surface: Surface,
            size: tuple[int, int],
            position: tuple[int, int],
            align_content_x: str,
            align_content_y: str,
            color: Color,
            border_color: Color,
            border_width: int,
        ):

        Sprite.__init__(self)

        self.align_func: tuple[Callable[[Rect, int], None],Callable[[Rect, int], None]]\
            = self.get_align_func(align_content_x, align_content_y)

        self.size = size
        self.position = position
        self.color = color
        self.border_width = border_width
        self.border_color = border_color

        self.children = Group()
        
        self.RECT_INFLATE_VAL = int(-2*self.border_width)

        # create root surface
        self.SURF_RECT = Rect((self.position), (self.size))
        self.SURF = surface.subsurface(self.SURF_RECT)
        # fill the original surface

        # create the border of the container as a rect
        self.bg_image = Surface(self.size).convert()
        self.bg_rect = self.bg_image.get_rect()
        self.bg_image.fill(self.border_color, self.bg_rect)

        # draw the smaller main color rect onto the background
        rect_cpy = self.bg_rect.copy().inflate(self.RECT_INFLATE_VAL, self.RECT_INFLATE_VAL)
        draw_rect(self.bg_image, self.color, rect_cpy)

        # store the background template
        self.image = self.bg_image
        self.rect = self.bg_rect.copy()

        # blit to the subsurface
        self.SURF.blit(self.image, self.rect)

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

    def position_children(self):
        pass

    def update(self):
        Surface.blit(self.bg_image, self.SURF, self.SURF_RECT)
        self.children.update()
        for child in self.children:
            child_rect = child.get_updated_rect()
            child_rect.centerx = self.rect.centerx
            child_rect.centery = self.rect.centery
        self.children.draw(self.SURF)

class Text_Box(Sprite):
    ''' Sprite for rendering and displaying text
        * must have a container
        * If border_width is set, a color must also be set.
        * text_is_const is whether or not the text will change after creation
        * font_antialias is whether to apply antialiasing when rendering
        * will auto get string if not text_is_const and provided a getter function

        For objects with a text_getter_func, the initial string serves as a 'pre-text'
        and will consist even when self.content is updated.
        For no pre-text, simply pass content as an empty string -> ''
    '''

    def __init__(self, 
            parent: Container,
            internal_padding_w: int,
            internal_padding_h: int,
            border_width: int,
            border_color: Color | None,
            bg_color: Color,
            text: str,
            text_is_const: bool,
            text_getter_func: Callable | None,
            font_path: str,
            font_size: int,
            font_color: Color,
            font_antialas: bool,
        ):

        Sprite.__init__(self)
        
        self.parent = parent
        self.internal_padding_w = internal_padding_w
        self.internal_padding_h = internal_padding_h
        self.border_width = border_width
        self.border_color = border_color
        self.bg_color = bg_color
        self.text = text
        self.text_is_const = text_is_const
        self.text_getter_func = text_getter_func
        self.font_path = font_path
        self.font_size = font_size
        self.font_color = font_color
        self.font_antialas = font_antialas
        
        if (self.text_getter_func):
            self.pre_text = self.text

        self.old_text = text

        # load the font, then render the text and create rect
        self.font = Font(font_path, font_size)
        self.image = self.font.render(
            self.text,
            self.font_antialas,
            self.font_color,
            self.font_color
        )
        self.rect = self.get_updated_rect()
        
        # allows for for a simple, generalized update func
        if (self.text_getter_func):
            self._text_update_func = self._get_text_from_getter_func
        else:
            self._text_update_func = self.get_text

    def update_text_render(self):
        ''' replaces self.image with a text render of the self.content text '''
        self.image = self.font.render(
            self.text,
            self.font_antialas,
            self.font_color,
            self.bg_color
        )

    def _get_text_from_getter_func(self):
        ''' returns a string through the given text_getter_func '''
        return f'{self.pre_text}{self.text_getter_func()}'

    def set_text(self):
        ''' returns self.text '''
        return self.text

    def get_text(self):
        ''' returns self.text '''
        return self.text

    def get_updated_rect(self) -> Rect:
        ''' update self.rect from image get_rect, then return the rect '''
        self.rect = self.image.get_rect()
        return self.rect

    def update(self):
        ''' update content if a getter exists. Does nothing if object is static '''

        # check if there's possible that theres something to update first
        if not self.text_is_const:
            # get updated text from one of the internal methods
            # this will either be through a getter func, or if self.text has been
            # manually changed since the last frame
            NEW_TEXT = self._text_update_func()
            # if new text is not the same as the last, replace and re-render
            # rendering is very expensive in pygame, so the strcmp is absolutely worth it
            if (NEW_TEXT != self.text):
                self.text = NEW_TEXT
                self.update_text_render()
