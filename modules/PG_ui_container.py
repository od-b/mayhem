## import needed pygame modules
from pygame import Surface, Rect, Color
from pygame.sprite import Sprite, Group



class UI_Container(Sprite):
    ''' Surface container. Automatically handles positioning of rects within self.\n
        The general idea here is creating a framework that is easy to modify and 
        configure to meet any need without having to modify this class. 
        ---
        parameters
        ---
        child_anchor:
            align-parent for positioning the first child, relative to the inner bounds of self.\n
            the next children will have the previous child as reference.
            expects: str in ["top_centerx", "left_centery"]

        child_align:
            determines where children are aligned/positioned, relative to the root and other children
            expects: str in ["top", "bottom", "left", "right", "bottomleft", "topleft"]
        ---
        readme
        ---
        if the container is moved:
            => update the anchor by calling:\n\t\t  .set_anchor_rect(new <child_anchor> | None=self.child_anchor)\n
            i.e., set_anchor_rect(None) will update the position of the anchor, but not its setting
            child_align (internally: self.ALIGN_FUNC) is unchanged by this action.
        ---
        the alignment may be changed at any point after container creation:
            => update the alignment setting by calling:\n\t\t  .set_align_func(<child_align>)\n
            child_anchor (internally: self.ANCHOR_RECT) is unchanged by this action.
        ---
        
        * ALL CHILDREN SHOULD HAVE AN ATTRIBUTED 'ref_id'. Can be anything, including None.
            In order to use this classes methods, use a list to contain multiple ref_id's, if iterable
    '''

    def __init__(self,
            cf_container: dict,
            position: tuple[int, int] | None,
            size: tuple[int, int] | None,
            child_anchor: str,
            child_align: str
        ):

        Sprite.__init__(self)
        self.cf_container   = cf_container
        self.size           = size
        self.position       = position
        self.CHILD_PADDING  = int(cf_container['child_padding'])

        # store dict settings
        
        if (self.position == None):
            self.position = (int(0), int(0))
        if (self.size == None):
            self.size = cf_container['size']

        # create a per pixel alpha surface
        self.ALPHA_COLOR = Color(0,0,0,0)
        self.image = Surface(self.size).convert_alpha()
        self.image.fill(self.ALPHA_COLOR)
        self.rect = self.image.get_rect(topleft=self.position)
        self.children = []
        ''' group of children with rects, that depend on the container for updates/positioning '''

        self.set_align_func(child_align)
        self.set_anchor_rect(child_anchor)

    def set_align_func(self, child_align):
        self.child_align = child_align
        # set the correct align_func for children in self
        match self.child_align:
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
                EXPECTED = ["top", "bottom", "left", "right", "bottomleft", "topleft"]
                raise ValueError(f'self.child_align expected=[{EXPECTED}]; Found="{self.child_align}"')

    def set_anchor_rect(self, child_anchor):
        self.child_anchor = child_anchor
        # get a copy of self rect, to be used as root, for placing the first child
        self.ANCHOR_RECT = self.rect.copy()
        # set the correct size/pos for the root parent, depending in parameters
        match self.child_anchor:
            case 'top_centerx':
                self.ANCHOR_RECT.height = 0
            case 'left_centery':
                self.ANCHOR_RECT.width = 0
            case _:
                EXPECTED = ["top_centerx", "left_centery"]
                raise ValueError(f'self.child_align expected=[{EXPECTED}]; Found="{self.child_anchor}"')

    def _align_to_left_of(self, child: Rect, parent: Rect):
        # move_ip()
        child.right = (parent.left - self.CHILD_PADDING)
        child.centery = parent.centery

    def _align_to_right_of(self, child: Rect, parent: Rect):
        child.left = (parent.right + self.CHILD_PADDING)
        child.centery = parent.centery

    def _align_to_top_of(self, child: Rect, parent: Rect):
        child.bottom = (parent.top - self.CHILD_PADDING)
        child.centerx = parent.centerx

    def _align_to_bottom_of(self, child: Rect, parent: Rect):
        child.top = (parent.bottom + self.CHILD_PADDING)
        child.centerx = parent.centerx

    def _align_to_topleft_of(self, child: Rect, parent: Rect):
        child.bottomleft = (parent.topleft[0], parent.topleft[1] - self.CHILD_PADDING)

    def _align_to_bottomleft_of(self, child: Rect, parent: Rect):
        child.topleft = (parent.bottomleft[0], parent.bottomleft[1] + self.CHILD_PADDING)

    #### CALLABLE METHODS ####

    def get_children_by_ref_id(self, ref_id):
        ''' get all children whose ref id / ids is or includes the given ref_id. 
            * None will return children with 'None' in or as their ref id.

            Example usage:
            for child in MY_CONTAINER.get_children_by_ref_id("APP"):
                print(child)
        '''
        matching_children = []
        for child in self.children:
            # check if child has multiple ref id's
            if (type(child.ref_id) == list):
                for elem in child.ref_id:
                    if ref_id == elem:
                        matching_children.append(child)
                        # if a child matches, break so we don't add it twice.
                        break
            else:
                # there's only one ref_id. check if it matches
                if ref_id == child.ref_id:
                    matching_children.append(child)

        return matching_children

    def get_children_by_ref_id_intersection(self, ref_ids_iterable):
        ''' return a list of children that contain ALL the given ref_ids.
            * example usage:
            list = self.BAR_CONTAINER.get_children_by_ref_id_intersection(("BAR", "CORE"))
            for child in list:
                child.kill()
        '''
        matching_children = []
        for child in self.children:
            if (type(child.ref_id) == list):
                # check if list contains all items
                if all(ref_id in child.ref_id for ref_id in ref_ids_iterable):
                    matching_children.append(child)

        return matching_children

    def child_fits_self(self, child: Sprite) -> bool:
        ''' simple check for verifying that child can fit inside this container '''
        if ((child.rect.h > self.rect.h) or (child.rect.w > self.rect.w)):
            print(f'{self}[child_fits_self]: {child} does not fit as a child')
            return False
        return True

    def get_n_children(self) -> int:
        ''' returns the current number of children '''
        return len(self.children)

    def get_children(self) -> list[Sprite]:
        return self.children

    def kill_all_children(self) -> int:
        self.children = []

    def kill_children_by_ref_id(self, ref_id):
        kill_list = self.get_children_by_ref_id(ref_id)
        for child in kill_list:
            self.children.remove(child)

    def add_child(self, child):
        self.child_fits_self(child)
        self.children.append(child)

    def add_children(self, child_list: list):
        for elem in child_list:
            self.add_child(elem)

    def update(self):
        ''' positions children according to the align_func '''
        parent = self.ANCHOR_RECT
        for child in self.children:
            RE = child.rect
            self.ALIGN_FUNC(RE, parent)
            parent = RE

    def __str__(self):
        msg = f'[{super().__str__()} : Rect="{self.rect}", '
        msg += f'child_anchor="{self.child_anchor}", child_align="{self.child_align}"]. Children:\n'
        i = 0
        for child in self.children:
            msg += f'child #{i} = [{child}]\n'
            i += 1
        if (i == 0):
            msg += "<no children>"
        return msg


