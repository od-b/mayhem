from typing import Callable

## import needed pygame modules
from pygame import Color, Surface, SRCALPHA
from pygame.font import Font
from pygame.sprite import Sprite
from pygame.draw import rect as draw_rect

from .PG_ui_text_box import UI_Text_Box

class UI_Button(Sprite):
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
            has_toggle: bool
        ):
        Sprite.__init__(self)

        if (tooltip_text):
            self.tooltip_text = tooltip_text

        self.hover_state_bool_func = hover_state_bool_func
        self.position = position
        self.has_toggle = has_toggle
        self.ref_id = ref_id
        self.trigger_func = trigger_func
        self.trigger_parameter = trigger_parameter
        self.size = size

        self.image = Surface(self.size, flags=SRCALPHA)
        self.rect = self.image.get_rect(topleft=self.position)
        self.click_state_active = False
        

    def int_or_none(self, cf_val):
        if (cf_val != None) and (cf_val != 0):
            return int(cf_val)
        return None

    def col_or_none(self, cf_val):
        if (cf_val != None):
            return Color(cf_val)
        return None

    def trigger(self):
        self.click_state_active = True
        if (self.trigger_parameter != None):
            self.trigger_func(self.trigger_parameter)
        else:
            self.trigger_func()


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
            has_toggle: bool,
            text: str,
            text_getter_func: Callable | None,
        ):
        super().__init__(cf_button, cf_global, ref_id, size, position, trigger_func, trigger_parameter,
                         hover_state_bool_func, tooltip_text, has_toggle)

        cf_default = cf_button['default']
        cf_hovering = cf_button['hovering']
        cf_clicked = cf_button['clicked']

        self.text_box = UI_Text_Box(cf_default['font'], cf_global, ref_id, text, text_getter_func, ref_id, position)
        self.hover_text_box = UI_Text_Box(cf_hovering['font'], cf_global, ref_id, text, text_getter_func, ref_id, position)
        self.click_text_box = UI_Text_Box(cf_clicked['font'], cf_global, ref_id, text, text_getter_func, ref_id, position)

        self.bg_color = self.col_or_none(cf_default['bg']['color'])
        self.border_color = self.col_or_none(cf_default['bg']['border_color'])
        self.border_width = self.int_or_none(cf_default['bg']['border_width'])

        self.hover_bg_color = self.col_or_none(cf_hovering['bg']['color'])
        self.hover_border_color = self.col_or_none(cf_hovering['bg']['border_color'])
        self.hover_border_width = self.int_or_none(cf_hovering['bg']['border_width'])

        self.click_bg_color = self.col_or_none(cf_clicked['bg']['color'])
        self.click_border_color = self.col_or_none(cf_clicked['bg']['border_color'])
        self.click_border_width = self.int_or_none(cf_clicked['bg']['border_width'])

        self.bg_surf = Surface(self.size, flags=SRCALPHA)
        self.hover_bg_surf = Surface(self.size, flags=SRCALPHA)
        self.click_bg_surf = Surface(self.size, flags=SRCALPHA)

        self.bg_surf.fill(Color(0,0,0,0))
        self.hover_bg_surf.fill(Color(0,0,0,0))
        self.click_bg_surf.fill(Color(0,0,0,0))

        if (self.bg_color):
            self.bg_surf.fill(self.bg_color)
        if (self.border_width):
            draw_rect(self.bg_surf, self.border_color, self.bg_surf.get_rect(), width=self.border_width)

        if (self.hover_bg_color):
            self.hover_bg_surf.fill(self.hover_bg_color)
        if (self.hover_border_width):
            draw_rect(self.hover_bg_surf, self.hover_border_color, self.hover_bg_surf.get_rect(), width=self.hover_border_width)

        if (self.click_bg_color):
            self.click_bg_surf.fill(self.click_bg_color)
        if (self.click_border_width):
            draw_rect(self.click_bg_surf, self.click_border_color, self.click_bg_surf.get_rect(), width=self.click_border_width)

        self.bg_rect = self.bg_surf.get_rect(topleft=self.position)
        self.hover_bg_rect = self.hover_bg_surf.get_rect(topleft=self.position)
        self.click_bg_rect = self.click_bg_surf.get_rect(topleft=self.position)

    def update(self, surface: Surface):
        # call the alt state decider. if true, use alt color. if not, regular.
        # this approach is not really optimized, however, there's a overflow of cpu capacity
        # when the menu is open, since no map sprites are being updated.
        if (self.click_state_active):
            surface.blit(self.click_bg_surf, self.rect)
            self.click_text_box.update()
            self.text_render = self.click_text_box.image
            self.text_rect = self.click_text_box.image.get_rect(center=self.rect.center)
        elif (self.hover_state_bool_func(self)):
            surface.blit(self.hover_bg_surf, self.rect)
            self.hover_text_box.update()
            self.text_render = self.hover_text_box.image
            self.text_rect = self.hover_text_box.image.get_rect(center=self.rect.center)
        else:
            surface.blit(self.bg_surf, self.rect)
            self.text_box.update()
            self.text_render = self.text_box.image
            self.text_rect = self.text_box.image.get_rect(center=self.rect.center)

        surface.blit(self.text_render, self.text_rect)
