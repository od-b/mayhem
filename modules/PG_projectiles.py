from typing import Callable
from pygame import Surface, transform, mask
from pygame.math import Vector2 as Vec2, lerp, clamp
from pygame import Surface, SRCALPHA, transform, Rect, image
from pygame.sprite import Sprite, Group, collide_mask, groupcollide
from .PG_common import load_sprites_tuple


class PG_Projectile(Sprite):
    ''' projectile with a single image '''
    def __init__(self,
            group: Group,
            damage: float,
            image: Surface,
            position: Vec2,
            velocity: Vec2,
        ):
        Sprite.__init__(self, group)
        self.group = group
        self.damage = damage

        self.position = position.copy()
        self.velocity = velocity.copy()
        self.image = image
        self.rect = self.image.get_rect(center=self.position)
        self.mask = mask.from_surface(self.image)

    def update(self):
        self.mask = mask.from_surface(self.image)
        self.position += self.velocity
        self.rect.center = self.position


class PG_Projectile_Cycle(PG_Projectile):
    ''' projectile that cycles between spritesheet images '''
    def __init__(self,
            group: Group,
            damage: float,
            IMAGES: tuple[tuple[Surface, ...], int],
            position: Vec2,
            velocity: Vec2,
            cycle_frequency: int
        ):
        super().__init__(group, damage, IMAGES[0][0], position, velocity)
        self.curr_image_index = 0
        self.IMAGES = IMAGES[0]
        self.N_IMAGES = IMAGES[1]
        self.cycle_frequency = cycle_frequency
        self.updates_until_cycle = cycle_frequency

    def cycle_active_image(self):
        if (self.curr_image_index >= self.N_IMAGES):
            self.curr_image_index = 0
        else:
            self.curr_image_index += 1
        self.image = self.IMAGES[self.curr_image_index]

    def update(self):
        if (self.updates_until_cycle == 0):
            self.updates_until_cycle = self.cycle_frequency
            self.cycle_active_image()
        else:
            self.updates_until_cycle -= 1

        super().update()


