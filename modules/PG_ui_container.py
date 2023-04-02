from typing import Callable

## import needed pygame modules
from pygame import Surface, Rect, Color, SRCALPHA
from pygame.sprite import Sprite, Group
from pygame.draw import rect as draw_rect
from pygame.draw import line as draw_line


class UI_Container(Sprite):
    ''' Sprite serving as a surface container for easy position of child sprites

        * surface is passed to create a subsurface internally
        * children_align expects: "top", "bottom",\
            "left", "right", "bottomleft" or "topleft"
        * child_flow expects: "top_bottom", "left_right"
        * note: combinations like "bottomleft"+"top_bottom" do not exactly look pretty
            (might not even work idk)
        * update() serves as a all-in-one clear, update children and draw children

        The general idea here is creating a framework that is easy to modify and 
        configure to meet any need without having to modify any previous code
    '''

    def __init__(self,
            cf_container: dict,
            position: tuple[int, int],
            size: tuple[int, int],
            child_align: str,
            child_flow: str,
        ):
        Sprite.__init__(self)

        self.cf_container   = cf_container
        self.size           = size
        self.position       = position
        self.child_flow     = child_flow
        self.child_align    = child_align

        # store dict settings
        self.cf_children_styles: dict = cf_container['children_styles']
        self.child_padding    = int(cf_container['children_padding'])

        # create a per pixel alpha surface
        self.ALPHA_COLOR = Color(0,0,0,0)
        self.image = Surface(self.size).convert_alpha()
        self.image.fill(self.ALPHA_COLOR)
        self.rect = self.image.get_rect(topleft=self.position)

        self.children = Group()
        ''' group of sprites that depend on the container for updates/positioning '''
        self._set_internal_references()

    def _set_internal_references(self):
        ''' sets internally used references based on configuration
            * self.ALIGN_FUNC refers to one of the internal 'self.align_to_<...>' methods
            * also sets self.ALIGN_PARENT, a rect used by the first child for each positioning

            by using references we only have to perform checks once, as opposed to on ever single update.
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
            case 'left_right':
                self.ALIGN_PARENT = self.rect.copy()
                self.ALIGN_PARENT.width = 0
            case _:
                raise ValueError(f'\
                    child_flow expected: "top_bottom" or "left_right"\n\
                    Found: {self.child_flow}')

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

    def _position_children(self):
        ''' positions children according to the align_func '''
        parent = self.ALIGN_PARENT
        for child in self.children:
            RE = child.rect
            self.ALIGN_FUNC(RE, parent)
            parent = RE

    #### CALLABLE METHODS ####

    def get_child_cf(self, key: str):
        for _key, val in self.cf_children_styles.items():
            if (str(_key) == key):
                cf_style: dict = val
                return cf_style
        print(f'{self}[get_child_cf_style]: key={key} not in cf_children_styles.')
        return None

    def child_fits_self(self, child: Sprite) -> bool:
        ''' simple check for verifying that child can fit inside this container '''
        if ((child.rect.h > self.rect.h) or (child.rect.w > self.rect.w)):
            print(f'{self}[child_fits_self]: {child} does not fit as a child')
            return False
        return True

    def add_child(self, child: Sprite):
        self.child_fits_self(child)
        self.children.add(child)

    def get_children_by_ref_id(self, ref_id):
        ''' get children by ref_id. 
            * returns a list of children with the given ref_id

            Example usage:
            for child in MY_CONTAINER.get_children_by_ref_id("APP"):
                print(child)
        '''
        matching_children = []
        for child in self.children:
            if type(child.ref_id) == list:
                for elem in child.ref_id:
                    if ref_id == elem:
                        matching_children.append(child)
                        break
            else:
                if ref_id == child.ref_id:
                    matching_children.append(child)

        return matching_children

    def get_children(self) -> list[Sprite]:
        ''' returns a list containing the children sprites '''
        return self.children.sprites()

    def get_n_children(self) -> int:
        ''' returns the current number of children '''
        return len(self.children.sprites())

    def remove_all_children(self) -> int:
        ''' removes all children from self.children '''
        self.children.empty()

    def update(self, surface: Surface):
        ''' update children. position children. '''
        # call update on all children
        self.image.fill(self.ALPHA_COLOR)
        self._position_children()
        surface.blit(self.image, self.position)
        self.children.draw(surface)
        self.children.update()

    def __str__(self):
        msg = f'[{super().__str__()} : '
        msg += f'rect="{self.rect}", n_children={self.get_n_children()}, '
        msg += f'child_flow="{self.child_flow}", child_align="{self.child_align}"]'
        return msg
