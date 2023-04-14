from os.path import join as os_path_join
from .colors import RGB, RGBA, PALLETTES

CF_BLOCKS = {
    #   color_pool: list of one ore more RGB color values
    #   spacing:
    #       integer ∈ (0 <= spacing < min(max_width, max_height))
    #       pixels inbetween similar type blocks when placed
    #   mass: 
    #       how 'tough' the blocks are. Used for collision responses
    #       a block with mass of 0 will ignore all collision with controllables
    'pastel_block': {
        'mass':             float(0),
        'spacing':          int(130),
        'min_height':       int(10),
        'max_height':       int(80),
        'min_width':        int(8),
        'max_width':        int(90),
        'color_pool':       PALLETTES['PASTEL_MIX'],
        'alpha_key':        int(255),
        'border_color':     None,
        'border_width':     int(0),
        # alt_surface may be None or a subdict as below
        'alt_surface': {
            'color':        RGB['signal_red'],
            'border_color': None,
            'duration':     int(3000),  # duration in ms once triggered
        },
    },
    'adaptive_block': {
        'mass':             float(0),
        'spacing':          int(0),
        'min_height':       int(10),
        'max_height':       int(16),
        'min_width':        int(8),
        'max_width':        int(20),
        'color_pool':       None,
        'alpha_key':        int(255),
        'border_color':     None,
        'border_width':     int(0),
        'alt_surface': {
            'color':        RGB['signal_red'],
            'border_color': None,
            'duration':     int(3000),  # duration in ms once triggered
        },
    },
    'small_gray_block': {
        'mass':             float(0),
        'spacing':          int(0),
        'min_height':       int(10),
        'max_height':       int(16),
        'min_width':        int(8),
        'max_width':        int(22),
        'color_pool':       PALLETTES['SHADES_OF_GRAY'],
        'alpha_key':        int(255),
        'border_color':     None,
        'border_width':     int(0),
        'alt_surface': {
            'color':        RGB['signal_red'],
            'border_color': None,
            'duration':     int(3000),  # duration in ms once triggered
        },
    },
}


CF_COINS = {
    'default': {
        'spritesheet_path': os_path_join('assets','spritesheets','coin_1.png'),
        'image_variants': int(9),
        'image_scalar': float(0.1),
        'min_img_iter_frequency': float(0.11),
        'max_img_iter_frequency': float(0.13)
    }
}

CF_PROJECTILES = {
    'missile': {
        'spritesheet': {
            'path': os_path_join('assets','spritesheets','projectiles','missile.png'),
            'n_images': int(4)
        },
        'img_cycle_frequency': int(0),
        'image_scalar': float(1.0),
        'damage': float(10)
    }
}

CF_PROJECTILE_SPAWNERS = {
    'missile_x1': {
        'rate_of_fire': int(60), # irrelevant if only one projectile at a time
        'sleep_duration': int(80),
        'n_projectiles_before_sleep': int(1),
        'cf_projectile': CF_PROJECTILES['missile']
    },
    'missile_x2': {
        'rate_of_fire': int(60),
        'sleep_duration': int(125),
        'n_projectiles_before_sleep': int(2),
        'cf_projectile': CF_PROJECTILES['missile']
    },
    'missile_x4': {
        'rate_of_fire': int(45),
        'sleep_duration': int(180),
        'n_projectiles_before_sleep': int(4),
        'cf_projectile': CF_PROJECTILES['missile']
    },
}

CF_TURRETS = {
    'missile_launcher_x1': {
        # shoots a single missile at a set interval while rotating; never stops rotating
        'cf_projectile_spawner': CF_PROJECTILE_SPAWNERS['missile_x1'],
        'rotation_rate': float(-0.15),
        'image_scalar': float(0.25),
        'delay_before_shooting': int(0),
        'delay_after_shooting': int(0),
        'projectile_magnitude': float(1.0),
        'spritesheet': {
            'path': os_path_join('assets','spritesheets','turrets','single','idle.png'),
            'n_images': int(1),
        },
    },
    'missile_launcher_x2': {
        # shoots 2 consecutive missiles while rotating
        'cf_projectile_spawner': CF_PROJECTILE_SPAWNERS['missile_x2'],
        'rotation_rate': float(-0.1),
        'image_scalar': float(0.25),
        'delay_before_shooting': int(5),
        'delay_after_shooting': int(3),
        'projectile_magnitude': float(1.0),
        'spritesheet': {
            'path': os_path_join('assets','spritesheets','turrets','single','idle.png'),
            'n_images': int(1),
        },
    },
    'missile_launcher_x4': {
        # shoots 4 consecutive missiles while rotating
        'cf_projectile_spawner': CF_PROJECTILE_SPAWNERS['missile_x4'],
        'rotation_rate': float(0.18),
        'image_scalar': float(0.25),
        'delay_before_shooting': int(0),
        'delay_after_shooting': int(0),
        'projectile_magnitude': float(0.5),
        'spritesheet': {
            'path': os_path_join('assets','spritesheets','turrets','single','idle.png'),
            'n_images': int(1),
        },
    }
}
