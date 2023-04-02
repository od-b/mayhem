from random import randint

from pygame import Color, Surface, mask, SRCALPHA
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
            position: tuple[int, int],
            update_interval: int
        ):

        Sprite.__init__(self)

        # store references to the config dicts
        self.cf_global  = cf_global
        self.cf_block   = cf_block
        self.UPDATE_INTERVAL = update_interval

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
            self.alpha_value = self.alpha_key
            if (self.color):
                # convert to rgba
                self.color = Color((self.color.r, self.color.g, self.color.b, self.alpha_key))
            else:
                self.color = Color((0, 0, 0, self.alpha_key))
        else:
            # color is rgb, no conversion needed needed
            self.alpha_value = None

        self.MAIN_IMAGE = self._create_main_image()
        ''' surface containing the original image and its content, if any '''

        self.ALT_IMAGE = self._create_alt_image()
        ''' if the blocks' cf_block-dict has a subdict under "['alt_surface']",
            this will be a Surface. Otherwise, it will be None.

            _create_alt_image Sets these attributes:
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
        self.mask = mask.from_surface(self.image)
        ''' pygame mask from the main surface, for fast collision detection '''

    def _create_main_image(self):
        # create main surface, converting to the right format
        IMG: Surface
        if (self.alpha_value):
            IMG = Surface(self.size, flags=SRCALPHA)
        else:
            IMG = Surface(self.size).convert()

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
                ALT_IMG = Surface(self.size, flags=SRCALPHA)
            else:
                ALT_IMG = Surface(self.size).convert()

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

            # subtracting update interval yields the correct timing
            # verify that this does not leave a negative timer, however
            if (cf_alt_surf['duration'] == 0):
                self.ALT_SURF_DURATION = int(0)
                ''' ms to highlight the block for '''
            elif (cf_alt_surf['duration'] < self.UPDATE_INTERVAL):
                self.ALT_SURF_DURATION = self.UPDATE_INTERVAL
            else:
                self.ALT_SURF_DURATION = int(cf_alt_surf['duration'] - self.UPDATE_INTERVAL)

            return ALT_IMG

        # else, no alt image is to be set. Be a good boy and set self values nonetheless
        self.alt_color = None
        self.alt_border_color = None
        self.ALT_SURF_DURATION = 0
        return None

    def swap_to_alt_image(self):
        if (self.ALT_IMAGE):
            self.image = self.ALT_IMAGE
            self.alt_surf_timeleft = 0

    def init_timed_highlight(self):
        ''' if an alt image exists, swap to it. 
            if self.ALT_SURF_DURATION is 0, the swap will be retained until manually reverted
            auto swaps back through self.update(), which should be called every frame
        '''
        if (self.ALT_IMAGE):
            self.image = self.ALT_IMAGE
            self.alt_surf_timeleft = self.ALT_SURF_DURATION

    def update(self):
        ''' checks if the block has a alt_surf_timeleft, swaps image back if time is up
            * if NO blocks are EVER highlighted, this function does not need to be called.
        '''
        if (self.alt_surf_timeleft):
            self.alt_surf_timeleft -= self.UPDATE_INTERVAL
            if (self.alt_surf_timeleft <= 0):
                # debugging code to check timer works as intended (it does):
                # time_diff = (timestamp - self.highlight_started_time)
                # print(f'highlight lasted {time_diff}ms')
                # self.highlight_started_time = int(0)
                # swap image back if timer is up
                self.image = self.MAIN_IMAGE
