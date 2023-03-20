from pygame import time
from .timing import Timer

class PG_Timer(Timer):
    ''' timer that uses the pygame clock for updates. Subclass of Timer '''
    def __init__(self, fps_limit):
        super().__init__()
        self.fps_limit = fps_limit
        self.clock = time.Clock()
        # create a function pointer instead of checking condition every frame
        if (type(self.fps_limit) == int):
            self.clock_update_func = self.clock_tick_limit_fps
        else:
            self.clock_update_func = self.clock_tick

    def get_duration(self):
        ''' to allow referencing the function before first segment is initialized '''
        return self.active_segment.get_duration_formatted()

    def get_fps_int(self):
        ''' get fps, rounded to the nearest integer '''
        return round(self.clock.get_fps(), None)

    def clock_tick_limit_fps(self):
        ''' tick the clock to keep track of time and limit time to next frame '''
        self.clock.tick(self.fps_limit)

    def clock_tick(self):
        ''' only tick the clock to keep track of time '''
        self.clock.tick()

    def start_first_segment(self, ref: int | None):
        ''' overwriting parent method '''
        self.clock_update_func()
        curr_time = time.get_ticks()
        super().start_first_segment(curr_time, ref)
    
    def update(self):
        ''' overwrites parent method. Updates pygame clock and increments segment time '''
        # update the pygame clock
        self.clock_update_func()
        # call parent update with the updated time
        curr_time = time.get_ticks()
        super().update(curr_time)
