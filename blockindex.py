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

###
# Other standard distro imports
###
from   collections.abc import *
import getpass

###
# Installed libraries like numpy, pandas, paramiko
###

###
# From hpclib
###
from   sloppytree import SloppyTree

###
# imports and objects that were written for this project.
###

###
# Credits
###
__author__ = 'George Flanagin'
__copyright__ = 'Copyright 2024, University of Richmond'
__credits__ = None
__version__ = 0.1
__maintainer__ = 'George Flanagin'
__email__ = f'gflanagin@richmond.edu'
__status__ = 'in progress'
__license__ = 'MIT'

class BlockIndex:
    """
    Registry to keep track of where things are to be displayed.
    The only purpose of this dataclass is to confine the
    tedious arithmetic into one translation unit.
    """
    def __init__(self,
        columns:int,
        x_dim:int,
        y_dim:int,
        x_offset:int=0,
        y_offset:int=0):

        self.columns = columns
        self.x_dim = x_dim
        self.y_dim = y_dim
        self.x_offset = x_offset
        self.y_offset = y_offset

        self.positions = []
        self.built = 0


    def __len__(self) -> int:
        return len(self.positions)

    def __int__(self) -> int:
        return len(self.positions)

    def add(self, n:int) -> None:
        self.positions.extend( {'x': self.x_offset + (i % self.columns) * self.x_dim,
                            'y': self.y_offset + (i // self.columns) * self.y_dim}
                            for i in range(self.built, self.built+n) )
        self.built += n


    def __getitem__(self, i:int) -> dict:
        try:
            return SloppyTree(self.positions[i])
        except:
            return {'x':-1, 'y':-1}
