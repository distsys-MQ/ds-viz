import argparse
import os

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

jobs = [j for s in servers for j in s.jobs]


def has_empty(job):
    return job.schd is None or job.start is None or job.end is None


for j in jobs:
    if has_empty(j):
        print("Job {}:\n  schd: {}\n  start: {}\n  end: {}".format(j.jid, j.schd, j.start, j.end))
