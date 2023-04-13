from pygame import Surface, SRCALPHA, transform, Rect, image


def partition_spritesheet(spritesheet: Surface, n_images: int, scalar: float, angle: None | float) -> tuple[Surface, ...]:
    ''' partition a horizontal spritesheet into equal sized segments '''
    images = []
    rect = spritesheet.get_rect()
    img_height = int(rect.h)
    img_width = int(rect.w / n_images)

    for x in range(0, rect.w, img_width):
        # create a new surface
        SURF = Surface((img_width, img_height), flags=SRCALPHA)
        # create a rect of the spritesheet area we want
        area_rect = Rect(x, 0, x+img_width, img_height)
        # blit that area from the sheet onto the surface, then scale
        SURF.blit(spritesheet, SURF.get_rect(), area_rect)
        IMG: Surface
        if (angle == None):
            IMG = transform.scale_by(SURF, scalar)
        else:
            IMG = transform.rotozoom(SURF, angle, scalar)

        images.append(IMG)

    # return list as a tuple
    return tuple(images)

def load_image(path: str, scalar: float, angle: None | float):
        IMG_SOURCE = image.load(path)
        img_width = IMG_SOURCE.get_width()
        img_height = IMG_SOURCE.get_height()

        SURF = Surface((img_width, img_height), flags=SRCALPHA)
        SURF.blit(IMG_SOURCE, SURF.get_rect())

        if (angle == None):
            return transform.scale_by(SURF, scalar)
        else:
            return transform.rotozoom(SURF, angle, scalar)

def load_sprites_tuple(path: str, n_images: int, scalar: float, angle: None | float) -> tuple[tuple[Surface, ...], int]:
    ''' returns a tuple:
        tuple[0] => tuple[images, ...]
        tuple[1] => max index of tuple[0] (len-1)
    '''

    if (n_images == 1):
        IMG = (load_image(path, scalar, angle), )
        return (IMG, int(n_images - 1))
    else:
        SHEET = image.load(path)
        IMAGES = partition_spritesheet(SHEET, n_images, scalar, angle)
        return (IMAGES, int(n_images - 1))
