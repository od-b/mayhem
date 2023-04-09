## import needed pygame modules
from pygame import Surface, Rect, Color, SRCALPHA
from pygame.sprite import Sprite, Group, GroupSingle
from pygame.draw import rect as draw_rect


class UI_Container(Sprite):
    ''' Surface container. Automatically handles positioning of rects within self.\n
        The general idea here is creating a framework that is easy to modify and 
        configure to meet any need without having to modify this class. 
        ---
        notable parameters
        ---
        child_anchor:
            align-parent for positioning the first child, relative to the inner bounds of self.\n
            the next children will have the previous child as reference.
            expects: str in ["top", "bottom", "left", "right"]

        child_align_x/y:
            determines where children are aligned/positioned, relative to the root and other children
            child_align_x expects one of ["left", "right", "centerx", "container_left", "container_right"]
            child_align_y expects one of ["top", "bottom", "centery", "container_top", "container_bottom"]
        ---
        readme
        ---
        * if inline, the respective padding is only applied to root

        if the container is moved:
            => update the anchor by calling:\n\t\t  .set_anchor_rect(new <child_anchor> | None=self.child_anchor)\n
            i.e., set_anchor_rect(None) will update the position of the anchor, but not its setting
            child_align (internally: self.ALIGN_FUNC_X/Y) is unchanged by this action.
        ---
        the alignment may be changed at any point after container creation:
            => update the alignment setting by calling:\n\t\t  .set_align_func(<child_align>)\n
            child_anchor (internally: self.ANCHOR_RECT) is unchanged by this action.
        ---
        
        * ALL CHILDREN SHOULD HAVE AN ATTRIBUTED 'ref_id'. Can be anything, including None.
            In order to use this classes methods, use a list to contain multiple ref_id's, if iterable
    '''

    def __init__(self,
            position: tuple[int, int],
            size: tuple[int, int],
            child_anchor: str,
            child_anchor_offset_x: int,
            child_anchor_offset_y: int,
            child_align_x: str,
            child_align_y: str,
            child_padding_x: int,
            child_padding_y: int
        ):

        Sprite.__init__(self)
        self.size            = size
        self.position        = position
        self.CHILD_PADDING_X = child_padding_x
        self.CHILD_PADDING_Y = child_padding_y
        self.CHILD_ANCHOR_OFFSET_X = child_anchor_offset_x
        self.CHILD_ANCHOR_OFFSET_Y = child_anchor_offset_y

        self.bg_color = None
        self.border_width = None
        self.border_color = None

        self.rect = Rect((self.position), (self.size))
        self.children = []
        ''' group of children with rects, that depend on the container for updates/positioning '''

        self.set_align_funcs(child_align_x, child_align_y)
        self.set_anchor_rect(child_anchor)

    def _align_x_to_left_of(self, child: Rect, parent: Rect):
        child.right = parent.left + self.CHILD_PADDING_X

    def _align_x_to_centerx_of(self, child: Rect, parent: Rect):
        child.centerx = parent.centerx + self.CHILD_PADDING_X

    def _align_x_to_right_of(self, child: Rect, parent: Rect):
        child.left = parent.right + self.CHILD_PADDING_X

    def _align_x_to_container_left(self, child: Rect, parent: Rect):
        child.left = self.rect.left + self.CHILD_PADDING_X

    def _align_x_to_container_right(self, child: Rect, parent: Rect):
        child.right = self.rect.right + self.CHILD_PADDING_X

    def _align_x_to_container_centerx(self, child: Rect, parent: Rect):
        child.centerx = self.rect.centerx + self.CHILD_PADDING_X

    def _align_y_to_top_of(self, child: Rect, parent: Rect):
        child.bottom = parent.top + self.CHILD_PADDING_Y

    def _align_y_to_centery_of(self, child: Rect, parent: Rect):
        child.centery = parent.centery + self.CHILD_PADDING_Y

    def _align_y_to_bottom_of(self, child: Rect, parent: Rect):
        child.top = parent.bottom + self.CHILD_PADDING_Y

    def _align_y_to_container_top(self, child: Rect, parent: Rect):
        child.top = self.rect.top + self.CHILD_PADDING_Y

    def _align_y_to_container_bottom(self, child: Rect, parent: Rect):
        child.bottom = self.rect.bottom + self.CHILD_PADDING_Y

    def _align_y_to_container_centery(self, child: Rect, parent: Rect):
        child.centery = self.rect.centery + self.CHILD_PADDING_Y

    #### CALLABLE METHODS ####

    def set_align_funcs(self, child_align_x, child_align_y):
        ''' updates the internally used self.ALIGN_FUNC_X & Y '''
        self.child_align_x = child_align_x
        self.child_align_y = child_align_y

        match self.child_align_x:
            case 'left':
                self.ALIGN_FUNC_X = self._align_x_to_left_of
            case 'right':
                self.ALIGN_FUNC_X = self._align_x_to_right_of
            case 'centerx':
                self.ALIGN_FUNC_X = self._align_x_to_centerx_of
            case 'container_left':
                self.ALIGN_FUNC_X = self._align_x_to_container_left
            case 'container_right':
                self.ALIGN_FUNC_X = self._align_x_to_container_right
            case 'container_centerx':
                self.ALIGN_FUNC_X = self._align_x_to_container_centerx
            case _:
                EXPECTED = ["left", "right", "centerx", "container_left", "container_right"]
                raise ValueError(f'child_align_x expected one of [{EXPECTED}]; Found="{self.child_align_x}"')

        match self.child_align_y:
            case 'top':
                self.ALIGN_FUNC_Y = self._align_y_to_top_of
            case 'bottom':
                self.ALIGN_FUNC_Y = self._align_y_to_bottom_of
            case 'centery':
                self.ALIGN_FUNC_Y = self._align_y_to_centery_of
            case 'container_top':
                self.ALIGN_FUNC_Y = self._align_y_to_container_top
            case 'container_bottom':
                self.ALIGN_FUNC_Y = self._align_y_to_container_bottom
            case 'container_centery':
                self.ALIGN_FUNC_Y = self._align_y_to_container_centery
            case _:
                EXPECTED = ["top", "bottom", "centery", "container_top", "container_bottom"]
                raise ValueError(f'child_align_y expected one of [{EXPECTED}]; Found="{self.child_align_y}"')

    def set_anchor_rect(self, new_child_anchor: str | None):
        ''' uses the existing self.child_anchor if new_child_anchor=None '''
        if (new_child_anchor):
            self.child_anchor = new_child_anchor
        # get a copy of self rect, to be used as root, for placing the first child
        self.ANCHOR_RECT = self.rect.copy()
        # set the correct size/pos for the root parent, depending in parameters
        match self.child_anchor:
            case 'top':
                self.ANCHOR_RECT.height = int(0)
                self.ANCHOR_RECT.top = self.rect.top
            case 'bottom':
                self.ANCHOR_RECT.height = int(0)
                self.ANCHOR_RECT.bottom = self.rect.bottom
            case 'left':
                self.ANCHOR_RECT.width = int(0)
                self.ANCHOR_RECT.left = self.rect.left
            case 'right':
                self.ANCHOR_RECT.width = int(0)
                self.ANCHOR_RECT.right = self.rect.right
            case _:
                EXPECTED = ["top", "bottom", "left", "right"]
                raise ValueError(f'self.child_align expected one of [{EXPECTED}]; Found="{self.child_anchor}"')

        self.ANCHOR_RECT.x += self.CHILD_ANCHOR_OFFSET_X
        self.ANCHOR_RECT.y += self.CHILD_ANCHOR_OFFSET_Y

    def get_children_by_ref_id(self, ref_id, child_iter):
        ''' get all children whose ref id / ids is or includes the given ref_id. 
            * None will return children with 'None' in or as their ref id.
            * ref_id can be a list or single reference

            Example usage:
            for child in MY_CONTAINER.get_children_by_ref_id("APP"):
                print(child)
        '''
        matching_children = []
        for child in child_iter:
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

    def get_children_by_ref_id_intersection(self, ref_ids_iterable, child_iter):
        ''' return a list of children that contain ALL the given ref_ids.
            * example usage:
            list = self.BAR_CONTAINER.get_children_by_ref_id_intersection(("BAR", "CORE"))
            for child in list:
                child.kill()
        '''
        matching_children = []
        for child in child_iter:
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

    def update(self):
        ''' positions children according to the align_func '''
        parent = self.ANCHOR_RECT
        for child in self.children:
            RE = child.rect
            self.ALIGN_FUNC_X(RE, parent)
            self.ALIGN_FUNC_Y(RE, parent)
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
    ''' Surface container for children that are sprites. Expanded functionality.
        * self.children is a group for this container.
        * update takes in a surface parameter and draws children onto the surface after positioning.
        * See UI_Container for further info
        '''
    def __init__(self,
            position: tuple[int, int],
            size: tuple[int, int],
            child_anchor: str,
            child_anchor_offset_x: int,
            child_anchor_offset_y: int,
            child_align_x: str,
            child_align_y: str,
            child_padding_x: int,
            child_padding_y: int
        ):
        super().__init__(position, size, child_anchor, child_anchor_offset_x, child_anchor_offset_y,
                         child_align_x, child_align_y, child_padding_x, child_padding_y)

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

    def add_child(self, child: Sprite | list[Sprite]):
        self.children.add(child)

    def add_children_by_ref_id(self, ref_id, child_iterable):
        ''' * if ref_id is a list, adds any child from the list that contains all ref_id's
            * else, adds any child from the list with / containing the given ref id
            * returns all/any matches as a list, after adding to self. (the list may be empty)
        '''

        matching_children: list | Sprite
        if type(ref_id) == list:
            matching_children = self.get_children_by_ref_id_intersection(ref_id, child_iterable)
        else:
            matching_children = self.get_children_by_ref_id(ref_id, child_iterable)

        if (matching_children):
            self.add_child(matching_children)

        return matching_children

    def update(self, surface: Surface):
        ''' update childrens positions. draw children to the given surface '''
        super().update()
        self.children.draw(surface)
        self.children.update()


