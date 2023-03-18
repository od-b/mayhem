from typing import Callable     # type hint for function pointers --> https://docs.python.org/3/library/typing.html
import pygame as pg
from modules.PG_shapes import PG_Rect


class PG_Text_Box(PG_Rect):
    ''' 
        Extends PG_Rect. All rendered text in pygame must have a rect, so by extending
        we can utilize relevant pre-existing methods.
        
        * is_static determines whether the internal parts (render+rect) is to be updated before each blit.
        ** i.e; for textboxes that will not have their text changed, set is_static = True

        * If border_width is set, a color must also be set. (see PG_Rect)
        
        * apply_aa is whether or not to apply antialiasing when rendering
        
        * will auto get string if not static and provided a getter function
    '''
    def __init__(self, window, content: str, font_path: str, font_size: int, apply_aa: bool, font_color: tuple,
                 bg_color: None | tuple, border_color: None | tuple, border_width: int, getter_func: Callable | None,
                 x: int, y: int, is_static: bool):

        # rect is dynamically created through update_txt_rect, so init with 0-values for w/h
        super().__init__(window, x+border_width, y+border_width, 0, 0, border_width, bg_color, border_color)
        #   def __init__(window, x, y, w, h, border_width, bg_color, border_color):

        ## misc:
        self.font_color = font_color
        self.content = content
        self.apply_aa = apply_aa
        self.is_static = is_static
        self.getter_func = getter_func
        if (self.getter_func):
            self.pretext = self.content

        # load the font, then render the text
        self.font = pg.font.Font(str(font_path), int(font_size))
        self.txt: pg.Surface
        self.render_txt()
        self.replace_rect()
        
        # if (self.border_width > 0):
        #     self.create_border()

    def update_content(self, new_content: str):
        ''' update the string to display '''
        self.content = new_content

    def render_txt(self):
        ''' replace self.txt with a new rendering, using self.content string '''
        self.txt = self.font.render(
            self.content,
            self.apply_aa,
            self.font_color,
            self.bg_color
        )

    def replace_rect(self):
        ''' apply correct position to the internal rect '''
        # get rect from current rendering
        new_rect = self.txt.get_rect()
        # apply position from the current rect, then replace
        new_rect.x = self.re.x
        new_rect.y = self.re.y
        self.re = new_rect
    
    def update(self):
        ''' update (unless static), draw rect if bg_color/border_color, then blit'''
        # if not static, update first
        if not self.is_static:
            # auto-get new string if a getter is provided
            if self.getter_func:
                self.content = f'{self.pretext}{self.getter_func()}'

            # update rendering @ self.txt
            self.render_txt()

            # replace rect @ self.re
            # replacing is nescessary as simply moving the prev rect would not allow
            # for a rect with varying size.
            self.replace_rect()

            # re-create the border if its set to be displayed
            if self.border_width > 0:
                self.create_border()
                self.draw_border()
        else:
            if self.border_width > 0:
                self.draw_border()

        # finally, blit the rendered text onto the rect
        self.window.surface.blit(self.txt, self.re)


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

        # refer alignment to the correct function
        match parent_alignment:
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
        # new_rect = self.txt.get_rect()
        # # apply position from the current rect, then replace
        # new_rect.x = self.re.x
        # new_rect.y = self.re.y
        self.re = self.txt.get_rect()
        self.align_func(self.parent, self.offset)
