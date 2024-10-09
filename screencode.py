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
from   blockindex import BlockIndex

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
    l_text=len(initial_text)
    if initial_text: block.addstr(1, (w-l_text)//2, initial_text)

    block.addstr(2, 3, "CPU")
    block.addstr(3, 3, "MEM")
    block.hline(4, 1, curses.ACS_HLINE, w-2)
    block.addstr(5, 4, "GPU TYPE")
    block.addstr(5, w-7, "FAN%")
    block.addstr(5, int(w*0.3), "MEM%")
    block.addstr(5, int(w*0.5), "WATTS")
    block.addstr(5, int(w*0.7), "TEMP")

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

    pickles = sorted(tuple( fileutils.extract_pickle(myargs.config.outfile) ))
    logger.debug(f'{len(pickles)} pickles extracted.')

    # Let's get some parameters for our environment. At this point
    # we are more interested in the width of the screen than the
    # height -- after all, we can scroll the screen vertically.
    h, w = stdscr.getmaxyx()

    # Build the index to calculate block positions.
    idx = BlockIndex((w - params.x_offset) // params.block_x_dim,
        params.block_x_dim, params.block_y_dim,
        params.x_offset, params.y_offset)
    # And add the number of blocks we need.
    idx.add(len(pickles))

    # Create the blocks. Each region is a tuple(block, panel)
    regions = [ block_and_panel(params.block_y_dim, params.block_x_dim,
            idx[i].y, idx[i].x, f"{pickles[i][0]}") for i in range(len(pickles)) ]

    for i in range(len(regions)):
        block = regions[i][0]
        tree = pickles[i][1]
        for i, k in enumerate(tree.keys(), start=6):
            n = len(tree[k].product_name) + 3
            block.addstr(i, 2, f"{i-5} {tree[k].product_name[-8:]}")
            block.addstr(i, 4+n, str(tree[k]["temperature.gpu_temp"]))
            block.addstr(i, 4+n+7, str(tree[k]["gpu_power_readings.power_draw"]))

    curses.panel.update_panels()
    stdscr.refresh()
    return


@trap
def safe_get(t:SloppyTree, k:str, default_value:object) -> str:
    """
    Take care of missing values for the display.
    """
    try:
        return None
    except:
        return None
