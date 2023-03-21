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

    def __init__(self, window, content: str, font_path: str, font_size: int, font_color: pg.Color,
                 apply_aa: bool, bg_color: pg.Color, border_color: None | pg.Color, border_width: int,
                 internal_padding_w: int, internal_padding_h: int,
                 getter_func: Callable | None, x: int, y: int, is_static: bool):

        # rect is dynamically created through update_txt_rect, so init with 0-values for w/h
        # position, however, is passed on to the new rect in replace_rect
        super().__init__(window, x+border_width, y+border_width, 0, 0, border_width, bg_color, border_color)

        self.font_color = font_color
        self.content = content
        self.apply_aa = apply_aa
        self.is_static = is_static
        self.internal_padding_w = internal_padding_w
        self.internal_padding_h = internal_padding_h
        self.getter_func = getter_func
        
        self.blit_adjust_x = int(internal_padding_w/2)
        self.blit_adjust_y = int(internal_padding_h/2)
        self.blit_pos: tuple

        # set text background color to the color used by the super() rect
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

    def get_adjusted_rect(self):
        ''' get rect from rendering, adjusted for padding '''
        return self.adjust_rect_padding(
            self.render.get_rect(),
            self.internal_padding_w,
            self.internal_padding_h
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
            self.replace_rendered_text()
            self.replace_rect()

            # re-create the border if its set to be displayed
            if self.border:
                self.replace_border_rect()

    def draw(self):
        ''' blit render to the rect, draw border if set '''
        if self.border:
            self.draw_border()
            self.draw_background()
        self.window.surface.blit(self.render, self.blit_pos)


class PG_Text_Box_Child(PG_Text_Box):
    ''' text box with centering relative to a parent
        * parent is another PG_Text_Box (or PG_Rect) that the textbox can 'attach' to.
        * parent_alignment accepts: "top", "bottom", "left", "right" "centerx" or "centery".
        * offset is how many extra pixels to position away from parent. (offset may be 0)
        * for 'centerx' / 'centery' only, offset can be both negative and positive.

        note: for correct positioning, call update on parent FIRST
        
        note_1: second generation subclass. Careful touching anything in here
    '''

    def __init__(self, window, content: str, font_path: str, font_size: int, font_color: pg.Color,
                 apply_aa: bool, bg_color: pg.Color, border_color: None | pg.Color, border_width: int,
                 internal_padding_w: int, internal_padding_h: int, getter_func: Callable | None,
                 parent: PG_Rect | PG_Text_Box, parent_alignment: str, parent_offset: int):
    
        ## parent and relation:
        self.parent = parent
        self.parent_offset = parent_offset
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
                    "centerx" or "centery". Found "{parent_alignment}"')

        # the super call is done post self-initialization, as self.align_func must
        # be defined before the super init will call _reposition_rect, modified below
        super().__init__(window, content, font_path, font_size, font_color, apply_aa, bg_color,
                         border_color, border_width, internal_padding_w, internal_padding_h,
                         getter_func, 0, 0, False)

    def replace_rect(self):
        ''' override super method to set anchored positioning through align_func '''
        self.re = self.get_adjusted_rect()
        self.align_func(self.parent, self.parent_offset)
        self.update_blit_position()
