from random import randint

# installed library imports
from pygame import Color, Surface, Rect
from pygame.sprite import Group, GroupSingle, spritecollide, spritecollideany, collide_mask

## general classes
from .general.exceptions import ConfigError
## pygame specific classes
from .PG_player import Player
from .PG_block import Block


class PG_Map:
    ''' current map setup used by the the app '''
    def __init__(self, cf_global: dict, cf_map: dict, surface: Surface):

        self.cf_global = cf_global
        self.LOOP_LIMIT = cf_global['loop_limit']
        self.surface = surface

        # store dict settings
        self.cf_map = cf_map
        self.name = str(cf_map['name'])
        self.available_time = int(cf_map['available_time'])
        self.fill_color = Color(cf_map['fill_color'])
        self.n_obstacles = int(cf_map['n_obstacles'])
        self.gravity_m = float(cf_map['gravity_m'])
        self.gravity_c = float(cf_map['gravity_c'])

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
        terrain_facing = 0
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

    def fill_surface(self):
        ''' fills/resets the map surface '''
        self.surface.fill(self.fill_color)

    def check_player_block_collide(self):
        ''' get a list of sprites that collide with the player
            * uses collide_mask()
        '''

        LIST: list[Block] = spritecollide(self.player, self.block_group, False, collided=collide_mask)
        if (len(LIST)):
            for BLOCK in LIST:
                BLOCK.init_highlight()

            # if not (self.player.crash_frames):
            #     self.player.init_collision_recoil()
            while (collide_mask(self.player, BLOCK)):
                self.player.position -= (2.0 * self.player.velocity)
                self.player_group.update()
                self.player_group.draw(self.surface)

            # offset = (self.player.width/2, self.player.height/2)
            # collidepos = self.player.mask.overlap(BLOCK.mask, offset)
            # print(collidepos)
            # self.player.handle_terrain_collision(collidepos)

    def __str__(self):
        msg = f'< Map with name="{self.name}"\n'
        msg += f'topleft[x,y] = {self.rect.topleft}\n'
        msg += f'size[w,h] = [{self.rect.w}, {self.rect.h} >\n'
        return msg
