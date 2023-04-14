from typing import Callable

## import needed pygame modules
from pygame import Color, Surface, SRCALPHA, Rect
from pygame.image import load as image_load
from pygame.transform import scale as transform_scale
from pygame.sprite import Sprite
from pygame.draw import rect as draw_rect

from .PG_ui_text_box import UI_Text_Box


class UI_Button(Sprite):
    ''' functions like a container in the sense that it should not be drawn, rather just updated.
        * -> put in a container wrapper if containing the button
        * image_padding_x / y can be adjusted if image looks warped.
        * will not blit the given image outside of the button surface
    
        ---
        Accessable initialized attributes without parameters:
        ---

        self.allow_trigger = True
         Set to anything other than True to block the button trigger/onclick
         Can be useful for buttons that require special conditions to execute.

        self.toggle_state_duration = 0
         how many updates to to apply the toggle visual for, after it is applied.
         0 => never untoggle automatically
         None => do not ever apply the toggle visual

        self.toggle_state_active = False
         whether or not the button is currently toggled.
            if allow_trigger is False, this will never automatically change.
            else, this is set to true when triggered.

    '''
    def __init__(self,
            cf_button: dict,
            cf_global: dict,
            ref_id,
            size: tuple[int, int],
            position: tuple,
            trigger_func: Callable,
            trigger_parameter,
            hover_state_bool_func: Callable,
            tooltip_text: str | None
        ):
        Sprite.__init__(self)

        if (tooltip_text):
            self.tooltip_text = tooltip_text

        self.cf_global = cf_global
        self.cf_button = cf_button
        self.hover_state_bool_func = hover_state_bool_func
        self.position = position
        self.ref_id = ref_id
        self.trigger_func = trigger_func
        self.trigger_parameter = trigger_parameter
        self.size = size

        self.allow_trigger = True
        ''' set to True at default. Not internally enforced.
        '''

        self.toggle_state_duration = 0
        ''' how many updates to to apply the toggle visual for, after it is applied.
            0 => forever
            None => never
        '''

        self.toggle_state_remaining_updates: int | None = None
        ''' internally used to deactivate toggle, if toggle_state_duration > 0 when triggered '''

        self.toggle_state_active = False
        ''' whether or not the button is currently toggled. False at default.
            Set to true when button triggered.
        '''

        self.rect = Rect(self.position, self.size)
        ''' This rect looks like it could be ommitted at a glance, but is actually
            a convenient way to externally reposition the button, regardless of its current state.
        '''
        
        self.set_up_surfaces()

    def set_up_surfaces(self):
        cf_default = self.cf_button['default']
        cf_hovering = self.cf_button['hovering']
        cf_toggled = self.cf_button['toggled']

        self.bg_color = self.col_or_none(cf_default['color'])
        self.border_color = self.col_or_none(cf_default['border_color'])
        self.border_width = self.int_or_none(cf_default['border_width'])

        self.hover_bg_color = self.col_or_none(cf_hovering['color'])
        self.hover_border_color = self.col_or_none(cf_hovering['border_color'])
        self.hover_border_width = self.int_or_none(cf_hovering['border_width'])

        self.toggle_bg_color = self.col_or_none(cf_toggled['color'])
        self.toggle_border_color = self.col_or_none(cf_toggled['border_color'])
        self.toggle_border_width = self.int_or_none(cf_toggled['border_width'])

        self.bg_surf = Surface(self.size, flags=SRCALPHA)
        self.hover_bg_surf = Surface(self.size, flags=SRCALPHA)
        self.toggle_bg_surf = Surface(self.size, flags=SRCALPHA)

        # in case of no color or transparent fill color
        self.bg_surf.fill(Color(0,0,0,0))
        self.hover_bg_surf.fill(Color(0,0,0,0))
        self.toggle_bg_surf.fill(Color(0,0,0,0))

        # fill backgrounds and draw borders for the surfaces
        if (self.bg_color):
            self.bg_surf.fill(self.bg_color)
        if (self.border_width):
            draw_rect(self.bg_surf, self.border_color, self.bg_surf.get_rect(), width=self.border_width)

        if (self.hover_bg_color):
            self.hover_bg_surf.fill(self.hover_bg_color)
        if (self.hover_border_width):
            draw_rect(self.hover_bg_surf, self.hover_border_color, self.hover_bg_surf.get_rect(), width=self.hover_border_width)

        if (self.toggle_bg_color):
            self.toggle_bg_surf.fill(self.toggle_bg_color)
        if (self.toggle_border_width):
            draw_rect(self.toggle_bg_surf, self.toggle_border_color, self.toggle_bg_surf.get_rect(), width=self.toggle_border_width)

        self.bg_rect = self.bg_surf.get_rect(topleft=self.position)
        self.hover_bg_rect = self.hover_bg_surf.get_rect(topleft=self.position)
        self.toggle_bg_rect = self.toggle_bg_surf.get_rect(topleft=self.position)

    def int_or_none(self, cf_val):
        if (cf_val != None) and (cf_val != 0):
            return int(cf_val)
        return None

    def col_or_none(self, cf_val):
        if (cf_val != None):
            return Color(cf_val)
        return None

    def trigger(self):
        ''' typically an onclick function to be executed externally '''
        self.toggle_state_active = True

        if (self.toggle_state_duration != 0):
            if (self.toggle_state_duration == None):
                self.toggle_state_active = False
            else:
                self.toggle_state_remaining_updates = self.toggle_state_duration

        if (self.trigger_parameter != None):
            self.trigger_func(self.trigger_parameter)
        else:
            self.trigger_func()

    def update_default(self, surface: Surface):
        surface.blit(self.bg_surf, self.rect)

    def update_hovering(self, surface: Surface):
        surface.blit(self.hover_bg_surf, self.rect)

    def update_toggled(self, surface: Surface):
        surface.blit(self.toggle_bg_surf, self.rect)
        self.hover_state_bool_func(self)

        if (self.toggle_state_remaining_updates != None):
            self.toggle_state_remaining_updates -= 1
            if (self.toggle_state_remaining_updates == 0):
                self.toggle_state_active = False
                self.toggle_state_remaining_updates = None

    def update(self, surface: Surface):
        if (self.toggle_state_active):
            self.update_toggled(surface)
        elif (self.hover_state_bool_func(self)):
            self.update_hovering(surface)
        else:
            self.update_default(surface)


