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
import getpass
import logging
import socket
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
import linuxutils
from   sloppytree import SloppyTree
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
def get_gpu_stats(target:str=None) -> SloppyTree:
    """
    target -- can be a hostname or a user@hostname string.

    returns -- a SloppyTree containing the data retrieved. Returns
        an empty SloppyTree if there is no available data.
    """

    cmd = """nvidia-smi -q --xml-format"""
    if target and target not in ('localhost', here):
        cmd = f"ssh {target} '{cmd}'"

    result = dorunrun(cmd)
    if not result['OK']:
        logger.error(f'No stats for {target}. {result}')
        return SloppyTree({'error':f"get_gpu_stats failed with {result}"})

    return xml_to_tree(ET.fromstring(result['stdout']))


@trap
def gather_data(myargs:argparse.Namespace) -> bool:
    return True

@trap
def gpuview_main(myargs:argparse.Namespace) -> int:
    """
    Collect the info based on the parameters given in the toml file.
    """

    try:
        i = 0
        while gather_data(myargs) and (i:= i+1) < myargs.num_readings:
            time.sleep(myargs.time)

    except KeyboardInterrupt:
        logger.info("You pressed control-C !")
        sys.exit(os.EX_OK)


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

    logger = URLogger(logfile=logfile, level=myargs.loglevel)

    try:
        with open(configfile, 'rb') as f:
            myargs.config=tomllib.load(f)
    except FileNotFoundError as e:
        myargs.config={}

    try:
        outfile = sys.stdout if not myargs.output else open(myargs.output, 'w')
        with contextlib.redirect_stdout(outfile):
            sys.exit(globals()[f"{progname}_main"](myargs))

    except Exception as e:
        print(f"Escaped or re-raised exception: {e}")

