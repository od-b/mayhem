### Author: Odin Bjerke | <od.bjerke@gmail.com> | <obj021@uit.no>  

# Dependancies

## Python 3.10+
The code uses type hints extensively, and therefore requires a recent python version [3.5 or newer](https://docs.python.org/3/library/typing.html).  [(further info)](https://peps.python.org/topic/typing/)  

To run this app, [Python 3.10.0](https://www.python.org/downloads/release/python-3100/) or newer is required.  
Note **pygame 2.3.0 should work with python 3.11+, but i have not tested it**
### Check python version by running one of the scripts below.
**Mac**:  
>python3 -c "exec(\"import sys\nprint('Python Version=='+sys.version)\")"  

**Windows/Linux**:  
>python -c "exec(\"import sys\nprint('Python Version=='+sys.version)\")"  

## Pygame 2.1.3+
Developed and tested using **pygame 2.3.0**  
If you are running an earlier version of pygame, i strongly recommend updating.
There are many performance updates, and introduces no backward compatibility issues that do not already exist in the prior 2.0+ versions.  
I know for a fact any pygame version prior to **2.1.3** will not work with this app.  
The app will run a version check on initialization, but will crash prior to this if pygame is not installed at all.


# How To Play
Use WASD for directional rotation  (keybinds can be changed in config.cf_players.py)
Thrust towards facing angle with space. This consumes fuel.  
If you run out of fuel, chances are good you will crash and die  
Collect all the coins without dying to finish the map.  

