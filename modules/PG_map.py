from random import randint

# installed library imports
from pygame import Color, Surface, Rect
from pygame.math import Vector2 as Vec2
from pygame.draw import line as draw_line, lines as draw_lines, rect as draw_rect
from pygame.sprite import Sprite, Group, GroupSingle, spritecollide, spritecollideany, collide_mask
from pygame.mask import Mask

## general classes
from .general.exceptions import ConfigError
## pygame specific classes
from .PG_player import Player
from .PG_block import Block
from .PG_timer import PG_Timer


class PG_Map:
    ''' current map setup used by the the app '''
    def __init__(self, cf_global: dict, cf_map: dict, surface: Surface, timer: PG_Timer):

        # self.cf_global = cf_global
        self.cf_global = cf_global
        self.cf_map = cf_map
        self.surface = surface
        self.timer = timer

        self.LOOP_LIMIT = int(cf_global['loop_limit'])
        self.DEBUG_COLOR = Color(cf_global['debug_color'])
        self.DEBUG_COLOR_2 = Color(cf_global['debug_color_2'])

        # store dict settings
        self.name = str(cf_map['name'])
        self.available_time = int(cf_map['available_time'])
        self.fill_color = Color(cf_map['fill_color'])
        self.n_obstacles = int(cf_map['n_obstacles'])
        self.gravity_m = float(cf_map['gravity_m'])
        self.gravity_c = float(cf_map['gravity_c'])
        self.mask_blit_color = self.fill_color

        # store nested dict settings
        self.cf_player: dict = cf_map['player']
        self.cf_blocks: dict = cf_map['blocks']

        self.rect = self.surface.get_rect()
        ''' rect of the map surface '''

        # combined groups
        self.block_group = Group()
        ''' combined group of constant, map-anchored rectangular sprites '''
        # specific groups
        self.obstacle_group = Group()
        ''' group specifically containing the randomly placed obstacle core blocks '''
        self.map_edge_group = Group()
        ''' group specifically containing the map surface outline blocks '''
        self.player_group = GroupSingle()
        ''' player sprite group. If a new sprite is added, the old is removed. '''
        
        self.DEBUG_DRAW_PLAYER = False

    def get_player_controls(self) -> dict[str, int]:
        ''' return a dict containing the player control keys '''
        return self.cf_player['controls']

    def get_rand_x(self, padding: int):
        ''' get random x-value within map left/right. Padding may be negative. '''
        return randint((self.rect.left + padding), (self.rect.right - padding))

    def get_rand_y(self, padding: int):
        ''' get random y-value within map top/bottom. Padding may be negative. '''
        return randint((self.rect.top + padding), (self.rect.bottom - padding))

    def get_rand_pos(self, padding_x: int, padding_y: int):
        ''' get a random position(x,y) within the map. Padding may be negative. '''
        return (self.get_rand_x(padding_x), self.get_rand_y(padding_y))

    def set_up_terrain(self):
        ''' specialized function for the creating the map terrain '''

        # outline the entire game bounds with terrain_blocks:
        terrain_facing = -1
        self.spawn_block_outline(
            self.cf_blocks['edge_outline'],
            self.map_edge_group,
            self.rect, terrain_facing, None
        )
        # add map bounds outline blocks to the general map group
        self.block_group.add(self.map_edge_group)

        # place obstacle_blocks within the game area
        self.spawn_obstacle_blocks(self.cf_blocks['obstacle'], self.obstacle_group)

        # outline the obstacles with smaller rects to create more jagged terrain
        terrain_facing = 1
        for BLOCK in self.obstacle_group:
            # for each block in obstacle_group, outline the block rect
            alt_pallette = [BLOCK.color]
            self.spawn_block_outline(
                self.cf_blocks['obstacle_outline'],
                self.obstacle_group, 
                BLOCK.rect, 
                terrain_facing,
                alt_pallette
            )

        # add obstacle blocks and their outline blocks to the general map group
        self.block_group.add(self.obstacle_group)

    def spawn_player(self, spawn_pos: tuple[int, int]):
        ''' create and spawn a player sprite
            * if a player already exists, replaces and removes it
            * updates the self.player reference
        '''
        # create the player sprite, then update player_group
        self.player = Player(self.cf_player, self.cf_map, self.cf_global, spawn_pos)
        self.player_group.add(self.player)

    def spawn_block_outline(self, cf_block: dict, group: Group, bounds: Rect,
                              facing: int, alt_pallette: None | list[Color]):

        ''' encapsulate the given rects' bounds with blocks
            * if alt_pallette is None, the block will use the cf_block color list at random
            * otherwise, choose the given color pallette for all blocks

            * facing decides the alignment of the blocks relative to the bounds axis':
            * -1 => inwards
            * 0  => center
            * 1  => outwards
        '''
        
        if (alt_pallette):
            color_pool = alt_pallette
        else:
            color_pool = cf_block['color_pool']

        # constant declarations for readability
        MIN_X = bounds.left
        MAX_X = bounds.right
        MIN_Y = bounds.top
        MAX_Y = bounds.bottom
        PADDING = int(cf_block['padding'])

        # below are four loops that together will outline the entire bounds
        # the loop places blocks in a clockwise path, following each axis
        # until a new bound is encountered, then swapping axis' and continuing
        # the first loop is explicit and commented, while the last three
        # are not, and are also slightly condensed. The logic is allround similar.
        # (they are way too specific to create a working generalized loop function, however)

        # last_block is for storing the last block placed when swapping axis'
        last_block: Block | None = None

        # 1) topleft --> topright
        curr_pos_x = MIN_X
        while curr_pos_x < MAX_X:
            # set random height/width from within the ranges
            width = randint(cf_block['min_width'], cf_block['max_width'])
            height = randint(cf_block['min_height'], cf_block['max_height'])

            # create a tuple to contain the position of the block
            position = (curr_pos_x, int(0))

            # ensure no edge overlap by checking for the last block:
            if (curr_pos_x + width) > MAX_X:
                # if the block will be last, adjust size before creating
                width = (MAX_X - curr_pos_x)

            # assemble the block
            BLOCK = Block(cf_block, self.cf_global, color_pool, (width, height), position)

            # adjust position according to facing
            match (facing):
                case (-1):
                    BLOCK.rect.top = MIN_Y
                case (0):
                    BLOCK.rect.centery = MIN_Y
                case (1):
                    BLOCK.rect.bottom = MIN_Y

            # add to the given group and update last block
            group.add(BLOCK)
            last_block = BLOCK

            # increment position for placing the next block
            curr_pos_x = (BLOCK.rect.right + PADDING)

        # 2) topright --> bottomright
        curr_pos_y = last_block.rect.bottom
        while curr_pos_y < MAX_Y:
            width = randint(cf_block['min_width'], cf_block['max_width'])
            height = randint(cf_block['min_height'], cf_block['max_height'])
            position = (int(0), curr_pos_y)
            if (curr_pos_y + height) > MAX_Y:
                height = MAX_Y - curr_pos_y

            BLOCK = Block(cf_block, self.cf_global, color_pool, (width, height), position)

            match (facing):
                case (-1):
                    BLOCK.rect.right = MAX_X
                case (0):
                    BLOCK.rect.centerx = MAX_X
                case (1):
                    BLOCK.rect.left = MAX_X
            last_block = BLOCK
            group.add(BLOCK)
            curr_pos_y = (BLOCK.rect.bottom + PADDING)

        # 3) bottomright --> bottomleft
        curr_pos_x = last_block.rect.left
        while curr_pos_x > MIN_X:
            width = randint(cf_block['min_width'], cf_block['max_width'])
            height = randint(cf_block['min_height'], cf_block['max_height'])
            position = (int(0), int(0))
            if (curr_pos_x - width) < MIN_X:
                width = abs(MIN_X - curr_pos_x)

            BLOCK = Block(cf_block, self.cf_global, color_pool, (width, height), position)
            BLOCK.rect.right = curr_pos_x

            match (facing):
                case (-1):
                    BLOCK.rect.bottom = MAX_Y
                case (0):
                    BLOCK.rect.centery = MAX_Y
                case (1):
                    BLOCK.rect.top = MAX_Y
            last_block = BLOCK
            group.add(BLOCK)
            curr_pos_x = (BLOCK.rect.left - PADDING)

        # 4) bottomleft --> topright
        curr_pos_y = last_block.rect.top
        while curr_pos_y > MIN_Y:
            width = randint(cf_block['min_width'], cf_block['max_width'])
            height = randint(cf_block['min_height'], cf_block['max_height'])
            position = (int(0), int(0))
            if (curr_pos_y - height) < MIN_Y:
                height = abs(MIN_Y - curr_pos_y)

            BLOCK = Block(cf_block, self.cf_global, color_pool, (width, height), position)
            BLOCK.rect.bottom = curr_pos_y

            match (facing):
                case (-1):
                    BLOCK.rect.left = MIN_X
                case (0):
                    BLOCK.rect.centerx = MIN_X
                case (1):
                    BLOCK.rect.right = MIN_X
            last_block = BLOCK
            group.add(BLOCK)
            curr_pos_y = (BLOCK.rect.top - PADDING)

    def spawn_obstacle_blocks(self, cf_block: dict, group: Group):
        ''' specialized obstacle spawning algorithm
            * checks for collision with the passed group and self.block_group before placing
        '''

        # padding, taking into account the player size to not completely block paths:
        H_PADDING = int(self.cf_player['surface']['height'] + cf_block['padding'])
        W_PADDING = int(self.cf_player['surface']['width'] + cf_block['padding'])
        color_pool = cf_block['color_pool']

        # initiate the loop
        placed_blocks = 0
        failed_attempts = 0
        while placed_blocks < self.n_obstacles:
            # set random height/width from within the ranges
            width = randint(cf_block['min_width'], cf_block['max_width'])
            height = randint(cf_block['min_height'], cf_block['max_height'])
            
            # get a random position within the map
            position = self.get_rand_pos(width, height)

            # assemble the block
            BLOCK = Block(cf_block, self.cf_global, color_pool, (width, height), position)

            # the block is now created, but there's 2 potential problems:
            # 1) the block might overlap other blocks
            # 2) we don't want to lock the player in by bad rng

            # solution: create a copy of the rect and inflate it using the player size + set padding
            inflated_rect = BLOCK.rect.copy().inflate(W_PADDING, H_PADDING)

            # temporarily swap the rect with the one of the block, while saving the original
            # this is to allow for easy and fast spritecollide checking
            original_rect = BLOCK.rect.copy()
            BLOCK.rect = inflated_rect

            # if the block + player rect doesn't collide with any terrain, add it to the group
            if not (spritecollideany(BLOCK, self.block_group) or (spritecollideany(BLOCK, group))):
                # block doesn't collide with anything, swap rect back and add block
                BLOCK.rect = original_rect
                group.add(BLOCK)
                placed_blocks += 1
            else:
                # otherwise, free (delete) the sprite and try again
                del BLOCK
                failed_attempts += 1
                # check if attempt limit is reached
                if (failed_attempts > self.LOOP_LIMIT):
                    msg = f'\
                        Fail limit of {self.LOOP_LIMIT} attempts reached.\
                        Too many or too large obstacles.\n\
                        block padding set too high can also be the cause.\
                        Current obstacle count: {placed_blocks} / {self.n_obstacles}'
                    raise ConfigError(msg, cf_block)

            # make sure the copied temp rect is not saved in memory
            del inflated_rect

    def get_rect_offset(self, rect_1: Rect, rect_2: Rect):
        ''' finds the offset between two sprites rects '''
        offset_x = (rect_1.x - rect_2.x)
        offset_y = (rect_1.y - rect_2.y)
        return (offset_x, offset_y)

    def get_largest_mask_component_bounds(self, mask: Mask):
        ''' get the bounding rect of the largest connected component within the mask '''

        bounding_rects: list[Rect] = mask.get_bounding_rects()
        # when called directly, get_bounding_rects calls connected_components(),
        # with a threshhold of only one pixel for each component
        # https://www.pygame.org/docs/ref/mask.html#pygame.mask.Mask.connected_components

        largest_re = bounding_rects[0]

        # typically there's only one rect, but theoretically there could be many.
        if (len(bounding_rects) > 1):
            # UNTESTED CASE
            print('[draw_mask_bounds]: found more than one c-component in mask')

            # iterate over rects and find the largest one
            for re in bounding_rects:
                if ((re.w * re.h) > (largest_re.w * largest_re.h)):
                    largest_re = re

        return largest_re

    def get_sprite_mask_overlap(self, sprite_1, sprite_2) -> Mask:
        ''' returns a new mask covering the overlapping area of two sprites
            * returns a new mask covering only the overlapping area
        '''
        offset = self.get_rect_offset(sprite_1.rect, sprite_2.rect)
        overlap_mask = sprite_2.mask.overlap_mask(sprite_1.mask, offset)
        return overlap_mask

    def get_collision_center(self, sprite_1, sprite_2):
        ''' for two overlapping sprites, finds the center of mask collision
            * returns the center of this area as a vector2
        '''
        overlap = self.get_sprite_mask_overlap(sprite_1, sprite_2)
        overlap_rect = overlap.get_rect(topleft=(sprite_2.rect.x, sprite_2.rect.y))
        collidepos = Vec2(overlap_rect.center)

        return collidepos

    def blit_overlap_mask(self, sprite_1, sprite_2):
        dest_pos = (sprite_2.rect.x, sprite_2.rect.y)
        overlap_mask = self.get_sprite_mask_overlap(sprite_1, sprite_2)
        MASK_SURF = overlap_mask.to_surface(unsetcolor=(0, 0, 0, 0), setcolor=self.mask_blit_color)
        self.surface.blit(MASK_SURF, dest_pos)

    def blit_block_player_overlap(self):
        # before checking masks, perform a simple collision check using rects
        if (spritecollideany(self.player, self.block_group)):
            # get list of colliding masks
            collidelist = spritecollide(self.player, self.block_group, False, collided=collide_mask)
            for BLOCK in collidelist:
                self.blit_overlap_mask(self.player, BLOCK)

    def check_player_block_collide(self):
        ''' if player collides with a block, init the recoil sequence for the player '''
        # case 0: ignore action if player has no mass
        if (self.player.MASS):
            # case 1: player is not in recoil or cooldown phase, and rects collide
            if (self.player.collision_cooldown_frames_left):
                # player has active recoil or cooldown frames
                self.blit_block_player_overlap()
            elif (spritecollideany(self.player, self.block_group)):
                # get list of colliding masks
                collidelist = spritecollide(self.player, self.block_group, False, collided=collide_mask)
                if (len(collidelist)):
                    # init player recoil phase
                    self.player.init_collision_recoil()
                    # highlight blocks that player collided with
                    for BLOCK in collidelist:
                        BLOCK.init_timed_highlight()
        else:
            # player has no mass. draw the overlap
            self.blit_block_player_overlap()

    def draw_sprites(self):
        ''' fill map surface. draw all sprites. check if drawing resulted in collisions. '''
        self.surface.fill(self.fill_color)
        if (self.DEBUG_DRAW_PLAYER):
            self.debug__draw_player_all_info()
        else:
            self.player_group.draw(self.surface)
        self.block_group.draw(self.surface)

    def check_for_collisions(self):
        ''' since collision is based on image masks, call this after draw, but before update '''
        self.check_player_block_collide()



    def debug__draw_player_all_info(self):
        # mask debug draws apply to the sprites' temp image, so call before blitting that image
        self.debug__draw_mask_center_mass(self.player)
        self.debug__draw_mask_bounds(self.player)
        self.player_group.draw(self.surface)
        # general debugging calls use the map surface instead, so call them post-draw.
        # (they may extend the image of the sprite, so no way to draw them to the sprite image)
        self.debug__draw_sprite_velocity(self.player, 40.0, 1)
        self.debug__draw_sprite_acceleration(self.player, 40.0, 1)
        self.debug__outline_rect(self.player)

    def debug__draw_sprite_acceleration(self, sprite: Sprite, len: float, width: int):
        ''' visualize sprite acceleration from its position '''
        p1 = Vec2(sprite.position)
        p2 = Vec2(sprite.position + (len * sprite.acceleration))
        draw_line(self.surface, self.DEBUG_COLOR_2, p1, p2, width)

    def debug__draw_sprite_velocity(self, sprite: Sprite, len: float, width: int):
        ''' visualize sprite velocity from its position '''
        p1 = Vec2(sprite.position)
        p2 = Vec2(sprite.position + (len * sprite.velocity))
        draw_line(self.surface, self.DEBUG_COLOR, p1, p2, width)

    def debug__outline_mask(self, sprite: Sprite):
        ''' visualize mask outline by drawing lines along the set pixel points '''
        p_list = sprite.mask.outline()  # get a list of cooordinates from the mask outline
        # print(f'n_points in mask: {len(p_list)}')
        if (p_list):
            draw_lines(sprite.image, self.DEBUG_COLOR, 1, p_list)

    def debug__outline_rect(self, sprite: Sprite):
        ''' draw a border around the sprite bounding rect '''
        draw_rect(self.surface, self.DEBUG_COLOR, sprite.rect, width=1)

    def debug__draw_mask_bounds(self, sprite: Sprite):
        ''' draw the actual bounding rect of the player mask '''
        mask_bounds = self.get_largest_mask_component_bounds(sprite.mask)
        draw_rect(sprite.image, self.DEBUG_COLOR_2, mask_bounds, width=1)

    def debug__draw_mask_center_mass(self, sprite: Sprite):
        ''' visualize the actual mask bounds by drawing an interesction through it
            * only works if 8 or moore pixels are connected
        '''
        sprite_mask: Mask = sprite.mask
        mask_bounds = self.get_largest_mask_component_bounds(sprite_mask)
        if mask_bounds == None:
            print('[draw_mask_center_mass]: failed finding connected component')
            return

        mask_center = sprite_mask.centroid()

        line_1_p1 = mask_center
        line_1_p2 = mask_bounds.midtop
        line_2_p1 = mask_center
        line_2_p2 = mask_bounds.midright
        line_3_p1 = mask_center
        line_3_p2 = mask_bounds.midleft
        line_4_p1 = mask_center
        line_4_p2 = mask_bounds.midbottom

        draw_line(self.player.image, self.DEBUG_COLOR_2, line_1_p1, line_1_p2, width=1)
        draw_line(self.player.image, self.DEBUG_COLOR_2, line_2_p1, line_2_p2, width=1)
        draw_line(self.player.image, self.DEBUG_COLOR_2, line_3_p1, line_3_p2, width=1)
        draw_line(self.player.image, self.DEBUG_COLOR_2, line_4_p1, line_4_p2, width=1)

    def __str__(self):
        msg = f'< Map with name="{self.name}"\n'
        msg += f'topleft[x,y] = {self.rect.topleft}\n'
        msg += f'size[w,h] = [{self.rect.w}, {self.rect.h} >\n'
        return msg


# collidepos = self.get_collision_center(self.player, LIST[0])
# print(f'collidepos: {collidepos}')
# player_mask_re = self.get_largest_mask_component_bounds(self.player.mask)
# weight = Vec2(player_mask_re.center).distance_to(collidepos)
# self.player.init_collision_recoil(weight)
