from pygame import time
from .timing import Timer

class PG_Timer(Timer):
    ''' timer that uses the pygame clock for updates. Subclass of Timer '''
    def __init__(self, max_fps):
        super().__init__()
        self.max_fps = max_fps
        self.clock = time.Clock
        # create a function pointer instead of checking condition every frame
        if (type(self.max_fps) == int):
            self.clock_update_func = self.clock_tick_limit_fps
        else:
            self.clock_update_func = self.clock_tick
        # misc

    def get_duration(self):
        ''' to allow referencing the function before first segment is initialized '''
        return self.active_segment.get_duration_formatted()

    def get_fps_int(self):
        ''' get fps, rounded to the nearest integer '''
        return round(self.clock.get_fps(), None)

    def clock_tick_limit_fps(self):
        ''' tick the clock to keep track of time and limit time to next frame '''
        self.clock.tick(self.max_fps)

    def clock_tick(self):
        ''' only tick the clock to keep track of time '''
        self.clock.tick()
    
    def update(self):
        self.clock_update_func()
        super().update(time.get_ticks())
