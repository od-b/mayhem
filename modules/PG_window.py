
## simplify some imports for readability:
from pygame import display, Color, Rect, FULLSCREEN

# https://www.pygame.org/docs/ref/display.html#pygame.display.set_mode
#
# pygame.FULLSCREEN    create a fullscreen display
# pygame.DOUBLEBUF     only applicable with OPENGL
# pygame.OPENGL        create an OpenGL-renderable display
# pygame.RESIZABLE     display window should be sizeable
# pygame.NOFRAME       display window will have no border or controls
# pygame.SCALED        resolution depends on desktop size and scale graphics
# pygame.SHOWN         window is opened in visible mode (default)
# pygame.HIDDEN        window is opened in hidden mode


class PG_Window:
    ''' wrapper for the main app surfaces / subsurfaces

    Noteworthy Attributes
    ---
    surface: 
        the entire window surface
    map_surface: 
        subsurface of surface designated to the active game area
    map_Rect: 
        Rect of the subsurface
    map_topleft_pos:
        map surface topleft, relative to the main surface
    '''

    def __init__(self, cf_global: dict, cf_window: dict):
        # set up window surface
        self.cf_global = cf_global
        self.cf_window = cf_window

        self.fill_color = Color(cf_window['fill_color'])
        self._vsync = int(cf_window['vsync'])
        self.fullscreen: bool = cf_window['fullscreen']
        self.width = int(cf_window['width'])
        self.height = int(cf_window['height'])
        self.caption = str(cf_window['caption'])

        if (self.fullscreen):
            self.surface = display.set_mode((self.width, self.height), vsync=self._vsync, flags=FULLSCREEN)
        else:
            self.surface = display.set_mode((self.width, self.height), vsync=self._vsync)

        self.fill_surface()
        self.set_extended_caption(None)

        # map subsurface topleft[x,y] position, relative to the main surface
        map_topleft_pos = (
            int(cf_window['map_surface_offset']['min_x']),
            int(cf_window['map_surface_offset']['min_y'])
        )

        # map size[w,h]
        map_size = (
            int(self.width - cf_window['map_surface_offset']['max_x'] - cf_window['map_surface_offset']['min_x']), 
            int(self.height - cf_window['map_surface_offset']['max_y'] - cf_window['map_surface_offset']['min_y'])
        )

        self.map_rect = Rect(
            (map_topleft_pos),
            (map_size)
        )
        ''' rect of map subsurface. Positioned relative to the entire window surface. '''

        self.map_surface = self.surface.subsurface(self.map_rect)
        ''' subsurface of the main surface dedicated to the map area '''
        # self.map_surface.set_colorkey(self.fill_color)

    def set_extended_caption(self, extension: str | None):
        ''' append a text to the window caption
            * set text to none to only use caption
        '''
        if (extension):
            display.set_caption(f'{self.caption}: {extension}')
        else:
            display.set_caption(self.caption)

    def fill_surface_alt_color(self, color: Color):
        ''' fill surface with a color that isn't self.fill_color '''
        self.surface.fill(color)

    def fill_surface(self):
        self.surface.fill(self.fill_color)

    def update(self):
        display.update()

    def __str__(self):
        msg = f'< PG_Window: width={self.width}, height={self.height}'
        if (self._vsync == 0):
            msg += f'vsync = True'
        else:
            msg += f'vsync = False'
        return msg
