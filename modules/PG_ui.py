from typing import Callable     # allows type hinting 'function pointers'

from .exceptions import ConfigError
## import needed pygame modules
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
            cf_container: dict,
            surface: Surface,
            position: tuple[int, int],
            size: tuple[int, int],
            child_align: str,
            child_flow: str,
        ):
        Sprite.__init__(self)

        self.size = size
        self.position = position
        self.child_flow = child_flow
        self.child_align = child_align
        
        # store dict settings
        self.color = Color(cf_container['color'])
        self.border_width = int(cf_container['border_width'])
        self.border_color = Color(cf_container['border_color'])
        self.child_padding = int(cf_container['children_padding'])
        self.separator_width = int(cf_container['separator_width'])
        self.separator_color = Color(cf_container['separator_color'])
        
        # calculate the correct padding for separator
        self.separator_padding = int((self.child_padding/2) + self.separator_width/2)
        self.draw_separator = False
        self.children = Group()
        ''' group of sprites that depend on the container for updates/positioning '''

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
        self._set_internal_references()

    def _set_internal_references(self):
        ''' sets internally used references based on configuration
            * self.ALIGN_FUNC refers to one of the internal 'self.align_to_<...>' methods
            * self.DRAW_FUNC is one of the different '_draw_<...>_separator' methods
            * self.POSITION_FUNC is one of the different '_position...' methods
            * also sets self.ALIGN_PARENT, a rect used by the first child for each positioning

            by using references we only have to perform checks once, 
            as opposed to on __every single__ update. This amounts to a huge performance gain,
            considering the update function is called <FPS> times per second, on every single child
            
            E.g., if we have 6 textboxes at 125 frames per sec, that would amount to a combined
            125*6*3 = 2250 checks per SECOND, or 135000 checks every minute.
        '''

        match (self.child_align):
            case 'left':
                self.ALIGN_FUNC = self._align_to_left_of
            case 'right':
                self.ALIGN_FUNC = self._align_to_right_of
            case 'top':
                self.ALIGN_FUNC = self._align_to_top_of
            case 'bottom':
                self.ALIGN_FUNC = self._align_to_bottom_of
            case 'bottomleft':
                self.ALIGN_FUNC = self._align_to_topleft_of
            case 'topleft':
                self.ALIGN_FUNC = self._align_to_bottomleft_of
            case _:
                raise ValueError(f'\
                    children_align expected: "top", "bottom",\
                    "left", "right", "bottomleft" or "topleft".\n\
                    Found "{self.child_align}"')

        match (self.child_flow):
            case 'top_bottom':
                # align-parent for positioning the first child
                # the next children will have the previous child as reference
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
                    Found: {self.child_flow}')

        # set position func to either just position, or position and draw a line
        if (self.separator_width > 0):
            self.POSITION_FUNC = self._position_children_and_draw
            self.child_padding += self.separator_width
        else:
            self.POSITION_FUNC = self._position_children

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

    def _set_align_func(self, child_align: str) -> Callable[[Rect, Rect], None]:
        ''' get the correct alignment function for positioning children '''
        # additional positioning functions can easily be added
        match (child_align):
            case 'left':
                self.ALIGN_FUNC = self._align_to_left_of
            case 'right':
                self.ALIGN_FUNC = self._align_to_right_of
            case 'top':
                self.ALIGN_FUNC = self._align_to_top_of
            case 'bottom':
                self.ALIGN_FUNC = self._align_to_bottom_of
            case 'bottomleft':
                self.ALIGN_FUNC = self._align_to_topleft_of
            case 'topleft':
                self.ALIGN_FUNC = self._align_to_bottomleft_of
            case _:
                raise ValueError(f'\
                    children_align expected: "top", "bottom",\
                    "left", "right", "bottomleft" or "topleft".\n\
                    Found "{child_align}"')

    def _position_children(self):
        ''' positions children according to the align_func '''
        parent = self.ALIGN_PARENT
        for child in self.children:
            RE = child.rect
            self.ALIGN_FUNC(RE, parent)
            parent = RE

    def _position_children_and_draw(self):
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

    def check_child_rect_fits(self, child):
        ''' simple check for verifying that child can fit inside this container '''
        if ((child.rect.h > self.rect.h) or (child.rect.w > self.rect.w)):
            msg = "[Container][check_child_rect_fits][WARNING]"
            msg += f':Child does not fit: {child}'
            msg += f'[Container]: {self}\n'
            msg += "to make child fit, perform one or several of the following actions:\n"
            msg += " -> reduce the font size in the set textbox config\n"
            msg += " -> reduce the length of the text given to the text box\n"
            msg += " -> increase the size of the container\n"
            msg += " -> change the font type used by the textbox\n"
            print(msg)

    def create_textbox_child(self, cf_textbox: dict, ref_id, text: str, text_getter_func: Callable | None):
        ''' creates a new child. ref_id may be any reference, or None
            * children may share references
            * adds the child to self.children
            * returns the child
        '''
        NEW_CHILD = Child_Text_Box(cf_textbox, ref_id, text, text_getter_func)
        self.check_child_rect_fits(NEW_CHILD)
        self.children.add(NEW_CHILD)
        return NEW_CHILD

    def get_children_by_ref(self, ref_id):
        ''' get child by its ref_id. Accepts ref_id = None.
            * returns a list of children with the given ref_id
        '''
        matching_children = []
        for child in self.children:
            if (child.ref_id == ref_id):
                matching_children.append(child)
        return matching_children

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
        # re-blit the background surface to clear any past blits
        self.SURF.blit(self.image, self.rect)

        # call update on all children
        self.children.update()

        # call the set position function for children
        self.POSITION_FUNC()

        # draw children
        self.children.draw(self.SURF)

    def __str__(self):
        msg = f'[Container with n={self.get_num_children()} children.\n'
        msg += f'position(x,y)={self.position}, height={self.rect.h}, width={self.rect.w},\n'
        msg += f'child_flow="{self.child_flow}", child_align="{self.child_align}"]'