class UI_Image_Button(UI_Button):
    def __init__(self,
            cf_button: dict,
            cf_global: dict,
            ref_id,
            size: tuple[int, int],
            position: tuple,
            trigger_func: Callable,
            trigger_parameter,
            hover_state_bool_func: Callable,
            tooltip_text: str | None,
            image_path: str,
            image_padding_x: int,
            image_padding_y: int,
        ):
        super().__init__(cf_button, cf_global, ref_id, size, position, trigger_func, trigger_parameter,
                         hover_state_bool_func, tooltip_text)

        # load the image
        IMG_SURF = image_load(image_path).convert_alpha()

        # scale image to the button surface
        scaled_rect = self.bg_rect.inflate(-int(2 * image_padding_x), -int(2 * image_padding_y))
        SCALED_IMG = transform_scale(IMG_SURF, (scaled_rect.w, scaled_rect.h))

        # blit onto the surfaces created by super
        blit_pos = (image_padding_x, image_padding_y)
        self.bg_surf.blit(SCALED_IMG, blit_pos)
        self.hover_bg_surf.blit(SCALED_IMG, blit_pos)
        self.toggle_bg_surf.blit(SCALED_IMG, blit_pos)


class UI_Text_Button(UI_Button):
    ''' functions like a container in the sense that it should not be drawn, rather just updated.
        * -> put in a container wrapper if containing the button
    '''
    def __init__(self,
            cf_button: dict,
            cf_global: dict,
            ref_id,
            size: tuple[int, int],
            position: tuple,
            trigger_func: Callable,
            trigger_parameter,
            hover_state_bool_func: Callable,
            tooltip_text: str | None,
            cf_fonts: dict,
            text: str,
            text_getter_func: Callable | None,
            text_getter_param
        ):
        super().__init__(cf_button, cf_global, ref_id, size, position, trigger_func, trigger_parameter,
                         hover_state_bool_func, tooltip_text)

        # create text boxes to hold and/or update the given text
        self.text_box = UI_Text_Box(cf_fonts['default'], cf_global, ref_id, text, text_getter_func, text_getter_param, position)
        self.hover_text_box = UI_Text_Box(cf_fonts['hovering'], cf_global, ref_id, text, text_getter_func, text_getter_param, position)
        self.toggle_text_box = UI_Text_Box(cf_fonts['toggled'], cf_global, ref_id, text, text_getter_func, text_getter_param, position)

    def update(self, surface: Surface):
        # call the alt state decider. if true, use alt color. if not, regular.

        if (self.toggle_state_active):
            self.update_toggled(surface)
            self.toggle_text_box.update()
            self.text_render = self.toggle_text_box.image
            self.text_rect = self.toggle_text_box.image.get_rect(center=self.rect.center)
        elif (self.hover_state_bool_func(self)):
            self.update_hovering(surface)
            self.hover_text_box.update()
            self.text_render = self.hover_text_box.image
            self.text_rect = self.hover_text_box.image.get_rect(center=self.rect.center)
        else:
            self.update_default(surface)
            self.text_box.update()
            self.text_render = self.text_box.image
            self.text_rect = self.text_box.image.get_rect(center=self.rect.center)

        surface.blit(self.text_render, self.text_rect)
