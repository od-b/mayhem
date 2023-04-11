from .colors import RGB, RGBA

CF_FILLED_RECT = {
    'beige_on_orange': {
        'color': RGB['beige'],
        'alpha': int(255),
        'border_color': RGB['orange'],
        'border_width': int(2),
        'border_alpha': int(255)
    },
    'orange_on_beige': {
        'color': RGB['orange'],
        'alpha': int(255),
        'border_color': RGB['beige'],
        'border_width': int(4),
        'border_alpha': int(255)
    },
    'lightblue_on_blue': {
        'color':            RGB['blue_light'],
        'alpha':            int(255),
        'border_color':     RGB['blue'],
        'border_width':     int(5),
        'border_alpha':     int(255),
    },
    ## VARIANTS WITH ALPHA BELOW ##
    'sage_on_sage': {
        'color': RGB['sage'],
        'alpha': int(100),
        'border_color': RGB['sage'],
        'border_width': int(2),
        'border_alpha': int(210)
    },
    'green_on_green': {
        'color':        RGB['green'],
        'alpha': int(220),
        'border_color': RGB['green'],
        'border_width': int(1),
        'border_alpha': int(240)
    },
    'blue_on_blue': {
        'color':             RGB['blue'],
        'alpha':             int(70),
        'border_color':      RGB['blue'],
        'border_width':      int(2),
        'border_alpha':      int(210)
    },
    'red_on_red': {
        'color':             RGB['red_1'],
        'alpha':             int(70),
        'border_color':      RGB['red_1'],
        'border_width':      int(2),
        'border_alpha':      int(210)
    },
    'orange_on_orange': {
        'color':             RGB['orange'],
        'alpha':             int(70),
        'border_color':      RGB['orange_1'],
        'border_width':      int(2),
        'border_alpha':      int(210)
    },
    'darkred_on_darkred': {
        'color':            RGB['red_2'],
        'alpha':            int(210),
        'border_color':     RGB['red_2'],
        'border_width':     int(1),
        'border_alpha':     int(240),
    },
    'lightblue_on_lightblue': {
        'color':            RGB['blue_light'],
        'alpha':            int(210),
        'border_color':     RGB['blue_light'],
        'border_width':     int(1),
        'border_alpha':     int(240),
    },
    'beige_on_beige': {
        'color':            RGB['beige'],
        'alpha':            int(210),
        'border_color':     RGB['beige'],
        'border_width':     int(1),
        'border_alpha':     int(240),
    },
    'offblack_on_beige': {
        'color':            RGB['offblack'],
        'alpha':            int(255),
        'border_color':     RGB['beige'],
        'border_width':     int(2),
        'border_alpha':     int(255),
    }
}
