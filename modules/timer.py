
class Segment:
    ''' Time segment created and used by Timer
        * ref is an ID of sort. can be for example a given map/challenge/algorithm
        * ref can be None if separating segment types is not needed
    '''

    def __init__(self, start: int, ref):
        self.ref = ref
        self.start = start
        self.duration = int(0)
        self.paused = False
        self.pause_timestamp = int(0)

    def pause(self):
        self.pause_timestamp = int(self.duration)

    def unpause(self, curr_time):
        self.update_duration(curr_time)
        time_diff = int(self.duration - self.pause_timestamp)
        self.start += time_diff 

    def get_duration(self):
        ''' returns milliseconds that have passed since segment started '''
        return self.duration

    def update_duration(self, curr_time: int):
        ''' increments duration of segment '''
        self.duration = (curr_time - self.start)


class Timer:
    ''' Segment based time tracking.
        * relies on an external clock to provide values through update
        * Tracking activates when .start_first_segment() is called, not on __init__
        * >> start_first_segment MUST be called before ANY other methods are called.
    '''

    def __init__(self):
        self.start_time: int = 0
        self.total_time: int = 0
        self.active_segment: Segment | None = None
        self.segments: list[Segment] = []

    def start_first_segment(self, curr_time: int, ref: int | None):
        ''' initialize the first segment '''
        self.start_time = curr_time
        self.active_segment = Segment(curr_time, ref)

    def new_segment(self, ref, archive_active_segment: bool):
        ''' start a new segment with the given ref
            * choose whether to archive or delete current active segment
        '''
        if (archive_active_segment):
            self.segments.append(self.active_segment)
        else:
            del self.active_segment
        self.active_segment = Segment(self.total_time, ref)

    def get_fastest_archived_segment(self, ref):
        ''' get fastest segment with a specific ref.
            * if ref is None, returns fastest segment with any ref
            * returns None if there are no matching segments
        '''
        fastest_time: int | None = None
        if (ref == None):
            for seg in self.segments:
                if (not fastest_time) or (seg.duration < fastest_time):
                    fastest_time = seg.duration
        else:
            for seg in self.segments:
                if (seg.ref == ref):
                    if (not fastest_time) or (seg.duration < fastest_time):
                        fastest_time = seg.duration
        
        return fastest_time

    def get_segment_duration_formatted(self):
        ''' Formats from milliseconds to a readable format
            * returns <mm:ss>, or <hh:mm:ss> if hh > 0 
        '''
        T = self.active_segment.duration
        secs = int(T/1000) % 60
        mins = int(T/(1000*60)) % 60
        hours = int(T/(1000*60*60)) % 24
        if hours == 0:
            return f'{mins:02d}:{secs:02d}'
        return f'{hours:02d}:{mins:02d}:{secs:02d}'

    def delete_archived_segments_by_ref(self, ref: int):
        ''' delete all segments with a given reference'''
        for seg in self.segments:
            if (seg.ref == ref):
                self.segments.remove(seg)
                del seg

    def delete_all_archived_segments(self):
        ''' delete all segments '''
        for seg in self.segments:
            del seg
        self.segments = []

    def full_reset(self):
        ''' resets everything, start_first_segment must be recalled when ready '''
        self.delete_all_archived_segments()
        self.start_time = 0
        self.total_time = 0
        self.active_segment = None

    def update(self, curr_time: int):
        ''' update total time and active segment duration '''
        self.total_time = (curr_time - self.start_time)
        self.active_segment.update_duration(curr_time)