class UI_Single_Centered_Container(UI_Sprite_Container):
    ''' replaces the sprite group with a GroupSingle, adding a new sprite removes the old
        position defaults to (0, 0) if given None.
        Use exactly like a regular UI_Sprite_Container.
    '''
    def __init__(self,
            position: tuple[int, int] | None,
            size: tuple[int, int],
            child_padding_x: int,
            child_padding_y: int,
            child: Sprite | None,
        ):

        given_pos = position
        if (given_pos == None):
            given_pos = (int(0), int(0))

        super().__init__(
            given_pos, size, "top", 0, 0,
            "container_centerx", "container_centery",
            child_padding_x, child_padding_y
        )

        self.children = GroupSingle()
        if (child):
            self.children.add(child)


class UI_Single_Centered_Container_Filled(UI_Single_Centered_Container):
    def __init__(self,
            position: tuple[int, int] | None,
            size: tuple[int, int],
            child_padding_x: int,
            child_padding_y: int,
            child: Sprite | None,
            bg_color: tuple | Color | None,
            border_color: tuple | Color | None,
            border_width: int | None
        ):
        super().__init__(position, size, child_padding_x, child_padding_y, child)

        if (bg_color):
            self.bg_color = Color(bg_color)
        if (border_width):
            self.border_width = int(border_width)
            self.border_color = Color(border_color)

    def update(self, surface):
        if (self.bg_color):
            draw_rect(surface, self.bg_color, self.rect)
        if (self.border_width):
            draw_rect(surface, self.border_color, self.rect, width=self.border_width)
        super().update()


