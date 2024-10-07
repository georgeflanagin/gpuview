# -*- coding: utf-8 -*-
"""

"""
import typing
from   typing import *

###
# Standard imports, starting with os and sys
###
min_py = (3, 11)
import os
import sys
if sys.version_info < min_py:
    print(f"This program requires Python {min_py[0]}.{min_py[1]}, or higher.")
    sys.exit(os.EX_SOFTWARE)

import enum


###
# Keep these objects handy across modules.
###

logger = None
myargs = None
stdscr = None

class Keys(enum.IntEnum):
    ESC  = 27
    HELP = ord('h')
    QUIT = ord('q')

class UserRequestedExit(Exception): pass

