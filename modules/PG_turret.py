from typing import Callable
from pygame import Surface, transform, mask
from pygame.math import Vector2 as Vec2, lerp, clamp
from pygame import Surface, SRCALPHA, transform, Rect, image
from pygame.sprite import Sprite, Group, GroupSingle, collide_mask, groupcollide
from .PG_common import load_image
from .PG_projectiles import PG_Projectile_Spawner

from math import cos, sin, pi

class PG_Missile_Turret(Sprite):
    def __init__(self,
            cf_turret: dict,
            group: Group,
            global_projectile_group: Group,
            position: Vec2 | tuple[int, int],
            angle: float
        ):
        Sprite.__init__(self, group)

        self.global_projectile_group = global_projectile_group
        self.position = position
        self.angle = angle
        self.image_scalar = float(cf_turret['image_scalar'])
        self.cf_projectile_spawner: dict = cf_turret['cf_projectile_spawner']
        self.ROTATION_RATE = float(cf_turret['rotation_rate'])
        self.projectile_magnitude = float(cf_turret['projectile_magnitude'])
        self.projectile_spawner_group = GroupSingle()

        rad = float(angle * (pi/180))
        p_velo = Vec2(cos(rad), sin(rad))
        
        p_velo.scale_to_length(self.projectile_magnitude)

        self.SPAWNER = PG_Projectile_Spawner(
            self.cf_projectile_spawner,
            self.projectile_spawner_group,
            self.global_projectile_group,
            self.position,
            p_velo
        )

        self.CHECK_IF_ROTATE = False

        if self.SPAWNER.SLEEP_DURATION:
            self.PRE_SHOT_DELAY = int(cf_turret['delay_before_shooting'])
            self.POST_SHOT_DELAY = int(cf_turret['delay_after_shooting'])
            self.POST_SHOT_DELAY_RANGE = int(self.SPAWNER.SLEEP_DURATION - self.POST_SHOT_DELAY)
            if (self.PRE_SHOT_DELAY > 0) or (self.POST_SHOT_DELAY > 0):
                self.CHECK_IF_ROTATE = True

        self.ORIGINAL_IMAGE = load_image(cf_turret['spritesheet']['path'], cf_turret['image_scalar'], -90.0)
        self.image = self.ORIGINAL_IMAGE
        self.rect = self.image.get_rect(center=self.position)
        self.mask = mask.from_surface(self.image)

    def init(self, player: Sprite):
        for spawner in self.projectile_spawner_group.sprites():
            spawner.init(player)

    def update_image(self):
        ''' update self.image, transforming it to the current angle. Recreate self .rect, .mask. '''
        self.image = transform.rotate(self.ORIGINAL_IMAGE, -self.angle)
        self.mask = mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=self.position)

    def update(self, surface: Surface):
        if (self.ROTATION_RATE):
            if (self.CHECK_IF_ROTATE):
                wake_time = self.SPAWNER.updates_until_wake_up

                if ((wake_time < self.PRE_SHOT_DELAY) or (wake_time > self.POST_SHOT_DELAY_RANGE)):
                    self.projectile_spawner_group.update(surface, float(0))
                else:
                    self.angle += self.ROTATION_RATE
                    self.projectile_spawner_group.update(surface, self.ROTATION_RATE)
            else:
                self.angle += self.ROTATION_RATE
                self.projectile_spawner_group.update(surface, self.ROTATION_RATE)

            self.update_image()
        else:
            self.projectile_spawner_group.update(surface, float(0))
