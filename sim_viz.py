import os
from argparse import ArgumentParser

from visualisation import Visualisation


# TODO Improve argument checking (e.g. positive ints)
#  Could sub-class argparse https://stackoverflow.com/a/18700817/8031185

# https://stackoverflow.com/a/11541450/8031185
def is_valid_file(psr: ArgumentParser, arg: str) -> str:
    if not os.path.isfile(arg):
        psr.error("The file '{}' does not exist!".format(arg))
    else:
        return arg


parser = ArgumentParser(description="Visualises DS simulations")
parser.add_argument("config", type=lambda f: is_valid_file(parser, f), help="configuration file used in simulation")
# TODO Work out how to make failures optional while maintaining argument order
parser.add_argument("failures", type=lambda f: is_valid_file(parser, f), help="resource-failures file from simulation")
parser.add_argument("log", type=lambda f: is_valid_file(parser, f), help="simulation log file to visualise")
parser.add_argument("-c", "--core_height", type=int, default=4, help="set core height")
parser.add_argument("-s", "--scale", type=int, default=0, help="set scaling factor of visualisation")
args = parser.parse_args()

viz = Visualisation(args.config, args.failures, args.log, args.core_height, args.scale)
viz.run()
