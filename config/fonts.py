from os.path import join as os_path_join
from .colors import RGB, RGBA

FORMATTING_TRIGGERS = {
    # one of | none:
    'bold': str("_b_"),
    'italic': str("_i_"),
    'light': str("_l_"),
    # may be combined:
    'alt_color': str("a/"),
    'title': str("t/"),
    'newline': str("n/"),
    'nosplit': str('::')    # renders words together. applies formatting to all. useful for titles.
}
''' Defined string triggers for applying different styles/fonts/colors/effects, for certain modules.
    * The positioning of triggers within a word is irrelevant, even if in the middle of a word.
    * Any style triggers are removed from the string before rendering/printing.\n
    see modules.PG_ui_container.py -> UI_Text_Container for an example use case '''

# global toggle for whether or not to apply font aliasing
FONT_ANTIALIAS = True
FONT_RECT_BG_COLOR = None
# FONT_RECT_BG_COLOR = RGB['P_pink']

STANDARDIZED_SIZES = {
    'small': 20,
    'normal': 24,
    'medium': 26,
    'large': 30,
    'xlarge': 40
}

PATHS = {
    'light': {
        'default': os_path_join('assets','fonts','JetBrainsMono-Light.ttf'),
        'italic': os_path_join('assets','fonts','JetBrainsMono-LightItalic.ttf'),
    },
    'regular': {
        'default': os_path_join('assets','fonts','JetBrainsMono-Regular.ttf'),
        'italic': os_path_join('assets','fonts','JetBrainsMono-Italic.ttf')
    },
    'semibold': {
        'default': os_path_join('assets','fonts','JetBrainsMono-SemiBold.ttf'),
        'italic': os_path_join('assets','fonts','JetBrainsMono-SemiBoldItalic.ttf')
    },
    'bold': {
        'default': os_path_join('assets','fonts','JetBrainsMono-Bold.ttf'),
        'italic': os_path_join('assets','fonts','JetBrainsMono-BoldItalic.ttf')
    },
}

def get_path(style: str, style_weight: str | None):
    ''' get path of the fonts used '''
    if (style_weight == None):
        return str(PATHS[style]['default'])
    return str(PATHS[style][style_weight])


def cf_font(size: int | str, color: str | tuple, style: str, style_weight: str | None):
    ''' choose from standardized font values or specify font color and/or size 
        * weight => ['None'=='default', 'italic']
        * color => tuple, OR, if string -> chooses matching key from .colors RGB or RGBA
        * size => if string, picks a standardized size. 
            implemented standardized sizes: ['small', 'normal', 'medium', 'large', xlarge']
            
        returns a dict = {
            'antialias': < bool, whether or not to apply antialiasing >,
            'bg_color': < color | None, to fill the font rect background. (pg.font.render supports bg=None for alpha) >,
            'path': < local path of the font file, assembled using os_path_join for compatibility >,
            'size': < int >,
            'color': < tuple of rgb(+/-a) color values >,
        }
        
        * antialias / bg_color are shared settings. overwrite locally if ever needed.
        bg_color can be very useful for debugging purposes. not so much otherwise, due to the varying text rect sizes.
    '''
    CF = {
        'antialias': FONT_ANTIALIAS,
        'bg_color': FONT_RECT_BG_COLOR
    }

    if (type(size) == str):
        CF['size'] = int(STANDARDIZED_SIZES[size])
    else:
        CF['size'] = int(size)

    if (type(color) == str):
        # search both RGB and RGBA for the right value
        key_found = False
        for k, v in RGB.items():
            if (k == color):
                CF['color'] = v
                key_found = True
                break
        if not key_found:
            for k, v in RGBA.items():
                if (k == color):
                    CF['color'] = v
                    key_found = True
                    break
        if not key_found:
            raise KeyError(f'key="{color}" not in config.colors RGB | RGBA')
    else:
        CF['color'] = color

    CF['path'] = get_path(style, style_weight)

    return CF

