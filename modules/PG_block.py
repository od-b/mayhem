from random import randint

import pygame as pg
from pygame import Color, Surface, SRCALPHA
from pygame.sprite import Sprite
from pygame.draw import rect as draw_rect
# from pygame.gfxdraw import aapolygon as gfxdraw_aapolygon, aatrigon as gfxdraw_aatrigon


class Block(Sprite):
    ''' Static object with none or a constant, set velocity/mass.
        * for a pure alpha block, set pallette to None and highlight_time to 0

        Parameters
        ---
        cf_block: dict with expected keys   -> config/cf_blocks/CF_BLOCKS
        cf_global: dict with expected keys  -> config/cf_global/CF_GLOBAL
        size: tuple[int, int]
        position: tuple[int, int]
        pallette: list[Color]
    '''

    def __init__(self,
            cf_block: dict,
            cf_global: dict,
            pallette: list[tuple],
            size: tuple[int, int],
            position: tuple[int, int]
        ):

        Sprite.__init__(self)

        # store references to the config dicts
        self.cf_global  = cf_global
        self.cf_block   = cf_block

        self.pallette   = pallette
        ''' list of one or more tuples. May be RGB, RGBA, or even a mix '''
        self.position   = position
        ''' top left position '''
        self.size       = size
        ''' use .rect for easier external access to the size '''
        self.alpha_key  = int(cf_block['alpha_key'])

        # store attributes from config
        self.mass          = float(cf_block['mass'])
        self.border_width  = int(cf_block['border_width'])
        self.border_color: Color | None = cf_block['border_color']

        # pick a random color from the given color pallette
        self.color = Color(self.pallette[randint(0, len(self.pallette)-1)])

        # determine if alpha conversion is needed
        if (self.alpha_key < 255):
            # convert to rgba
            self.alpha_value = self.alpha_key
            COLOR_TO_ALPHA = (self.color.r, self.color.g, self.color.b, self.alpha_key)
            self.color = Color(COLOR_TO_ALPHA)
        else:
            # color is rgb, no convert_alpha() needed
            self.alpha_value = None

        self.MAIN_IMAGE = self._create_main_image()
        ''' surface containing the original image and its content, if any '''

        self.ALT_IMAGE = self._create_alt_image()
        ''' if the blocks' cf_block-dict has a subdict under "['alt_surface']",
            this will be a Surface.
            Otherwise, it will be None.
            ---
            Iff ALT_IMAGE is a Surface, the following attributes may also be accessed:
            * self.alt_border_color
            * self.alt_color
            * self.ALT_SURF_DURATION
        '''

        if (self.ALT_IMAGE):
            self.alt_surf_timeleft = int(0)
            ''' variable, remaining duration of the highlight.
                * is set to None if an ALT_IMG does not exist
            '''
        else:
            self.alt_surf_timeleft = None

        self.image = self.MAIN_IMAGE
        ''' currently used image '''

        # needed for sprite blitting through group.draw()
        self.rect = self.MAIN_IMAGE.get_rect()
        self.rect.topleft = self.position

        # create a mask for fast collision detection
        self.mask = pg.mask.from_surface(self.image)
        ''' pygame mask from the main surface, for fast collision detection '''

    def _create_main_image(self):
        # create main surface, converting to the right format
        IMG: Surface
        if (self.alpha_value):
            IMG = pg.Surface(self.size, flags=SRCALPHA)
            IMG.fill((0, 0, 0, 0))
        else:
            IMG = pg.Surface(self.size).convert()

        if (self.color):
            IMG.fill(self.color)

        # draw border if set
        if (self.border_width > 0) and (self.border_color != None):
            draw_rect(IMG, Color(self.border_color), IMG.get_rect(), width=self.border_width)
        
        return IMG

    def _create_alt_image(self):
        # check whether the subdict config is set to none before trying to access it
        if (type(self.cf_block['alt_surface']) == dict):
            # function-scope reference for readability
            cf_alt_surf = self.cf_block['alt_surface']

            # create alt surface, converting to the right format
            ALT_IMG: Surface
            if (self.alpha_value):
                ALT_IMG = pg.Surface(self.size, flags=SRCALPHA)
            else:
                ALT_IMG = pg.Surface(self.size).convert()

            # read and store the dict settings as proper types
            if (cf_alt_surf['color'] != None):
                # set attr and convert to pygame color
                self.alt_color = Color(cf_alt_surf['color'])
                ALT_IMG.fill(Color(self.alt_color))
            else:
                self.alt_color = None

            if (cf_alt_surf['border_color'] != None):
                # set attr and convert to pygame color
                self.alt_border_color = Color(cf_alt_surf['color'])
                draw_rect(ALT_IMG, Color(self.alt_border_color), ALT_IMG.get_rect(), width=self.border_width)
            else:
                self.alt_border_color = None

            # calculated the frames needed to display x milliseconds worth of highlight
            self.ALT_SURF_DURATION  = int(1000 / (cf_alt_surf['duration'] / self.cf_global['fps_limit']))
            ''' frames to highlight the block for, calculated using the FPS limit '''

            return ALT_IMG

        # else, no alt image is to be set
        return None

    def init_highlight(self):
        ''' swap to the ALT_IMAGE for a certain time
            * the duration is specified as millisecond within cf_block
            * does nothing if the block does not have an ALT_IMAGE
        '''
        if (self.ALT_IMAGE):
            self.alt_surf_timeleft = self.ALT_SURF_DURATION
            # swap image to the alt image
            self.image = self.ALT_IMAGE

    def update(self):
        ''' does nothing for the block unless highlighted through .init_highlight() '''
        if (self.alt_surf_timeleft):
            self.alt_surf_timeleft -= 1
            if (self.alt_surf_timeleft == 0):
                # swap image back if timer is up
                self.image = self.MAIN_IMAGE
