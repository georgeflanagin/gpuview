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
import contextlib
import curses
import enum
import getpass
import logging
import pickle
import socket
import time
import tomllib
import xml.etree.ElementTree as ET

###
# Installed libraries like numpy, pandas, paramiko
###

###
# From hpclib
###
from   dorunrun import dorunrun
import fileutils
import linuxutils
from   sloppytree import SloppyTree, SloppyException
from   urdecorators import trap
from   urlogger import URLogger

###
# imports and objects that were written for this project.
###
import screenglobals
from   screenglobals import Keys, UserRequestedExit

###
# Global objects
###
stdscr = screenglobals.stdscr
myargs = screenglobals.myargs
logger = screenglobals.logger

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
def display_screen() -> None:
    curses.panel.update_panels()
    stdscr.refresh()
    return


@trap
def handle_events(refresh_interval:int) -> None:
    """
    Keep track of the keys pressed and the timer so
    that the user can leave or refresh before the time
    expires.
    """
    global stdscr

    stdscr.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)
    time.sleep(refresh_interval)

    start = time.time()

    while True:
        key = Key(stdscr.getch().lower())
        if key in (Keys.QUIT, Keys.ESC):
            raise UserRequestedExit
        else:
            return

        if (elapsed_time := time.time()-start) < refresh_interval:
            continue


@trap
def populate_screen() -> None:
    """
    Take the data returned by querying the nodes, and
    draw a screen. This is a little bit of a tedious and
    error prone process.
    """
    global myargs
    global stdscr
    params = myargs.config

    pickles = tuple(fileutils.extract_pickle(myargs.config.outfile))

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
    panels = tuple(curses.panel.new_panel(_ for _ in blocks))

    for i, block in enumerate(blocks):
        block.box()
        block.addstr(2, 2, f"Blurb in box {i}")

    return


