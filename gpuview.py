# -*- coding: utf-8 -*-
"""
program to show usage of GPUs on a cluster.
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
import pynvml

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

###
# Global objects
###
mynetid = getpass.getuser()
here = socket.gethostname()
logger = None
myargs = None

class Keys(enum.IntEnum):
    ESC  = 27
    HELP = ord('h')
    QUIT = ord('q')

class UserRequestedExit(Exception): pass

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
def xml_to_tree(XMLelement:object) -> SloppyTree:
    """
    Translate XML tags/text into SloppyTree nodes and leaves.
    Note that all XML attributes are discarded.
    """
    data = SloppyTree()

    for child in XMLelement:
        data[child.tag] = xml_to_tree(child) if len(child) else child.text
    return data


@trap
def display_screen() -> None:
    # stdscr.refresh()
    return


@trap
def get_gpu_stats(target:str=None) -> SloppyTree:
    """
    target -- can be a hostname or a user@hostname string.

    returns -- a SloppyTree containing the data retrieved. Returns
        an empty SloppyTree if there is no available data.
    """
    global myargs

    # cmd = myargs.config.toolname
    cmd = "nvidia-smi -q --xml-format"
    if target and target not in ('localhost', here):
        cmd = f"ssh {target} '{cmd}'"

    result = dorunrun(cmd)
    if not result['OK']:
        logger.error(f'No stats for {target}. {result}')
        return SloppyTree()

    xml = ET.fromstring(result['stdout'])
    t = SloppyTree()
    gpu_blobs = xml.findall('gpu')
    for i, blob in enumerate(gpu_blobs):
        t[f"gpu_{i}"] = xml_to_tree(blob)

    return t


@trap
def gather_data(myargs:argparse.Namespace) -> bool:
    """
    Collect the info based on the parameters given in the toml file.
    """
    global logger
    hosts = myargs.config.hosts
    logger.info(f"Gathering data from {hosts}")

    # Remove any old data if there are any.
    try:
        os.unlink(myargs.config.outfile)
        logger.info("Old data file removed.")
    except:
        pass

    # Query each host on a separate thread.
    children = set()
    for host in hosts:
        if (pid := os.fork()):
            children.add(pid)
            continue

        try:
            result = None
            data = scrub_result(get_gpu_stats(host))
            logger.info(f"{data=}")
            result = fileutils.append_pickle(data, myargs.config.outfile)
            logger.debug(f"append_pickle returned {result}")

        finally:
            os._exit(os.EX_OK if result is True else os.EX_IOERR)

    # Wait for results
    while children:
        try:
            child_pid, exit_status, usage = os.wait3(0)
            children.remove(child_pid)
            logger.info(f"{child_pid} finished with {exit_status=}")

        except KeyboardInterrupt as e:
            logger.error(f"You pressed control-C")

    return True


@trap
def handle_events(refresh_interval:int) -> None:
    """
    Keep track of the keys pressed and the timer so
    that the user can leave or refresh before the time
    expires.
    """
    # stdscr.curs_set(0)
    # stdscr.nodelay(True)
    # stdscr.timeout(100)
    time.sleep(refresh_interval)
    return

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

    pickles = tuple(fileutils.extract_pickle(myargs.config.outfile))

    print(pickles)
    return
    stdscr.refresh()

    # Let's get some parameters for our environment.
    h, w = stdscr.getmaxyx()
    stripe_height = h // len(pickles)

    stripes = tuple(curses.newwin(stripe_height, w, i*stripe_height, 0)
        for i in range(len(pickles)))

    for i, stripe in enumerate(stripes, start=1):
        stripe.addstr(1, 1, f"Stripe {i}", curses.A_BOLD)

    return


@trap
def scrub_result(data:SloppyTree) -> SloppyTree:
    """
    Remove the uninteresting leaves.
    """
    t = SloppyTree()

    # First, we must find out how many GPUs there are
    # for which data have been reported.

    global myargs

    for k in data.keys():
        for key in myargs.config.keepers:
            try:
                t[k][key] = data[k](key)
            except SloppyException as e:
                logger.error(f"unable to find {key} in {data=}")

    return t


@trap
def gpuview_main(# stdscr:curses.window,
                 myargs:argparse.Namespace) -> int:
    """
    Set up the basic operation. Go ahead and clear the
    screen here, as any output will mess up the display
    after the cursor window has been opened.
    """
    # stdscr.clear()
    logger.info("Screen cleared.")

    try:
        i = 0
        while gather_data(myargs) and myargs.num_readings > i:
            # The data have all been written to a file, so
            # now it is time to build the display
            i += 1
            populate_screen()
            display_screen()

            handle_events(myargs.time)

        else:
            logger.info(f"Ended with reading {i}")

    except KeyboardInterrupt:
        logger.info("You pressed control-C !")
        sys.exit(os.EX_OK)

    except Exception as e:
        logger.error(f"Unexpected error: {e=}")


    return os.EX_OK


if __name__ == '__main__':

    here       = os.getcwd()
    progname   = os.path.basename(__file__)[:-3]
    configfile = f"{here}/{progname}.toml"
    logfile    = f"{here}/{progname}.log"
    lockfile   = f"{here}/{progname}.lock"

    parser = argparse.ArgumentParser(prog="gpuview",
        description="What gpuview does, gpuview does best.")


    parser.add_argument('-n', '--num-readings', type=int, default=sys.maxsize,
        help="Number of readings to make. Default is not to stop.")

    parser.add_argument('--loglevel', type=int,
        choices=range(logging.FATAL, logging.NOTSET, -10),
        default=logging.DEBUG,
        help=f"Logging level, defaults to {logging.DEBUG}")

    parser.add_argument('-o', '--output', type=str, default="",
        help="Output file name")

    parser.add_argument('--test', type=str, default="",
        help="Specify a host to test with, as opposed to the hosts in the toml file.")

    parser.add_argument('-t', '--time', type=int, default=60,
        help="Number of seconds to wait between readings.")

    parser.add_argument('-z', '--zap', action='store_true',
        help="Remove old log file and create a new one.")

    myargs = parser.parse_args()
    if myargs.test:
        print(dict(get_gpu_stats(myargs.test)))
        sys.exit(os.EX_OK)


    try:
        with open(configfile, 'rb') as f:
            myargs.config=tomllib.load(f)
    except FileNotFoundError as e:
        myargs.config={}

    if myargs.zap:
        try:
            os.unlink(logfile)
        except:
            pass

    logger = URLogger(logfile=logfile, level=myargs.loglevel)
    logger.info(linuxutils.dump_cmdline(myargs, True))
    myargs.config = SloppyTree(myargs.config)


    # Set up the full screen environment.
    # stdscr = curses.initscr()

    try:
        outfile = sys.stdout if not myargs.output else open(myargs.output, 'w')
        with contextlib.redirect_stdout(outfile):
            # Note the use of the lambda crutch to invoke the main function.
            # sys.exit(
            #     curses.wrapper(
            #         lambda stdscr : globals()[f"{progname}_main"](stdscr, myargs))
            #     )
            sys.exit(globals()[f"{progname}_main"](myargs))

    except UserRequestedExit as e:
        logger.info("User requested exit.")
        pass

    except Exception as e:
        logger.info(f"Escaped or re-raised exception: {e}")

    finally:
        logger.info("Closing window")
        # curses.endwin()

