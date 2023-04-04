from random import randint, uniform

from pygame import Color, Surface, mask, SRCALPHA
from pygame.sprite import Sprite
from pygame.draw import rect as draw_rect
# from pygame.gfxdraw import aapolygon as gfxdraw_aapolygon, aatrigon as gfxdraw_aatrigon


class Coin(Sprite):
    def __init__(self,
            cf_coin: dict,
            cf_global: dict,
            IMAGES: tuple[Surface, ...],
            position: tuple[int, int]
        ):

        Sprite.__init__(self)
        self.IMAGES = IMAGES
        self.cf_coin = cf_coin
        self.cf_global = cf_global
        self.position = position
        self.N_IMAGES = int(cf_coin['image_variants'] - 1)

        min_rate = self.cf_coin['min_img_iter_frequency']
        max_rate = self.cf_coin['max_img_iter_frequency']
        self.img_iteration_rate = round(float(cf_global['fps_limit']) * uniform(min_rate, max_rate))
        self.time_since_update = 0
        self.curr_img = randint(0, self.N_IMAGES-1)

        self.image = self.IMAGES[self.curr_img]
        self.rect = self.image.get_rect(topleft=position)
        self.mask = mask.from_surface(self.image)

    def update(self):
        self.time_since_update += 1
        if (self.time_since_update == self.img_iteration_rate):
            self.time_since_update = 0
            self.curr_img = (self.curr_img + 1) % self.N_IMAGES
            self.image = self.IMAGES[self.curr_img]
            self.mask = mask.from_surface(self.image)

