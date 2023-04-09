from typing import Callable

## import needed pygame modules
from pygame import Color
from pygame.font import Font
from pygame.sprite import Sprite

from .PG_ui_text_box import UI_Text_Box

class UI_Button(UI_Text_Box):
    def __init__(self,
            cf_font: dict,
            cf_alt_font: dict,
            cf_global: dict,
            ref_id,
            text: str,
            text_getter_func: Callable | None,
            trigger_func: Callable,
            position: tuple
        ):
        super().__init__(cf_font, cf_global, ref_id, text, text_getter_func, position)

        if (cf_alt_font['text_bg_color']):
            self.alt_bg_color = Color(cf_alt_font['text_bg_color'])
        else:
            self.alt_bg_color = None

        self.alt_font_color = Color(cf_alt_font['font_color'])
        self.alt_font = Font(
            str(cf_alt_font['font_path']),
            int(cf_alt_font['font_size'])
        )
        
        
        self.alt_state_active = False

    def update_text_render(self):
        if self.alt_state_active:
            pass
        else:
            super().update_text_render()

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