class UI_Sprite_Container(UI_Container):
    ''' see UI_Container. For this container, children is a group instead of a list. '''
    def __init__(self,
            cf_container: dict,
            position: tuple[int, int] | None,
            size: tuple[int, int] | None,
            child_anchor: str,
            child_align: str
        ):
        super().__init__(cf_container, position, size, child_anchor, child_align)
        self.children = Group()

    def get_children(self) -> list[Sprite]:
        ''' returns a list containing the children sprites '''
        return self.children.sprites()

    def kill_all_children(self) -> int:
        ''' removes all children from self.children '''
        self.children.empty()

    def kill_children_by_ref_id(self, ref_id):
        ''' kills any/all children whose ref_id is or includes the given ref_id '''
        kill_list = self.get_children_by_ref_id(ref_id)
        for child in kill_list:
            child.kill()

    def add_child(self, child):
        self.child_fits_self(child)
        self.children.add(child)

    def add_children(self, list: list[Sprite]):
        for elem in list:
            self.add_child(elem)

    def update(self, surface: Surface):
        ''' update childrens positions. draw children to the given surface '''
        # call update on all children
        # self.image.fill(self.ALPHA_COLOR)
        super().update()
        surface.blit(self.image, self.position)
        self.children.draw(surface)
        self.children.update()