class UI_Sprite_Container_Filled(UI_Sprite_Container):
    def __init__(self,
            position: tuple[int, int],
            size: tuple[int, int],
            child_anchor: str,
            child_anchor_offset_x: int,
            child_anchor_offset_y: int,
            child_align_x: str,
            child_align_y: str,
            child_padding_x: int,
            child_padding_y: int,
            bg_color,
            border_color,
            border_width
        ):
        super().__init__(position, size, child_anchor, child_anchor_offset_x, child_anchor_offset_y,
                         child_align_x, child_align_y, child_padding_x, child_padding_y)

        self.bg_color = bg_color
        if (self.bg_color != None):
            self.bg_color = Color(self.bg_color)
        self.border_color = border_color
        if (self.border_color != None):
            self.border_color = Color(self.border_color)
        self.border_width = border_width

    def update(self, surface: Surface):
        if (self.bg_color):
            draw_rect(surface, self.bg_color, self.rect)
        if (self.border_width):
            draw_rect(surface, self.border_color, self.rect, width=self.border_width)
        super().update(surface)


class UI_Container_Wrapper(UI_Sprite_Container):
    ''' for containing other containers. do not add non-container sprites.
        * may have UI_Container_Wrapper as child(ren), if so updates all/any subcontainers + their children.
    '''
    def __init__(self,
            position: tuple[int, int],
            size: tuple[int, int],
            child_anchor: str,
            child_anchor_offset_x: int,
            child_anchor_offset_y: int,
            child_align_x: str,
            child_align_y: str,
            child_padding_x: int,
            child_padding_y: int,
            bg_color,
            border_color,
            border_width
        ):
        super().__init__(position, size, child_anchor, child_anchor_offset_x, child_anchor_offset_y,
                         child_align_x, child_align_y, child_padding_x, child_padding_y)

        self.bg_color = bg_color
        if (self.bg_color != None):
            self.bg_color = Color(self.bg_color)
        self.border_color = border_color
        if (self.border_color != None):
            self.border_color = Color(self.border_color)
        self.border_width = border_width

    def update(self, surface: Surface):
        if (self.bg_color):
            draw_rect(surface, self.bg_color, self.rect)
        if (self.border_width):
            draw_rect(surface, self.border_color, self.rect, width=self.border_width)

        parent = self.ANCHOR_RECT
        for child in self.children:
            RE = child.rect
            self.ALIGN_FUNC_X(RE, parent)
            self.ALIGN_FUNC_Y(RE, parent)
            parent = RE

        for container in self.children:
            # if container is a wrapper, reposition anchor rect
            # draw_rect(surface, (255, 255, 255), container.rect)
            if (type(container) == type(self)):
                container.set_anchor_rect(None)
            else:
                draw_rect(surface, (0, 0, 0), container.rect, width=2)
            container.update(surface)
