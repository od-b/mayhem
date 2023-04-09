from typing import Callable

## import needed pygame modules
from pygame import Color
from pygame.sprite import Sprite

from .PG_ui_text_box import UI_Text_Box

class UI_Button(UI_Text_Box):
    def __init__(self,
            cf_textbox: dict,
            cf_global: dict,
            ref_id,
            text: str,
            text_getter_func: Callable | None,
            position: tuple
        ):
        super().__init__(cf_textbox, cf_global, ref_id, text, text_getter_func, position)
