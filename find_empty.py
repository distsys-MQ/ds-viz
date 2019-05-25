import argparse
import os

import numpy as np

from server import get_servers, get_servers_from_system


def is_valid_file(psr, arg):
    if not os.path.isfile(arg):
        psr.error("The file '{}' does not exist!".format(arg))
    else:
        return arg


display_choices = ["graph", "text", "both"]

parser = argparse.ArgumentParser(description="Finds jobs with empty values")
parser.add_argument("filename", type=lambda f: is_valid_file(parser, f), metavar="FILE",
                    help="name of log file to test")
parser.add_argument("-s", "--system", type=lambda f: is_valid_file(parser, f), metavar="FILE",
                    help="name of system file")

if parser.parse_args().system is None:
    servers = get_servers(parser.parse_args().filename)
else:
    servers = get_servers_from_system(parser.parse_args().filename, parser.parse_args().system)

job_lists = []
for s in servers:
    job_lists.append(np.array([(j.jid, j.schd, j.start, j.end) for j in s.jobs]))

for jobs in job_lists:
    for j in jobs:
        if None in j:
            print("Job {}:\n  schd: {}\n  start: {}\n  end: {}".format(j[0], j[1], j[2], j[3]))
