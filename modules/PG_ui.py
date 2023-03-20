from typing import Callable     # type hint for function pointers
import pygame as pg
from modules.PG_shapes import PG_Rect


class PG_Text_Box(PG_Rect):
    ''' Extends PG_Rect. All rendered text in pygame must have a rect, so by extending we can access
        relevant pre-existing methods.

        * is_static determines whether the internal parts (render+rect) is to be updated before each blit.
        * If border_width is set, a color must also be set. (see PG_Rect)
        * apply_aa is whether or not to apply antialiasing when rendering
        * will auto get string if not static and provided a getter function

        For objects with a getter_func, the initial string serves as a 'pre-text'
        and will consist even when self.content is updated.
        For no pre-text, simply pass content as an empty string -> ''
    '''

    def __init__(self, window, content: str, font_path: str, font_size: int, apply_aa: bool, font_color: tuple,
                 bg_color: None | tuple, border_color: None | tuple, border_width: int, getter_func: Callable | None,
                 x: int, y: int, is_static: bool):

        # rect is dynamically created through update_txt_rect, so init with 0-values for w/h
        super().__init__(window, x+border_width, y+border_width, 0, 0, border_width, bg_color, border_color)

        self.font_color = font_color
        self.content = content
        self.apply_aa = apply_aa
        self.is_static = is_static
        self.getter_func = getter_func
        self.txt_bg_color = self.bg_color
        
        if (self.getter_func):
            self.pretext = self.content

        # load the font, then render the text and create rect
        self.font = pg.font.Font(str(font_path), int(font_size))
        self.render: pg.Surface

        # initialize the rendering, and then get its rect
        self.replace_rendered_text()
        self.replace_rect()

    def replace_rendered_text(self) -> pg.Surface:
        ''' replaces self.render with a text render of the self.content text '''
        self.render = self.font.render(self.content, self.apply_aa, self.font_color, self.txt_bg_color)

    def replace_rect(self):
        ''' replaces self.re with a rect from the rendering '''
        # get rect from current rendering
        new_rect = self.render.get_rect()
        # apply position from the current rect, then replace
        new_rect.x = self.re.x
        new_rect.y = self.re.y
        self.re = new_rect

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
            self.replace_rendered_text()
            self.replace_rect()

            # re-create the border if its set to be displayed
            if self.border:
                self.replace_border_rect()

    def draw(self):
        ''' draw/blit the rect (and border if it exists )'''
        if self.border:
            self.draw_border()
        self.window.surface.blit(self.render, self.re)


class PG_Text_Box_Child(PG_Text_Box):
    '''
        text box with centering relative to a parent
        * parent is another PG_Text_Box (or PG_Rect) that the textbox can 'attach' to.
        * parent_alignment accepts: "top", "bottom", "left", "right" "centerx" or "centery".
        * offset is how many extra pixels to position away from parent.
        ** (offset may be 0)
        ** for 'centerx' / 'centery' only, offset can be both negative and positive.

        note: for correct positioning, call update on parent FIRST
    '''
    def __init__(self, window, content: str, font_path: str, font_size: int, apply_aa: bool, font_color: tuple,
                 bg_color: None | tuple, border_color: None | tuple, border_width: int, getter_func: Callable | None,
                 parent: PG_Rect | PG_Text_Box, parent_alignment: str, offset: int):
    
        ## parent and relation:
        self.parent = parent
        self.offset = offset
        self.align_func: Callable

        # match alignment setting to the correct placement function
        match (parent_alignment):
            case 'top':
                self.align_func = self.align_to_top_of
            case 'bottom':
                self.align_func = self.align_to_bottom_of
            case 'left':
                self.align_func = self.align_to_left_of
            case 'right':
                self.align_func = self.align_to_right_of
            case 'centerx':
                self.align_func = self.align_to_center_x_of
            case 'centery':
                self.align_func = self.align_to_center_y_of
            case _:
                raise ValueError(f'parent_alignment expected "top", "bottom", "left", "right",\
                    "centerx" or "centery". Got "{parent_alignment}"')

        # init at dummy position (0, 0), is_static=false
        super().__init__(window, content, font_path, font_size, apply_aa, font_color, bg_color,
                         border_color, border_width, getter_func, 0, 0, False)

    def replace_rect(self):
        # overwrite parent method to replace rect
        self.re = self.render.get_rect()
        self.align_func(self.parent, self.offset)
