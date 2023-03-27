from .cf_colors import RGB

MISC = {
    # req_pygame_version:
    #   the required pygame version for the app. will be verified on init.
    #   set this value to your installed version if you would like to try running anyways
    'req_pg_version': str('2.3.0'),
    # loop_limit:
    #   General loop limit, mainly for debugging and configuration purposes.
    #   In effect, set how many failed attempts to allow when performing pseudorandom
    #   algorithms that have a chance to not being capable of success, depending on settings.
    #   Avoids program crash by breaking out of loops that would never finish,
    #   and can be useful to print how close an algorithm was to success.
    'loop_limit':       int(10000),
    # debug_color: high contrast color used for visualizing certain screen elements
    #   should not occur anywhere else on the screen. 
    #   Do not use black as screen defaults to black.
    'debug_color':      RGB['uranianblue'],
    # fps_limit:
    #   due to how tick works with sync limitations, especially at higher values,
    #   fps should be set to one of the following values: [30, 62, 125, 200, 250]
    #   any value will work, but in essence, it will not actually sync correctly to other values
    #   this can be checked by setting accurate_timing to true
    #   for example, when trying to set an FPS of 220, it will automatically snap to 250 instead.
    #   (i'm not entirely sure why this happens, but it's not really an issue.)
    #   setting FPS to 0 will leave it uncapped
    'fps_limit':        int(125),      # default: 125
    # accurate_timing:
    #   how strict the time tick function should be.
    #   Uses more resources if set to true
    #   docref: https://www.pygame.org/docs/ref/time.html#pygame.time.Clock.tick_busy_loop
    'accurate_timing':  True,    # default: True
}
''' various settings that didnt fit in anywhere else '''
