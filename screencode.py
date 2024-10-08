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
def display_screen(stdscr:curses.window,
                    logger:URLogger) -> None:

    curses.panel.update_panels()
    stdscr.refresh()

    return


@trap
def handle_events(refresh_interval:float,
                stdscr:curses.window,
                logger:URLogger) -> int:

    start = time.time()
    stdscr.nodelay(True)  # Make getch() non-blocking
    stdscr.timeout(100)  # Timeout for getch() in milliseconds
    key = -1

    while True:
        # If we have waited long enough, return control to the
        # rest of the program.
        if (now := time.time()) - start >= refresh_interval:
            logger.info("Waited for Godot.")
            return

        # Check for key press (non-blocking)
        if (key := stdscr.getch()) == -1:
            time.sleep(0.1)
            continue

        return key

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
    logger.debug(f'{len(pickles)} extracted.')

    # Let's get some parameters for our environment. At this point
    # we are more interested in the width of the screen than the
    # height -- after all, we can scroll the screen vertically.
    h, w = stdscr.getmaxyx()
    # Number of columns that will fit the screen
    block_columns = w // params.block_x_dim
    # Number of rows we need.
    block_rows = len(pickles) // block_columns
    # Build 'em
    blocks = tuple(curses.newwin(params.block_y_dim,
                      params.block_x_dim,
                      y * params.block_y_dim,
                      x * params.block_x_dim)
        for y in range(block_rows) for x in range(block_columns))
    panels = tuple(curses.panel.new_panel(_) for _ in blocks)

    for i, block in enumerate(blocks):
        block.box()
        block.addstr(2, 2, f"Blurb in box {i}")

    return


