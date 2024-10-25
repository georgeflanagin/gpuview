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
def block_and_panel(h:int, w:int, y:int, x:int) -> tuple:
    """
    Build screen regions to hold data.

    h - height of the region
    w - width of the region
    y - vertical offset of the top-left corner.
    x - horizontal offset of the top-left corner.

    """
    block = curses.newwin(h, w, y, x)
    block.box()
    panel = curses.panel.new_panel(block)
    return block, panel


@trap
def decorate_regions(idx:BlockIndex, config:SloppyTree, statics:SloppyTree,
                     pickles:tuple, logger:URLogger) -> list:

    logger.error(f"{dict(config)}")

    hosts = config.hosts
    regions =  [
        block_and_panel(config.block_y_dim, config.block_x_dim, idx[i].y, idx[i].x)
            for i in range(len(idx))
            ]

    for i, host in enumerate(sorted(hosts)):

        t = pickles[i][1]
        # logger.error(f'{t=}')
        w = config.block_x_dim

        regions[i][0].addstr(1, (config.block_x_dim - len(host))//2, host)
        regions[i][0].addstr(2, 3, "CPU")
        regions[i][0].addstr(2, w-3, str(statics[host].cores))
        regions[i][0].addstr(3, 3, "MEM")
        regions[i][0].addstr(3, w-4, str(statics[host].mem))
        regions[i][0].hline(4, 1, curses.ACS_HLINE, w-2)
        regions[i][0].addstr(5, 4, "GPU TYPE")
        regions[i][0].addstr(5, w-7, "FAN%")
        regions[i][0].addstr(5, int(w*0.3), "MEM%")
        regions[i][0].addstr(5, int(w*0.5), "WATTS")
        regions[i][0].addstr(5, int(w*0.7), "TEMP")

        for j, k in enumerate(t.keys(), start=6):
            regions[i][0].addstr(j, 2, f"{j-5} {t[k].product_name[-8:].strip()}")
            regions[i][0].addstr(j, int(w*0.7), de_unit(t[k]["temperature.gpu_temp"]))
            regions[i][0].addstr(j, int(w*0.5), de_unit(t[k]["gpu_power_readings.power_draw"]))

    return regions


@trap
def de_unit(o:object) -> str:
    try:
        return str(o.split()[0])
    except:
        return str(o)

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
    regions = decorate_regions(idx, myargs.config,
        myargs.static_info, pickles, logger)

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
