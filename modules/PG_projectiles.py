from typing import Callable
from pygame import Surface, transform, mask, math as pg_math
from pygame.math import Vector2 as Vec2, lerp, clamp
from pygame import Surface, SRCALPHA, transform, Rect, image
from pygame.sprite import Sprite, Group, GroupSingle, spritecollide, spritecollideany, collide_mask, groupcollide
from .PG_common import load_sprites_tuple


class PG_Projectile(Sprite):
    def __init__(self,
            group: Group,
            damage: float,
            IMAGES: tuple[tuple[Surface, ...], int],
            position: Vec2,
            velocity: Vec2,
        ):
        Sprite.__init__(self, group)
        self.group = group
        self.damage = damage
        self.IMAGES = IMAGES[0]
        self.N_IMAGES = IMAGES[1]

        self.position = position.copy()
        self.velocity = velocity.copy()

        self.curr_image_index = 0
        self.image = self.IMAGES[self.curr_image_index]
        self.rect = self.image.get_rect(center=self.position)
        self.mask = mask.from_surface(self.image)

    def cycle_active_image(self):
        if (self.curr_image_index >= self.N_IMAGES):
            self.curr_image_index = 0
        else:
            self.curr_image_index += 1
        self.image = self.IMAGES[self.curr_image_index]

    def update(self, cycle_img: bool):
        if cycle_img:
            self.cycle_active_image()
        self.mask = mask.from_surface(self.image)
        self.position += self.velocity
        self.rect.center = self.position

class PG_Projectile_Spawner(Sprite):
    def __init__(self,
            group: Group,
            position: Vec2,
            rate_of_fire: int,
            sleep_duration: int | None,
            n_projectiles_before_sleep: int | None,
            P_cf_spritesheet: dict,
            P_img_cycle_frequency: int,
            P_image_scalar: float,
            P_collide_group: Group,
            P_player_collide_func: Callable[[float], None],
            P_kill_on_collide: bool,
            P_velocity: Vec2,
            P_damage: float
        ):
        Sprite.__init__(self, group)

        self.group = group
        self.position = position
        self.RATE_OF_FIRE = rate_of_fire
        self.SLEEP_DURATION = sleep_duration
        self.NUM_P_BEFORE_SLEEP = n_projectiles_before_sleep

        self.P_collide_group = P_collide_group
        self.P_player_collide_func = P_player_collide_func
        self.P_kill_on_collide = P_kill_on_collide
        self.P_IMG_CYCLE_FREQUENCY = P_img_cycle_frequency
        self.P_VELOCITY = P_velocity
        self.P_DAMAGE = P_damage

        # load + scale and rotate images
        self.P_angle = Vec2(0.0, 0.0).angle_to(P_velocity)
        self.P_IMG_SOURCE = load_sprites_tuple(
            P_cf_spritesheet['path'],
            P_cf_spritesheet['n_images'],
            P_image_scalar,
            self.P_angle
        )

        self.projectiles = Group()
        self.updates_until_fire = 0
        self.updates_until_cycle = 0
        self.updates_until_wake_up = None

        if (self.NUM_P_BEFORE_SLEEP != None):
            self.updates_until_wake_up = int(self.SLEEP_DURATION)
            self.projectiles_until_sleep = int(self.NUM_P_BEFORE_SLEEP)

    def init(self, player):
        self.player = player
        self.P_COLLIDEANY_GROUP = Group()
        self.P_COLLIDEANY_GROUP.add(player)
        self.P_COLLIDEANY_GROUP.add(self.P_collide_group)

    def spawn_projectile(self):
        PG_Projectile(self.projectiles, self.P_DAMAGE, self.P_IMG_SOURCE, self.position, self.P_VELOCITY)
        self.updates_until_fire = self.RATE_OF_FIRE

    def update(self, surface: Surface):
        if (self.updates_until_fire == 0):
            if (self.SLEEP_DURATION == None):
                self.spawn_projectile()
            else:
                if (self.updates_until_wake_up > 0):
                    self.updates_until_wake_up -= 1
                else:
                    self.spawn_projectile()
                    self.projectiles_until_sleep -= 1
                    if (self.projectiles_until_sleep == 0):
                        self.updates_until_wake_up = int(self.SLEEP_DURATION)
                        self.projectiles_until_sleep = int(self.NUM_P_BEFORE_SLEEP)
        else:
            self.updates_until_fire -= 1

        self.projectiles.draw(surface)

        if (self.updates_until_cycle == 0):
            self.updates_until_cycle = self.P_IMG_CYCLE_FREQUENCY
            self.projectiles.update(True)
        else:
            self.updates_until_cycle -= 1
            self.projectiles.update(False)

        collidedict = groupcollide(self.P_COLLIDEANY_GROUP, self.projectiles, False, True, collided=collide_mask)
        if (collidedict):
            for k, _ in collidedict.items():
                if k == self.player:
                    self.P_player_collide_func(self.P_DAMAGE)