class Child_Text_Box(Sprite):
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
            cf_textbox: dict,
            ref_id,
            text: str,
            text_getter_func: Callable | None,
        ):

        Sprite.__init__(self)
        self.ref_id = ref_id
        self.text = text
        self.text_getter_func = text_getter_func

        # store config settings
        self.bg_color = Color(cf_textbox['text_bg_color'])
        self.font_path = str(cf_textbox['font_path'])
        self.font_size = int(cf_textbox['font_size'])
        self.font_color = Color(cf_textbox['font_color'])
        self.font_antialas: bool = cf_textbox['font_antialias']

        # load font
        self.font = Font(self.font_path, self.font_size)
        self.old_text = text

        # load the font, then render the text and create rect
        self.image = self.font.render(
            self.text,
            self.font_antialas,
            self.font_color,
            self.bg_color
        )
        self.rect = self.image.get_rect()

        self._set_internal_update_func()

    def _set_internal_update_func(self):
        ''' all textboxes have a update func, regardless of text_getter_func/not '''
        # allows for for a simple, generalized update func
        if (self.text_getter_func):
            self.render_on_update = True
            if (self.text == ''):
                self.text_update_func = self._get_text_from_getter_func
            else:
                self.pre_text = self.text
                self.text_update_func = self._get_text_from_getter_func_with_pre_text
        else:
            self.render_on_update = False
            # default to just returning own text
            self.text_update_func = self.get_text

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
        ''' function to add or replace pre-text for textboxes with a getter_func.
            * does nothing if textbox does not have a getter_func
        '''
        self.pre_text = text
        if not self.text_getter_func:
            self.text = f'{self.pre_text}{self.text}'

    def set_text(self, text: str):
        ''' for manual replacement of text. Re-renders image to the text.
            * if this is called and a getter exists, it will prevent future updates from the getter
            * call resume_text_getter to resume rendering through the getter
        '''
        self.text = text
        self.update_text_render()
        self.render_on_update = False

    def resume_text_getter(self):
        ''' if a textbox with a getter_func has been overwritten through set_text, call this to resume
            updating through the getter instead
        '''
        if (self.text_getter_func):
            self.render_on_update = True

    def update_text_render(self):
        ''' replaces self.image with a text render of the self.content text. Updates self.rect '''
        self.image = self.font.render(
            self.text,
            self.font_antialas,
            self.font_color,
            None
        )
        self.rect = self.image.get_rect()

    def update(self):
        ''' update rendering if text has changed '''

        if self.render_on_update:
            # get updated text from one of the internal methods
            # this will either be through a getter func, or if self.text has been
            # manually changed since the last frame
            TEXT = self.text_update_func()

            # if new text is not the same as the last, replace and re-render
            # rendering is very expensive in pygame, so the strcmp is absolutely worth it
            if (TEXT != self.text):
                self.text = TEXT
                self.update_text_render()

    def __str__(self):
        msg = f'[Child_Text_Box with text="{self.pre_text}{self.text}", '
        msg += f'height={self.rect.h}, width={self.rect.w}]'
        return msg
