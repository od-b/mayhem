from typing import Callable

## import needed pygame modules
from pygame import Color
from pygame.sprite import Sprite
from pygame.font import Font

from .PG_ui_container import UI_Sprite_Container_Filled


class UI_Text_Box(Sprite):
    ''' Created by container as a child

        Parameters
        ---
        font_antialias: bool
            whether to apply antialiasing when rendering text

        ---
        text_getter_func: Callable[[None], any] | None
            * must take no parameters. The return value will be converted to a string.
            * on update, will call the function and set its text to the returned value
            * if provided, and given text is not and empty string, 
                the initial text parameter will serve as a 'pre-text' for all updated strings.
        --- 
        if None is passed as text_getter_func and the text is to be changed, set_new_text()
        must be called manually to update the text and its rendering.
    '''

    def __init__(self,
            cf_textbox: dict,
            cf_global: dict,
            ref_id,
            text: str,
            text_getter_func: Callable | None,
            position: tuple
        ):

        Sprite.__init__(self)
        self.cf_textbox = cf_textbox
        self.cf_global = cf_global
        self.ref_id = ref_id
        self.text = text
        self.text_getter_func = text_getter_func
        self.position = position

        # store config settings
        self.font_path = str(cf_textbox['font_path'])
        self.font_size = int(cf_textbox['font_size'])
        self.font_antialas: bool = cf_textbox['font_antialias']
        self.font_color = Color(cf_textbox['font_color'])
        if (cf_textbox['text_bg_color']):
            self.bg_color = Color(cf_textbox['text_bg_color'])
        else:
            self.bg_color = None

        # load font
        self.font = Font(self.font_path, self.font_size)
        self.old_text = text

        # render the text and get its rect
        self.image = self.font.render(
            self.text,
            self.font_antialas,
            self.font_color,
            self.bg_color
        )
        self.rect = self.image.get_rect()
        self.rect.topleft = position

        self._set_internal_update_func()

    def _set_internal_update_func(self):
        ''' all textboxes have a update func, regardless of text_getter_func/not '''
        # allows for for a simple, generalized update func
        if (self.text_getter_func):
            self.render_on_update = True
            if (self.text == ''):
                self.text_update_func = self._get_text_from_getter_func
            else:
                self.pre_text = self.text
                self.text_update_func = self._get_text_from_getter_func_with_pre_text
        else:
            self.render_on_update = False
            # default to just returning own text
            self.text_update_func = self.get_text

    def _get_text_from_getter_func(self):
        ''' internal function: returns a string through the given text_getter_func, no pre_text '''
        return self.text_getter_func()

    def _get_text_from_getter_func_with_pre_text(self):
        ''' internal function: returns a string through the given text_getter_func
            * concats the text provided originally and the string from the getter
        '''
        return f'{self.pre_text}{self.text_getter_func()}'

    def get_text(self):
        ''' returns the exact text displayed on the current render '''
        return self.text

    def set_pre_text(self, text: str):
        ''' function to add or replace pre-text for textboxes with a getter_func.
            * does nothing if textbox does not have a getter_func
        '''
        self.pre_text = text
        if not self.text_getter_func:
            self.text = f'{self.pre_text}{self.text}'

    def set_text(self, text: str):
        ''' for manual replacement of text. Re-renders image to the text.
            * if this is called and a getter exists, it will prevent future updates from the getter
            * call resume_text_getter to resume rendering through the getter
        '''
        self.text = text
        self.update_text_render()
        self.render_on_update = False

    def resume_text_getter(self):
        ''' if a textbox with a getter_func has been overwritten through set_text, call this to resume
            updating through the getter instead
        '''
        if (self.text_getter_func):
            self.render_on_update = True

    def update_text_render(self):
        ''' replaces self.image with a text render of the self.content text. Updates self.rect '''
        self.image = self.font.render(
            self.text,
            self.font_antialas,
            self.font_color,
            self.bg_color
        )
        self.rect = self.image.get_rect()

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

    def __str__(self):
        msg = f'[{super().__str__()} : '
        msg += f'text="{self.pre_text}{self.text}", height={self.rect.h}, width={self.rect.w}'
        msg += f'ref_id(s)={self.ref_id}]'
        return msg


class UI_Text_Box_Filled(UI_Text_Box):
    def __init__(self,
            cf_textbox: dict,
            cf_global: dict,
            ref_id,
            text: str,
            text_getter_func: Callable | None,
            position: tuple,
            fill_color,
            border_color,
            border_width,
            width,
            height,
            padding_x,
            padding_y,
        ):

        super().__init__(cf_textbox, cf_global, ref_id, text, text_getter_func, position)

        self.fill_color = fill_color
        self.border_color = border_color
        self.border_width = border_width

        
