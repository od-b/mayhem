from typing import Callable
from pygame import time, event
from pygame.event import Event
from .general.timer import Timer


class PG_Timer(Timer):
    ''' Segment based time tracking. Extends .general/Timer
        * relies on the pygame clock to provide time values
        * update must be called every frame to yield the correct time values
        * Tracking activates when .start_first_segment() is called, not on __init__
        * >> start_first_segment MUST be called before ANY other methods are called.
        * the timer also has methods to customize events
    '''

    def __init__(self, fps_limit: int, busy_loop: bool):
        super().__init__()
        self.fps_limit = int(fps_limit)
        self.busy_loop = busy_loop
        self.clock = time.Clock()
        self.first_init_done: bool = False
        self.custom_events = []
        self.blocked_events = []

        # create a function pointer instead of checking conditions every frame
        if (self.busy_loop):
            self.tick_func: Callable = self.clock_tick_busy
        else:
            self.tick_func: Callable = self.clock_tick

    def start_first_segment(self, ref: int | None):
        ''' overwrites parent method.
            * since this subclass has an internal clock, handles time parameters
        '''
        self.first_init_done = True
        self.tick_func()
        curr_time = time.get_ticks()
        super().start_first_segment(curr_time, ref)

    def get_custom_events(self):
        return self.custom_events

    def get_blocked_events(self):
        return self.blocked_events

    def allow_event(self, event_id):
        event.set_allowed(event_id)
        if (event_id) in self.blocked_events:
            self.blocked_events.remove(event_id)

    def block_events(self, events: list):
        ''' blocks the given events from entering the event queue
            * saves some time when iterating over pg.event.get()
            * custom added events can be removed through this function
            * blocked events are stored in self.blocked_events
        '''
        for EVENT_ID in events:
            event.set_blocked(EVENT_ID)
            self.blocked_events.append(EVENT_ID)

    def create_event_timer(self, ms_interval: int, n_loops: int):
        ''' creates a custom event+timer with an unique integer reference
            * returns the assigned event id
        '''
        EVENT_ID = event.custom_type()
        self.custom_events.append(EVENT_ID)
        time.set_timer(EVENT_ID, ms_interval, loops=n_loops)
        return EVENT_ID

    def post_event(self, event_id):
        event.post(Event(event_id))

    def activate_busy_tick(self):
        ''' sets tick function to busy loop. Consumes more CPU, but more accurate '''
        self.tick_func = self.clock_tick_busy

    def activate_normal_tick(self):
        ''' sets tick function to regular '''
        self.tick_func = self.clock_tick

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

    def update(self):
        ''' overwrites parent method. 
            * Ticks pygame clock and increments segment timestamp
        '''
        # update the pygame clock
        self.tick_func()
        # call parent update with the updated time
        curr_time = time.get_ticks()
        super().update(curr_time)
