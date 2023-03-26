from typing import Callable
from pygame import Surface, Rect, Color
from pygame.sprite import Sprite, Group
from pygame.draw import rect as draw_rect
from pygame.draw import line as draw_line
from pygame.font import Font


class Container(Sprite):
    ''' Sprite serving as a surface container for UI objects.
        The container .image will be subsurface of the given surface

        * surface is passed to create a subsurface internally
        * children_align expects: "top", "bottom",\
            "left", "right", "bottomleft" or "topleft"
        * child_flow expects: "top_bottom", "left_right"
        * All configurations work, but combinations like "bottomleft" and "top_bottom"
            do not exactly look pretty
        * update() is the only function that should be called externally.
        
        The general idea here is creating a framework that is easy to modify and 
        configure to meet any need without having to modify any previous code
    '''

    def __init__(self,
            surface: Surface,
            size: tuple[int, int],
            position: tuple[int, int],
            color: Color,
            border_color: Color,
            border_width: int,
            child_align: str,
            child_flow: str,
            child_padding: int,
            separator_width: int,
            separator_color: int
        ):

        Sprite.__init__(self)

        self.size = size
        self.position = position
        self.color = color
        self.border_width = border_width
        self.border_color = border_color
        self.child_padding = child_padding
        self.separator_width = separator_width
        self.separator_color = separator_color
        self.child_flow = child_flow
        self.child_align = child_align
        
        # calculate the correct padding for separator
        self.separator_padding = int((self.child_padding/2) + self.separator_width/2)
        self.draw_separator = False
        self.children = Group()
        ''' group of sprites that depend on the container for updates/positioning '''

        print(self.position, self.size)
        # create surface of the container
        self.SURF_RECT = Rect((self.position), (self.size))
        self.SURF = surface.subsurface(self.SURF_RECT)
        ''' the surfaces here might seem confusing at first glance.
            * SURF_RECT / SURF is the entire container portion of the subsurface
            * image is the empty background surface with border, created for the container
            
            in short:
            * never blit/draw a source surface onto to self.image
            * blit self.image onto SURF to clear
            * pass self.SURF as surface for any children to be drawn
            * we never have to spend resources refilling the surface/creating border
            * => profit
        '''

        # create the border of the container as a rect
        self.image = Surface(self.size).convert()
        self.rect = self.image.get_rect()
        
        if (self.border_width > 0):
            self.image.fill(self.border_color, self.rect)
            # create a rect -2*self.border_width smaller than the surface
            PADDED_RE = self.rect.copy().inflate(
                int(-2*self.border_width),
                int(-2*self.border_width)
            )
            # draw the background color ontop of what now makes the border
            draw_rect(self.image, self.color, PADDED_RE)
        else:
            self.image.fill(self.color, self.rect)

        # find fitting functions instead of performing tests every frame:
        self.ALIGN_FUNC = self._get_align_func(self.child_align)
        self._set_pos_funcs(self.child_flow)

    def _align_to_left_of(self, child: Rect, parent: Rect):
        child.right = parent.left - self.child_padding
        child.centery = parent.centery

    def _align_to_right_of(self, child: Rect, parent: Rect):
        child.left = parent.right + self.child_padding
        child.centery = parent.centery

    def _align_to_top_of(self, child: Rect, parent: Rect):
        child.bottom = parent.top - self.child_padding
        child.centerx = parent.centerx

    def _align_to_bottom_of(self, child: Rect, parent: Rect):
        child.top = parent.bottom + self.child_padding
        child.centerx = parent.centerx

    def _align_to_topleft_of(self, child: Rect, parent: Rect):
        child.bottomleft = (parent.topleft[0], parent.topleft[1] - self.child_padding)

    def _align_to_bottomleft_of(self, child: Rect, parent: Rect):
        child.topleft = (parent.bottomleft[0], parent.bottomleft[1] + self.child_padding)

    def _draw_vertical_right_separator(self, RE: Rect):
        # draw separating line vertically on the right of rect
        p1 = ((RE.topright[0] + self.separator_padding), RE.topright[1])
        p2 = ((RE.bottomright[0] + self.separator_padding), RE.bottomright[1])
        draw_line(self.SURF, self.separator_color, p1, p2, self.separator_width)

    def _draw_horizontal_bottom_separator(self, RE: Rect):
        # draw separating line horizontally on the bottom of rect
        p1 = ((RE.bottomleft[0] + self.separator_padding), RE.bottomleft[1])
        p2 = ((RE.bottomright[0] + self.separator_padding), RE.bottomright[1])
        draw_line(self.SURF, self.separator_color, p1, p2, self.separator_width)

    def _position_and_separate_children(self):
        ''' positions children according to the align_func
            and draws a separator using SEPARATE_FUNC 
        '''
        parent = self.ALIGN_PARENT
        for child in self.children:
            RE = child.rect
            self.ALIGN_FUNC(RE, parent)
            parent = RE
            # draw separating line vertically
            self.DRAW_FUNC(RE)

    def _position_children(self):
        ''' positions children according to the align_func '''
        parent = self.ALIGN_PARENT
        for child in self.children:
            RE = child.rect
            self.ALIGN_FUNC(RE, parent)
            parent = RE

    def _get_align_func(self, child_align: str) -> Callable[[Rect, Rect], None]:
        ''' get the correct alignment function for positioning children '''
        # additional positioning functions can easily be added
        match (child_align):
            case 'left':
                return self._align_to_left_of
            case 'right':
                return self._align_to_right_of
            case 'top':
                return self._align_to_top_of
            case 'bottom':
                return self._align_to_bottom_of
            case 'bottomleft':
                return self._align_to_topleft_of
            case 'topleft':
                return self._align_to_bottomleft_of
            case _:
                raise ValueError(f'\
                    children_align expected: "top", "bottom",\
                    "left", "right", "bottomleft" or "topleft".\n\
                    Found "{child_align}"')

    def _set_pos_funcs(self, child_flow):
        ''' set self.POSITION_FUNC, self.DRAW_FUNC and self.ALIGN_PARENT 
            * self.ALIGN_PARENT is a parent rect used by the first child for each positioning
            * self.DRAW_FUNC is one of the different '_draw_<...>_separator' methods
            * self.POSITION_FUNC is one of the different '_position...' methods

            by using references we only have to perform checks once, as opposed to every single frame.
        '''
        match (child_flow):
            case 'top_bottom':
                self.ALIGN_PARENT = self.rect.copy()
                self.ALIGN_PARENT.height = 0
                self.ALIGN_PARENT.top -= self.separator_padding
                self.DRAW_FUNC = self._draw_horizontal_bottom_separator
            case 'left_right':
                self.ALIGN_PARENT = self.rect.copy()
                self.ALIGN_PARENT.width = 0
                self.ALIGN_PARENT.left -= self.separator_padding
                self.DRAW_FUNC = self._draw_vertical_right_separator
            case _:
                raise ValueError(f'\
                    child_flow expected: "horizontal" or "vertical"\n\
                    Found: {child_flow}')
        
        # set position func to either just position, or position and draw a line
        if (self.separator_width == 0):
            self.POSITION_FUNC = self._position_children
        else:
            self.POSITION_FUNC = self._position_and_separate_children
            self.child_padding += self.separator_width

    def verify_children_size(self):
        problem_children = []

        for child in self.children:
            child = f'{child}\n'
            if (child.rect.h > self.rect.h) or (child.rect.w > self.rect.w):
                problem_children.append(child)

        if (len(problem_children) > 0):
            msg = f'WARNING: children too wide or tall to fit.\n{self}. \nProblem children:\n'
            for child in problem_children:
                msg += str(child)
            print(msg)

    def get_children(self) -> list[Sprite]:
        ''' returns a list containing the children sprites '''
        return self.children.sprites()

    def get_num_children(self) -> int:
        ''' returns the current number of children '''
        return len(self.children.sprites())

    def remove_all_children(self) -> int:
        ''' removes all children from self.children '''
        self.children.empty()

    def update(self):
        self.SURF.blit(self.image, self.rect)
        # update children
        self.children.update()
        # position and align children. draw separater if set.
        self.POSITION_FUNC()
        # blit the background surface to clear any past blits
        # draw children
        self.children.draw(self.SURF)

    def __str__(self):
        msg = f'< Container with {self.get_num_children()} children.\n'
        msg += f'  position(x,y)={self.position}, height={self.rect.h}, width={self.rect.h},\n'
        msg += f'  child_flow="{self.child_flow}", child_align="{self.child_align}", '


