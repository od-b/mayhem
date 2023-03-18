#
# nothing is tested here
#


class Segment:
    ''' reference can be for example a given map/challenge '''
    def __init__(self, start: int, reference: int | None):
        self.reference: int | None = reference
        self.start: int = start
        self.duration: int = 0

    def update_duration(self, curr_time: int):
        self.duration = (curr_time - self.start)


class Timer:
    ''' Segment based time tracking.
        Activates when Timer.start_first_segment() is called, not on Timer.__init__ '''
    def __init__(self):
        self.start_time: int = 0
        self.total_time: int = 0
        self.active_segment: Segment | None = None
        self.segments: list[Segment] = []
        self.n_segments: int = 0
    
    def get_active_segment_time(self):
        return self.active_segment.duration

    def start_first_segment(self, curr_time: int, ref: int | None):
        self.start_time = curr_time
        self.active_segment = Segment(curr_time, ref)

    def new_segment(self, ref: int | None, archive_curr: bool):
        if (archive_curr):
            self.segments.append(self.active_segment)
            self.n_segments += 1
        self.active_segment = Segment(self.total_time, ref)

    def get_fastest_segment(self, ref: int | None):
        fastest_time: int | None = None
        if not ref:
            for seg in self.segments:
                if (not fastest_time) or (seg.duration < fastest_time):
                    fastest_time = seg.duration
        else:
            for seg in self.segments:
                if (seg.reference == ref):
                    if (not fastest_time) or (seg.duration < fastest_time):
                        fastest_time = seg.duration
        
        return fastest_time

    def delete_segments_by_ref(self, ref: int):
        for seg in self.segments:
            if (seg.reference == ref):
                self.segments.remove(seg)

    def delete_all_segments(self):
        self.segments = []
        self.n_segments = 0

    def full_reset(self, curr_time: int):
        self.delete_all_segments()
        self.start_time = curr_time
        self.total_time = 0

    # TODO
    def total_curr_sync_ms(self):
        # prob looks weird when seconds are flip flopping on different ms timers
        pass

    def update(self, curr_time: int):
        # update total time
        self.total_time = (curr_time - self.start_time)
        # update segment time
        self.active_segment.update_duration(curr_time)


# TODO
class FPS_Based_Timer(Timer):
    # fps based timer instead of using actual time
    pass
