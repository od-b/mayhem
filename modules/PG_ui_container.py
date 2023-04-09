## import needed pygame modules
from pygame import Surface, Rect, Color, SRCALPHA
from pygame.sprite import Sprite, Group, GroupSingle
from pygame.draw import rect as draw_rect


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
            expects: str in ["top", "left"]

        child_align:
            determines where children are aligned/positioned, relative to the root and other children
            expects: str in ["top", "bottom", "left", "right", "bottomleft", "bottomright", "topleft"]
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
            position: tuple[int, int],
            size: tuple[int, int],
            child_anchor: str,
            child_align: str,
            child_padding: int
        ):

        Sprite.__init__(self)
        self.size           = size
        self.position       = position
        self.CHILD_PADDING  = child_padding

        self.bg_color = None
        self.border_width = None
        self.border_color = None

        # create a per pixel alpha surface
        self.ALPHA_COLOR = Color(0,0,0,0)

        self.rect = Rect((self.position), (self.size))
        self.children = []
        ''' group of children with rects, that depend on the container for updates/positioning '''

        self.set_align_func(child_align)
        self.set_anchor_rect(child_anchor)

    def _align_to_left_of(self, child: Rect, parent: Rect):
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

    def _align_to_bottomright_of(self, child: Rect, parent: Rect):
        child.topright = (parent.bottomright[0], parent.bottomright[1] + self.CHILD_PADDING)

    #### CALLABLE METHODS ####

    def set_align_func(self, child_align):
        ''' updates the internally used self.ALIGN_FUNC '''
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
            case 'topleft':
                self.ALIGN_FUNC = self._align_to_topleft_of
            case 'bottomright':
                self.ALIGN_FUNC = self._align_to_bottomright_of
            case 'bottomleft':
                self.ALIGN_FUNC = self._align_to_bottomleft_of
            case _:
                EXPECTED = ["top", "bottom", "left", "right", "bottomleft", "bottomright", "topleft"]
                raise ValueError(f'self.child_align expected=[{EXPECTED}]; Found="{self.child_align}"')

    def set_anchor_rect(self, new_child_anchor: str | None):
        ''' uses the existing self.child_anchor if new_child_anchor=None '''
        if (new_child_anchor):
            self.child_anchor = new_child_anchor
        # get a copy of self rect, to be used as root, for placing the first child
        self.ANCHOR_RECT = self.rect.copy()
        # set the correct size/pos for the root parent, depending in parameters
        match self.child_anchor:
            case 'top':
                self.ANCHOR_RECT.height = 0
            case 'left':
                self.ANCHOR_RECT.width = 0
            case _:
                EXPECTED = ["top", "left"]
                raise ValueError(f'self.child_align expected=[{EXPECTED}]; Found="{self.child_anchor}"')

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
    ''' Surface container for children that are sprites. Expanded functionality.
        * self.children is a group for this container.
        * update takes in a surface parameter and draws children onto the surface after positioning.
        * See UI_Container for further info
        '''
    def __init__(self,
            position: tuple[int, int],
            size: tuple[int, int],
            child_anchor: str,
            child_align: str,
            child_padding: int
        ):
        super().__init__(position, size, child_anchor, child_align, child_padding)
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


class UI_Sprite_Container_Filled(UI_Sprite_Container):
    def __init__(self,
            position: tuple[int, int],
            size: tuple[int, int],
            child_anchor: str,
            child_align: str,
            child_padding: int,
            bg_color,
            border_color,
            border_width
        ):
        super().__init__(position, size, child_anchor, child_align, child_padding)

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
    def __init__(self,
            position: tuple[int, int],
            size: tuple[int, int],
            child_anchor: str,
            child_align: str,
            child_padding: int,
            bg_color,
            border_color,
            border_width
        ):
        super().__init__(position, size, child_anchor, child_align, child_padding)

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
            self.ALIGN_FUNC(RE, parent)
            parent = RE

        for container in self.children:
            draw_rect(surface, (255,255,255), container.rect)
            draw_rect(surface, (0, 0, 0), container.rect, width=2)
            # if container is a wrapper, reposition anchor rect
            if (type(container) == type(self)):
                container.set_anchor_rect(None)
            container.update(surface)


