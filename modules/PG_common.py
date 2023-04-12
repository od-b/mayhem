from pygame import Surface, SRCALPHA, transform, Rect, image


def partition_spritesheet(spritesheet: Surface, n_images: int, scale: float) -> tuple[Surface, ...]:
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
        IMG = transform.scale_by(SURF, scale)
        images.append(IMG)

    # return list as a tuple
    return tuple(images)

def load_sprites_tuple(path, n_images, scalar) -> tuple[tuple[Surface, ...], int]:
    ''' returns a tuple:
        tuple[0] => tuple[images, ...]
        tuple[1] => max index of tuple[0] (len-1)
    '''
    SHEET = image.load(path)

    if (n_images == 1):
        img_width = SHEET.get_width()
        img_height = SHEET.get_height()

        SURF = Surface((img_width, img_height), flags=SRCALPHA)
        SURF.blit(SHEET, SURF.get_rect())

        IMG = (transform.scale_by(SURF, scalar), )
        return (IMG, int(n_images - 1))
    else:
        IMAGES = partition_spritesheet(SHEET, n_images, scalar)
        return (IMAGES, int(n_images - 1))
