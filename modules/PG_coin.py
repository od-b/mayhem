from random import randint, uniform

from pygame import Surface, mask
from pygame.sprite import Sprite


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

        rand_rate = uniform(self.cf_coin['min_img_iter_frequency'], self.cf_coin['max_img_iter_frequency'])
        self.img_iteration_rate = round(cf_global['fps_limit'] * rand_rate)
        self.img_iteration_rate = 14
        self.time_since_update = 0

        self.curr_image_index = randint(0, self.IMAGES[1])
        self.image = self.IMAGES[0][self.curr_image_index]
        self.rect = self.image.get_rect(center=position)
        self.mask = mask.from_surface(self.image)

    def update(self):
        self.time_since_update += 1
        if (self.time_since_update == self.img_iteration_rate):
            self.time_since_update = 0
            if (self.curr_image_index >= self.IMAGES[1]):
                self.curr_image_index = 0
            else:
                self.curr_image_index += 1
            self.image = self.IMAGES[0][self.curr_image_index]

            # TODONE - look into how costly mask generation is. could pre-make a list of masks
            # ncalls  tottime  percall  cumtime  percall filename:lineno(function)
            #     1    0.000    0.000   31.657   31.657 <string>:1(<module>)
            #  7262    0.047    0.000    0.047    0.000 {built-in method pygame.mask.from_surface}
            # --> from_surface seems extremely optimized, not worth looking into
            self.mask = mask.from_surface(self.image)
