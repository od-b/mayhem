from typing import Callable
from pygame import time, event, Surface
from pygame.sprite import Sprite, Group, GroupSingle
from pygame.event import Event

from .timer import Timer
from .PG_ui_text_box import UI_Text_Box
from .PG_ui_container import UI_Sprite_Container

class PG_Timer(Timer):
    ''' Segment based time tracking. Extends .general/Timer
        * relies on the pygame clock to provide time values
        * update must be called every frame to yield the correct time values
        * Tracking activates when .start_first_segment() is called, not on __init__
        * >> start_first_segment MUST be called before ANY other methods are called.
        * the timer also has methods to customize events
    '''

    def __init__(self, cf_global: dict, cf_timer: dict):
        super().__init__()
        
        self.cf_global = cf_global
        self.cf_timer = cf_timer

        self.FPS_LIMIT = int(self.cf_global['fps_limit'])
        self.busy_loop = self.cf_timer['accurate_timing']
        self.clock = time.Clock()
        self.first_init_done: bool = False
        self.custom_events = []
        self.blocked_events = []

        # create a function pointer instead of checking conditions every frame
        if (self.busy_loop):
            self.tick_func: Callable = self.clock_tick_busy
        else:
            self.tick_func: Callable = self.clock_tick
        
        self.container_group = GroupSingle()

        cf_text_container = self.cf_timer['text_box_container']
        self.TEXT_CONTAINER = UI_Sprite_Container(
            cf_text_container['position'],
            cf_text_container['size'],
            cf_text_container['child_anchor'],
            cf_text_container['child_align_x'],
            cf_text_container['child_align_y'],
            cf_text_container['child_padding_x'],
            cf_text_container['child_padding_y']
        )
        self.container_group.add(self.TEXT_CONTAINER)
        
        self.set_up_textboxes()

    def set_up_textboxes(self):
        if (self.cf_timer['display_fps_text']):
            FPS_TEXT = UI_Text_Box(
                self.cf_timer['fps_text_style'],
                self.cf_global,
                ["FPS", "TEXT_BOX", "CONST"],
                'FPS: ',
                self.get_fps_string,
                self.TEXT_CONTAINER.rect.center
            )
            self.TEXT_CONTAINER.add_child(FPS_TEXT)

        if (self.cf_timer['display_segment_time_text']):
            DURATION_TEXT = UI_Text_Box(
                self.cf_timer['segment_time_text_style'],
                self.cf_global,
                ["DURATION", "TEXT_BOX", "CONST"],
                'Time: ',
                self.get_segment_duration_formatted,
                self.TEXT_CONTAINER.rect.center
            )
            self.TEXT_CONTAINER.add_child(DURATION_TEXT)

    def new_segment(self, ref: int | None, archive_active_segment: bool):
        ''' overwrites parent method.
            * since this subclass has an internal clock, handles time parameters
        '''
        if (self.first_init_done):
            super().new_segment(ref, archive_active_segment)
        else:
            self.first_init_done = True
            # tick to allow getting the current time from time.get_ticks()
            self.tick_func()
            curr_time = time.get_ticks()
            super().start_first_segment(curr_time, ref)

    def get_custom_events(self):
        return self.custom_events

    def get_blocked_events(self):
        return self.blocked_events

    def get_segment_duration(self):
        return self.active_segment.get_duration_int()

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
            * sec_interval: updates per second
            * n_loops = 0 => don't stop looping
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

    def get_fps_string(self):
        ''' get fps as a string, no decimals '''
        return str(int(self.clock.get_fps()))

    def clock_tick(self):
        ''' only tick the clock to keep track of time '''
        self.clock.tick(self.FPS_LIMIT)

    def clock_tick_busy(self):
        ''' tick the clock to keep track of time and limit time to next frame.
            More accurate than clock_tick, but consumes more resources
        '''
        self.clock.tick_busy_loop(self.FPS_LIMIT)

    def draw_ui(self, surface):
        ''' updates and draws FPS text, time text, etc., if set to be displayed. '''
        self.container_group.update(surface)

    def update(self):
        ''' overwrites parent method. 
            * Ticks pygame clock and increments segment timestamp
        '''
        # update the pygame clock
        self.tick_func()
        # call parent update with the updated time
        curr_time = time.get_ticks()
        super().update(curr_time)

