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
import argparse
from   collections.abc import *
import curses
import curses.panel
import pickle
import time

###
# Installed libraries like numpy, pandas, paramiko
###

###
# From hpclib
###
import fileutils
from   sloppytree import SloppyTree, SloppyException
from   urdecorators import trap
from   urlogger import URLogger

###
# imports and objects that were written for this project.
###
from   screenglobals import Keys, UserRequestedExit

###
# Global objects
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


@trap
def handle_events(refresh_interval:float,
                stdscr:curses.window,
                logger:URLogger) -> int:

    time.sleep(60)
    logger.info("Waited for Godot.")

    return 0

@trap
def block_and_panel(h:int, w:int, y:int, x:int, initial_text:str="") -> tuple:
    """
    Build screen regions to hold data.

    h - height of the region
    w - width of the region
    y - vertical offset of the top-left corner.
    x - horizontal offset of the top-left corner.
    initial_text - handy for debugging; usually blank.

    """
    block = curses.newwin(h, w, y, x)
    block.box()
    if initial_text: block.addstr(1, 1, initial_text)
    panel = curses.panel.new_panel(block)
    return block, panel


@trap
def populate_screen(myargs:argparse.Namespace,
                    stdscr:curses.window,
                    logger:URLogger) -> None:
    """
    Take the data returned by querying the nodes, and
    draw a screen. This is a little bit of a tedious and
    error prone process.
    """
    logger.debug("entering function")

    params = myargs.config

    pickles = tuple(fileutils.extract_pickle(myargs.config.outfile))
    logger.debug(f'{len(pickles)} pickles extracted.')

    # Let's get some parameters for our environment. At this point
    # we are more interested in the width of the screen than the
    # height -- after all, we can scroll the screen vertically.
    h, w = stdscr.getmaxyx()
    # Number of columns that will fit the screen
    block_columns = w // params.block_x_dim
    # Number of rows we need.
    block_rows = len(pickles) // block_columns
    # Build 'em
    regions = tuple(
        block_and_panel(params.block_y_dim, params.block_x_dim,
            y * params.block_y_dim, x * params.block_x_dim, f"{pickles[y*block_columns + x][0]}")
        for y in range(block_rows) for x in range(block_columns)
        )

    for y in range(block_rows):
        for x in range(block_columns):
            idx = y*block_columns + x
            block = regions[idx][0]
            tree = pickles[idx][1]
            for i, k in enumerate(tree.keys(), start=3):
                block.addstr(i, 3, tree[k].product_name)

    curses.panel.update_panels()
    stdscr.refresh()
    return