class Text_Box(Sprite):
    ''' Sprite for rendering and displaying text

        Parameters
        ---
        font_antialias: bool
            whether to apply antialiasing when rendering text

        ---
        text_getter_func: Callable[[None], any] | None
            * must take no parameters. The return value will be converted to a string.
            * on update, will call the function and set its text to the returned value
            * if provided, and given text is not and empty string, 
                the initial text parameter will serve as a 'pre-text' for all updated strings.
        --- 
        if None is passed as text_getter_func and the text is to be changed, set_new_text()
        must be called manually to update the text and its rendering.
    '''

    def __init__(self,
            bg_color: Color | None,
            text: str,
            text_getter_func: Callable | None,
            font_path: str,
            font_size: int,
            font_color: Color,
            font_antialas: bool,
        ):

        Sprite.__init__(self)

        self.bg_color = bg_color
        self.text = text
        self.text_getter_func = text_getter_func
        self.font_path = font_path
        self.font_size = font_size
        self.font_color = font_color
        self.font_antialas = font_antialas

        self.font = Font(font_path, font_size)
        self.old_text = text
        self.text_is_const: bool = True
        ''' whether the text will be re-rendered on update '''

        # allows for for a simple, generalized update func
        if (self.text_getter_func):
            self.text_is_const = False
            self.pre_text = self.text
            if (self.pre_text == ''):
                self._text_update_func = self._get_text_from_getter_func
            else:
                self._text_update_func = self._get_text_from_getter_func_with_pre_text
        else:
            self.pre_text = str('')
            self._text_update_func = self.get_text

        # load the font, then render the text and create rect
        self.image = self.font.render(
            self.text,
            self.font_antialas,
            self.font_color,
            self.bg_color
        )
        self.rect = self.image.get_rect()

    def _get_text_from_getter_func(self):
        ''' internal function: returns a string through the given text_getter_func, no pre_text '''
        return str(self.text_getter_func())

    def _get_text_from_getter_func_with_pre_text(self):
        ''' internal function: returns a string through the given text_getter_func
            * concats the text provided originally and the string from the getter
        '''
        return f'{self.pre_text}{self.text_getter_func()}'

    def get_text(self):
        ''' returns the exact text displayed on the current render '''
        return self.text

    def set_pre_text(self, text: str):
        ''' for replacement of pretext. Does not call render if a getter exists. 
            
            if a getter does not exist, sets text to "self.pre_text + self.text".

            if a getter does exist, update_text_render() does not need to be called.
            
            if manually updating a text without a getter func, that already has pre-text:
                1) call set_text, 
                2) call this function, 
                3) call update_text_render() to update the rendering
        '''
        self.pre_text = text
        if not self.text_getter_func:
            self.text = f'{self.pre_text}{self.text}'

    def set_text(self, text: str):
        ''' for manual replacement of text.
            * call update_text_render() when ready to render
        '''
        self.text = text

    def update_text_render(self):
        ''' replaces self.image with a text render of the self.content text. Updates self.rect '''
        self.image = self.font.render(
            self.text,
            self.font_antialas,
            self.font_color,
            None
        )
        self.rect = self.image.get_rect()

    def draw_line_on_right_edge(self, surface: Surface, offset: int, color: Color, width: int):
        p1 = ((self.rect.topright[0] + offset), self.rect.topright[1])
        p2 = ((self.rect.bottomright[0] + offset), self.rect.bottomright[1])
        draw_line(surface, color, p1, p2, width)

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

    def __str__(self):
        msg = f'< Text_Box with text="{self.pre_text}{self.text}"'
        msg += f'  height={self.rect.h}, width={self.rect.w} >'
        return msg
