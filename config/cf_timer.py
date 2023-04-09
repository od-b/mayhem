from .cf_window import MAP_TOPRIGHT_POS
from .ui_components import CF_TEXT_BOXES


text_box_container_width = int(200)
text_box_container_height = int(200)

# position the container top left of the map surface + some padding
text_box_container_pos_x = int(MAP_TOPRIGHT_POS[0] - text_box_container_width - 40)
text_box_container_pos_y = int(MAP_TOPRIGHT_POS[1] + 8)

CF_TIMER = {
    # accurate_timing:
    #   how strict the time tick function should be.
    #   Uses more resources if set to true
    #   docref: https://www.pygame.org/docs/ref/time.html#pygame.time.Clock.tick_busy_loop
    'accurate_timing':  True,                # default: True
    'display_fps_text': True,
    'display_segment_time_text': True,
    'fps_text_style': CF_TEXT_BOXES['bold_large_green'],
    'segment_time_text_style': CF_TEXT_BOXES['regular_large_bone'],
    'text_box_container': {
        'position':      (text_box_container_pos_x, text_box_container_pos_y),
        'size':          (text_box_container_width, text_box_container_height),
        'child_padding': int(14),   # also pads the first child from its anchor
        'child_anchor':  str("top"),
        'child_align':   str("bottomright")
    }
}