class PG_Projectile_Spawner(Sprite):
    def __init__(self,
            cf_projectile_spawner: dict,
            group: Group,
            position: Vec2 | tuple[int, int],
            P_velocity: Vec2 | tuple[int, int],
            P_collide_group: Group,
            P_player_collide_func: Callable[[float], None],
        ):
        Sprite.__init__(self, group)

        self.group = group
        self.position = Vec2(position)
        self.RATE_OF_FIRE = int(cf_projectile_spawner['rate_of_fire'])
        self.SLEEP_DURATION = cf_projectile_spawner['sleep_duration']
        self.N_PROJECTILES_BEFORE_SLEEP = cf_projectile_spawner['n_projectiles_before_sleep']

        cf_projectile = cf_projectile_spawner['cf_projectile']
        self.P_IMG_CYCLE_FREQUENCY = int(cf_projectile['img_cycle_frequency'])
        self.P_IMAGE_SCALAR = float(cf_projectile['image_scalar'])
        self.P_KILL_ON_COLLIDE = cf_projectile['kill_on_collide']
        self.P_DAMAGE = float(cf_projectile['damage'])
        self.P_VELOCITY = Vec2(P_velocity)
        self.P_collide_group = P_collide_group
        self.P_player_collide_func = P_player_collide_func
        
        self.P_spritesheet_path = str(cf_projectile['spritesheet']['path'])
        self.P_spritesheet_n_images = int(cf_projectile['spritesheet']['n_images'])
        
        # load + scale and rotate images
        self.P_angle = Vec2(0.0, 0.0).angle_to(Vec2(self.P_VELOCITY.x, -self.P_VELOCITY.y))
        IMG_SOURCE = load_sprites_tuple(
            self.P_spritesheet_path,
            self.P_spritesheet_n_images,
            self.P_IMAGE_SCALAR,
            self.P_angle
        )

        self.spawn_projectile_func: Callable
        if (self.P_IMG_CYCLE_FREQUENCY == 0):
            self.spawn_projectile_func = self.spawn_projectile
            self.P_IMG_SOURCE = IMG_SOURCE[0][0]
            self.ORIGINAL_SURF = Surface((self.P_IMG_SOURCE.get_width(), self.P_IMG_SOURCE.get_height()), flags=SRCALPHA)
            self.ORIGINAL_SURF.blit(self.P_IMG_SOURCE, self.ORIGINAL_SURF.get_rect())
        else:
            self.spawn_projectile_func = self.spawn_cycle_projectile
            self.P_IMG_SOURCE = IMG_SOURCE

        self.projectiles = Group()
        self.updates_until_fire = 0
        self.updates_until_cycle = 0
        self.updates_until_wake_up = None

        if (self.N_PROJECTILES_BEFORE_SLEEP != None):
            self.updates_until_wake_up = int(self.SLEEP_DURATION)
            self.projectiles_until_sleep = int(self.N_PROJECTILES_BEFORE_SLEEP)

    def rotate_projectile_angle(self, new_velo: Vec2):
        ''' rotate the direction of NEW projectiles. fired ones remain the same '''
        self.P_VELOCITY = Vec2(new_velo)
        self.P_angle = Vec2(0.0, 0.0).angle_to(Vec2(self.P_VELOCITY.x, -self.P_VELOCITY.y))

        if (self.P_IMG_CYCLE_FREQUENCY == 0):
            self.P_IMG_SOURCE = transform.rotate(self.ORIGINAL_SURF, self.P_angle)
        else:
            IMG_SOURCE = load_sprites_tuple(
                self.P_spritesheet_path,
                self.P_spritesheet_n_images,
                self.P_IMAGE_SCALAR,
                self.P_angle
            )
            self.P_IMG_SOURCE = IMG_SOURCE

    def rotate_by_degrees(self, delta_angle):
        new_velo = self.P_VELOCITY.rotate(delta_angle)
        self.rotate_projectile_angle(new_velo)

    def init(self, player: Sprite):
        self.player = player
        self.P_COLLIDEANY_GROUP = Group()
        self.P_COLLIDEANY_GROUP.add(player)
        self.P_COLLIDEANY_GROUP.add(self.P_collide_group)

    def spawn_cycle_projectile(self):
        PG_Projectile_Cycle(self.projectiles, self.P_DAMAGE, self.P_IMG_SOURCE,
                            self.position, self.P_VELOCITY, self.P_IMG_CYCLE_FREQUENCY)
        self.updates_until_fire = self.RATE_OF_FIRE

    def spawn_projectile(self):
        PG_Projectile(self.projectiles, self.P_DAMAGE, self.P_IMG_SOURCE, self.position, self.P_VELOCITY)
        self.updates_until_fire = self.RATE_OF_FIRE

    def update(self, surface: Surface, delta_angle: float):
        if (delta_angle):
            self.rotate_by_degrees(delta_angle)

        if (self.updates_until_fire == 0):
            if (self.SLEEP_DURATION == None):
                self.spawn_projectile_func()
            else:
                if (self.updates_until_wake_up > 0):
                    self.updates_until_wake_up -= 1
                else:
                    self.spawn_projectile_func()
                    self.projectiles_until_sleep -= 1
                    if (self.projectiles_until_sleep == 0):
                        self.updates_until_wake_up = int(self.SLEEP_DURATION)
                        self.projectiles_until_sleep = int(self.N_PROJECTILES_BEFORE_SLEEP)
        else:
            self.updates_until_fire -= 1

        self.projectiles.draw(surface)
        self.projectiles.update()

        collidedict = groupcollide(
            self.P_COLLIDEANY_GROUP,
            self.projectiles,
            False,
            self.P_KILL_ON_COLLIDE,
            collided=collide_mask
        )
        if (collidedict):
            for k, _ in collidedict.items():
                if k == self.player:
                    self.P_player_collide_func(self.P_DAMAGE)
