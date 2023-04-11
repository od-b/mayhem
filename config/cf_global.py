from .colors import RGB, RGBA
import pygame as pg

CF_GLOBAL = {
    # req_pygame_version:
    #   the required pygame version for the app. will be verified on init.
    #   set this value to your installed version if you would like to try running anyways
    'req_pg_version': {
        'vernum': (2, 3, 0),
        'string': "2.3.0"
    },
    # loop_limit:
    #   General loop limit, mainly for debugging and configuration purposes.
    #   In effect, set how many failed attempts to allow when performing pseudorandom
    #   algorithms that have a chance to not being capable of success, depending on settings.
    #   Avoids program crash by breaking out of loops that would never finish,
    #   and can be useful to print how close an algorithm was to success.
    'loop_limit': int(10000),
    # debug_color: high contrast color used for visualizing certain screen elements
    'debug_color': RGB['white'],
    'debug_color_2': RGB['purple'],
    # fully transparent color
    'transparent_color': RGBA['alpha_0'],
    # fps_limit:
    #   due to how tick works with sync limitations, especially at higher values,
    #   fps should be set to one of the following values: [30, 62, 125, 200, 250]
    #   any value will work, but in essence, it will not actually sync correctly to other values
    #   this can be checked by setting accurate_timing to true
    #   for example, when trying to set an FPS of 220, it will automatically snap to 250 instead.
    #   (i'm not entirely sure why this happens, but it's not really an issue.)
    #   fps limit must be set to a value for sprites to behave properly
    'fps_limit': int(125),      # default: 125
    # blocked_events are a list of pg.event.type that will be blocked from the event queue
    # improves performance slightly by not needing to iterate over events that are unused
    'blocked_events': [
        pg.TEXTINPUT
    ],
}
''' various settings that didnt fit in anywhere else, or are needed for multiple objects '''
