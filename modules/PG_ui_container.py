from typing import Callable

## import needed pygame modules
from pygame import Surface, Rect, Color, SRCALPHA
from pygame.sprite import Sprite, Group
from pygame.draw import rect as draw_rect
from pygame.draw import line as draw_line
from .PG_text_box import Text_Box


class UI_Container(Sprite):
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
        
        * Containers use the same type of config for all their equally typed children.
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
        self.cf_children_styles = cf_container['children_styles']

        # store dict settings
        self.color = Color(cf_container['color'])
        ''' bg color '''
        self.border_width = int(cf_container['border_width'])
        self.border_color = Color(cf_container['border_color'])
        self.bg_alpha_key      = int(cf_container['bg_alpha_key'])
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

        if (self.bg_alpha_key < 255):
            # convert color to rgba
            COLOR_TO_ALPHA = (self.color.r, self.color.g, self.color.b, self.bg_alpha_key)
            self.color = Color(COLOR_TO_ALPHA)

            # create a per pixel alpha surface
            self.image = Surface(self.size, flags=SRCALPHA)
        else:
            self.bg_alpha_key = None
            # create a regular surface
            self.image = Surface(self.size).convert()

        # create the border of the container as a rect
        self.rect = self.image.get_rect()
        self.image.fill(self.color)

        if (self.border_width > 0):
            draw_rect(self.image, self.border_color, self.rect, width=self.border_width)

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

    def create_textbox_child(self, ref_id, text: str, text_getter_func: Callable | None):
        ''' creates a new textbox as a child of self. ref_id may be any reference, or None
            * children may share references
            * adds the child to self.children
            * returns the child (in case a reference is needed)
        '''
        NEW_CHILD = Text_Box(
            self.cf_children_styles['text_box'],
            ref_id,
            text,
            text_getter_func,
            self.rect.topleft
        )
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
        # if (self.bg_alpha_key):
        #     self.SURF.fill
        # else:
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

