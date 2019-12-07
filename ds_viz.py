#!/usr/bin/env python3

import sys
from argparse import ArgumentParser

from arg_checks import IsFile, MinInt
from visualisation import Visualisation

parser = ArgumentParser(description="Visualises DS simulations")

# The order of arguments in descending order of file frequency is: config, failures, log.
# This should be the preferable order when using ds-viz via command-line.
# However, failure-free simulations should also be supported, so the failure argument is optional
parser.add_argument("config", action=IsFile,
                    help="configuration file used in simulation")
parser.add_argument("log", action=IsFile,
                    help="simulation log file to visualise")
parser.add_argument("-f", "--failures", metavar="RESOURCE_FAILURES", action=IsFile,
                    help="resource-failures file from simulation")
parser.add_argument("-c", "--core_height", type=int, default=8, action=MinInt, min_int=1,
                    help="set core height, minimum value of 1")
parser.add_argument("-s", "--scale", type=int, default=sys.maxsize, action=MinInt,
                    help="set scaling factor of visualisation")
parser.add_argument("-w", "--width", type=int, default=1, action=MinInt, min_int=1,
                    help="set visualisation width as a multiple of window width, minimum value of 1")
args = parser.parse_args()

viz = Visualisation(args.config, args.failures, args.log, args.core_height, args.scale, args.width)
viz.run()
