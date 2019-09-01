from argparse import ArgumentParser

from arg_checks import IsFile, MinInt
from visualisation import Visualisation

parser = ArgumentParser(description="Visualises DS simulations")
parser.add_argument("config", action=IsFile,
                    help="configuration file used in simulation")
# TODO Work out how to make failures optional while maintaining argument order
parser.add_argument("failures", action=IsFile,
                    help="resource-failures file from simulation")
parser.add_argument("log", action=IsFile,
                    help="simulation log file to visualise")
parser.add_argument("-c", "--core_height", type=int, default=4, action=MinInt, min_int=1,
                    help="set core height, minimum value of 1")
parser.add_argument("-s", "--scale", type=int, default=0, action=MinInt,
                    help="set scaling factor of visualisation")
args = parser.parse_args()

viz = Visualisation(args.config, args.failures, args.log, args.core_height, args.scale)
viz.run()
