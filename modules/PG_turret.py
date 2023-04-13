from typing import Callable
from pygame import Surface, transform, mask
from pygame.math import Vector2 as Vec2, lerp, clamp
from pygame import Surface, SRCALPHA, transform, Rect, image
from pygame.sprite import Sprite, Group, collide_mask, groupcollide
from .PG_common import load_image
from .PG_projectiles import PG_Projectile_Spawner

from math import cos, sin, pi

class PG_Turret(Sprite):
    def __init__(self,
            cf_turret: dict,
            group: Group,
            position: Vec2 | tuple[int, int],
            angle: float,
            collide_group: Group,
            player_collide_func: Callable
        ):
        Sprite.__init__(self, group)

        self.position = position
        self.angle = angle
        self.image_scalar = float(cf_turret['image_scalar'])
        self.n_projectile_spawners = int(cf_turret['n_projectile_spawners'])
        self.cf_projectile_spawner: dict = cf_turret['cf_projectile_spawner']
        self.rotation_rate = float(cf_turret['rotation_rate'])
        self.projectile_spawner_group = Group()

        rad = float(angle * (pi/180))
        p_velo = Vec2(cos(rad), sin(rad))

        for _ in range(self.n_projectile_spawners):
            PG_Projectile_Spawner(
                self.cf_projectile_spawner,
                self.projectile_spawner_group,
                self.position,
                p_velo,
                collide_group,
                player_collide_func
            )

        image_scalar = cf_turret['image_scalar']
        image_path = cf_turret['spritesheet']['path']
        # n_images = cf_turret['spritesheet']['n_images']
        self.ORIGINAL_IMAGE = load_image(image_path, image_scalar, self.angle)
        self.image = self.ORIGINAL_IMAGE
        self.rect = self.image.get_rect(center=self.position)
        self.mask = mask.from_surface(self.image)

    def init(self, player: Sprite):
        for spawner in self.projectile_spawner_group.sprites():
            spawner.init(player)

    def update(self, surface: Surface):
        self.angle += self.rotation_rate
        self.projectile_spawner_group.update(surface, self.rotation_rate)
