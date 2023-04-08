from .cf_window import CF_WINDOW
from .ui_components import CF_TEXT_BOXES


TEXT_BOX_CONTAINER_WIDTH = int(200)
TEXT_BOX_CONTAINER_HEIGHT = int(200)

# position the container top left of the window + offset
TEXT_BOX_CONTAINER_X = int(CF_WINDOW['width'] - TEXT_BOX_CONTAINER_WIDTH - 50)
TEXT_BOX_CONTAINER_Y = int(14)

CF_TIMER = {
    # accurate_timing:
    #   how strict the time tick function should be.
    #   Uses more resources if set to true
    #   docref: https://www.pygame.org/docs/ref/time.html#pygame.time.Clock.tick_busy_loop
    'accurate_timing':  True,                # default: True
    'display_fps_text': True,
    'display_segment_time_text': True,
    'fps_text_style': CF_TEXT_BOXES['semibold_bone_offblack'],
    'segment_time_text_style': CF_TEXT_BOXES['semibold_bone_offblack'],
    'text_box_container': {
        'position':      (TEXT_BOX_CONTAINER_X, TEXT_BOX_CONTAINER_Y),
        'size':          (TEXT_BOX_CONTAINER_WIDTH, TEXT_BOX_CONTAINER_HEIGHT),
        'child_padding': int(14),
        'child_anchor':  str("top"),
        'child_align':   str("bottomright")
    }
}