# for container in reposition:
#     parent = container.ANCHOR_RECT
#     for child in container.children:
#         RE = child.rect
#         container.ALIGN_FUNC(RE, parent)
#         parent = RE
#     container.update(surface)


#### single containers ####

class UI_Container_Single(Sprite):
    ''' container for only one child 
        * child_position_x: str in ["left", "centerx", "right"]
        * child_position_y: str in ["top", "centery", "bottom"]
    '''
    def __init__(self,
            position: tuple[int, int],
            size: tuple[int, int],
            ref_id,
            child_position_x: str,
            child_position_y: str,
            child_padding_x: int,
            child_padding_y: int,
            child: Sprite,
        ):
        Sprite.__init__(self)

        self.position = position
        self.size = size
        self.ref_id = ref_id
        self.child_padding_x = child_padding_x
        self.child_padding_y = child_padding_y

        self.bg_color = None
        self.border_width = None
        self.border_color = None

        self.child = child
        self.children = GroupSingle(child)

        self.rect = Rect((self.position), (self.size))
        self.set_position_funcs(child_position_x, child_position_y)

    def _position_x_left(self, child: Rect):
        child.left = self.rect.left + self.child_padding_x

    def _position_x_center(self, child: Rect):
        child.centerx = self.rect.centerx + self.child_padding_x

    def _position_x_right(self, child: Rect):
        child.right = self.rect.right - self.child_padding_x

    def _position_y_top(self, child: Rect):
        child.top = self.rect.top + self.child_padding_y

    def _position_y_center(self, child: Rect):
        child.centery = self.rect.centery + self.child_padding_y

    def _position_y_bottom(self, child: Rect):
        child.bottom = self.rect.bottom - self.child_padding_y

    def set_position_funcs(self, child_position_x, child_position_y):
        ''' updates the internally used self.POS_FUNC_X '''
        self.child_position_x = child_position_x
        self.child_position_y = child_position_y

        # set the correct align_func for children in self
        match self.child_position_x:
            case 'left':
                self.POS_FUNC_X = self._position_x_left
            case 'centerx':
                self.POS_FUNC_X = self._position_x_center
            case 'right':
                self.POS_FUNC_X = self._position_x_right
            case _:
                EXPECTED = ["left", "centerx",  "right"]
                raise ValueError(f'child_position_x expected=[{EXPECTED}]; Found="{self.child_position_x}"')

        match self.child_position_y:
            case 'top':
                self.POS_FUNC_Y = self._position_y_top
            case 'centery':
                self.POS_FUNC_Y = self._position_y_center
            case 'bottom':
                self.POS_FUNC_Y = self._position_y_bottom
            case _:
                EXPECTED = ["left", "centery", "right"]
                raise ValueError(f'child_position_y expected=[{EXPECTED}]; Found="{self.child_position_y}"')

    def add_child(self, child: Sprite):
        ''' will replace the current child, if any '''
        self.child = child
        self.children.add(child)

    def update(self, surface: Surface):
        self.children.update()
        self.POS_FUNC_X(self.child.rect)
        self.POS_FUNC_Y(self.child.rect)
        self.children.draw(surface)


class UI_Container_Single_Filled(UI_Container_Single):
    def __init__(self,
            position: tuple[int, int],
            size: tuple[int, int],
            ref_id,
            child_position_y: str,
            child_position_x: str,
            child_padding_x: int,
            child_padding_y: int,
            children: list[Sprite] | None,
            active_child_index: int | None,
            bg_color,
            border_color,
            border_width
        ):
        super().__init__(
            position, size, ref_id, child_position_y, child_position_x,
            child_padding_x, child_padding_y, children, active_child_index
        )

        self.bg_color = bg_color
        self.border_color = border_color
        self.border_width = border_width

    def update(self, surface: Surface):
        ''' draw bg//border update childrens positions. draw children to the given surface '''
        draw_rect(surface, self.bg_color, self.rect)
        if (self.border_width):
            draw_rect(surface, self.border_color, self.rect, width=self.border_width)
        super().update(surface)
