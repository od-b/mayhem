### Author: Odin Bjerke | <od.bjerke@gmail.com> | <obj021@uit.no>  

# Python Version
The code uses type hints extensively, and therefore requires a recent python version [3.5 or newer](https://docs.python.org/3/library/typing.html). [further info](https://peps.python.org/topic/typing/)  
Be aware **the latest python version may break pygame, stick to 3.5 to 3.10** (3.11 etc.)  
Recommended version: [Python 3.10.0 (v3.10.0:b494f5935c)](https://www.python.org/downloads/release/python-3100/)  
#### Check python version by running one of the scripts below.
**Mac**:  
>python3 -c "exec(\"import sys\nprint('Python Version => '+sys.version)\")"  

**Windows/Linux**:  
>python -c "exec(\"import sys\nprint('Python Version => '+sys.version)\")"  

# Pygame Version
Written and tested using pygame 2.3.0  
I know for a fact any version prior to 2.1.3 will not work.  

# Installation
Assuming pip as package manager, automatically install the required libraries by running  
>pip install -r requirements.txt
__or__ check the __requirements.txt__ file and manually install the modules.  
