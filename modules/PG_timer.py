from pygame import time
from .timing import Timer
from typing import Callable

class PG_Timer(Timer):
    ''' Segment based time tracking. Extends Timer.
        * relies on the pygame clock to provide time values
        * update must be called every frame to yield the correct time values
        * Tracking activates when .start_first_segment() is called, not on __init__
        * >> start_first_segment MUST be called before ANY other methods are called.
    '''

    def __init__(self, fps_limit: int, busy_loop: bool):
        super().__init__()
        self.fps_limit = fps_limit
        self.busy_loop = busy_loop
        self.clock = time.Clock()

        # create a function pointer instead of checking conditions every frame
        if (self.busy_loop):
            self.tick_func: Callable = self.clock_tick_busy
        else:
            self.tick_func: Callable = self.clock_tick

    def activate_busy_tick(self):
        ''' sets tick function to busy loop. Consumes more CPU, but more accurate '''
        self.tick_func = self.clock_tick_busy

    def activate_normal_tick(self):
        ''' sets tick function to regular '''
        self.tick_func = self.clock_tick

    def get_duration(self):
        ''' to allow referencing the function before first segment is initialized '''
        return self.active_segment.get_duration_formatted()

    def get_fps_int(self):
        ''' get fps as an integer '''
        return int(self.clock.get_fps())

    def clock_tick(self):
        ''' only tick the clock to keep track of time '''
        self.clock.tick(self.fps_limit)

    def clock_tick_busy(self):
        ''' tick the clock to keep track of time and limit time to next frame.
            More accurate than clock_tick, but consumes more resources
        '''
        self.clock.tick_busy_loop(self.fps_limit)

    def start_first_segment(self, ref: int | None):
        ''' overwrites parent method.
            * since this subclass has an internal clock, handles time parameters
        '''
        self.tick_func()
        curr_time = time.get_ticks()
        super().start_first_segment(curr_time, ref)

    def update(self):
        ''' overwrites parent method. 
            * Ticks pygame clock and increments segment timestamp
        '''
        # update the pygame clock
        self.tick_func()
        # call parent update with the updated time
        curr_time = time.get_ticks()
        super().update(curr_time)
