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
            text: str,
            text_getter_func: Callable | None,
            size: tuple[int, int],
            position: tuple,
            trigger_func: Callable,
            trigger_parameter,
            alt_state_bool_func: Callable
        ):
        Sprite.__init__(self)

        self.text_box = UI_Text_Box(cf_button['font'], cf_global, ref_id, text, text_getter_func, ref_id, position)
        self.alt_text_box = UI_Text_Box(cf_button['alt_font'], cf_global, ref_id, text, text_getter_func, ref_id, position)

        self.alt_state_bool_func = alt_state_bool_func
        self.position = position
        self.cf_button = cf_button

        self.bg_color = self.col_or_none(cf_button['bg_color'])
        self.border_color = self.col_or_none(cf_button['border_color'])
        self.border_width = self.int_or_none(cf_button['border_width'])

        self.alt_bg_color = self.col_or_none(cf_button['alt_bg_color'])
        self.alt_border_color = self.col_or_none(cf_button['alt_border_color'])
        self.alt_border_width = self.int_or_none(cf_button['alt_border_width'])

        self.size = size
        self.bg_surf = Surface(self.size, flags=SRCALPHA)
        self.alt_bg_surf = Surface(self.size, flags=SRCALPHA)
        self.image = Surface(self.size, flags=SRCALPHA)

        self.image.fill(Color(0,0,0,0))
        self.bg_surf.fill(Color(0,0,0,0))
        self.alt_bg_surf.fill(Color(0,0,0,0))

        if (self.bg_color):
            self.bg_surf.fill(self.bg_color)
        if (self.border_width):
            draw_rect(self.bg_surf, self.border_color, self.bg_surf.get_rect(), width=self.border_width)

        if (self.alt_bg_color):
            self.alt_bg_surf.fill(self.alt_bg_color)
        if (self.alt_border_width):
            draw_rect(self.alt_bg_surf, self.alt_border_color, self.alt_bg_surf.get_rect(), width=self.alt_border_width)

        self.rect = self.image.get_rect(topleft=self.position)
        self.bg_rect = self.bg_surf.get_rect(topleft=self.position)
        self.alt_bg_rect = self.alt_bg_surf.get_rect(topleft=self.position)

        self.trigger_func = trigger_func
        self.trigger_parameter = trigger_parameter
        self.alt_state_active = False

    def int_or_none(self, cf_val):
        if (cf_val != None) and (cf_val != 0):
            return int(cf_val)
        return None

    def col_or_none(self, cf_val):
        if (cf_val != None):
            return Color(cf_val)
        return None

    def trigger(self):
        if (self.trigger_parameter != None):
            self.trigger_func(self.trigger_parameter)
        else:
            self.trigger_func()

    def update(self, surface: Surface):
        ''' update rendering if text has changed '''

        if (self.alt_state_bool_func(self)):
            surface.blit(self.alt_bg_surf, self.rect)
            self.alt_text_box.update()
            self.text_render = self.alt_text_box.image
            self.text_rect = self.alt_text_box.image.get_rect(center=self.rect.center)
        else:
            surface.blit(self.bg_surf, self.rect)
            self.text_box.update()
            self.text_render = self.text_box.image
            self.text_rect = self.text_box.image.get_rect(center=self.rect.center)

        surface.blit(self.text_render, self.text_rect)

