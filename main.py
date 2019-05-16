import argparse
import os
from typing import List

import timing  # TODO remove before submission
from job import Job
from server import get_servers, Server

WIDTH = 80


# https://stackoverflow.com/a/11541450/8031185
def is_valid_file(psr, arg):
    if not os.path.isfile(arg):
        psr.error(f"The file '{arg}' does not exist!")
    else:
        return arg


parser = argparse.ArgumentParser(description="Visualises job scheduler logs")
parser.add_argument("filename", help="name of log file to visualise", metavar="FILE",
                    type=lambda f: is_valid_file(parser, f))


def print_job_vert(j: Job):
    ind = " " * 2
    print(f"{ind}job {j.jid} ({j.cores} core(s))")
    ind *= 2
    for name, val in zip(["scheduled:", "started:", "ended:"], [j.schd, j.start, j.end]):
        print(f"{ind}{name:>10} {val}")


def print_vert(servers: List[Server]):
    for s in servers:
        print(f"{s.kind} {s.sid}")
        for j in s.jobs:
            print_job_vert(j)
        print("=" * WIDTH)


print_vert(get_servers(parser.parse_args().filename))


# https://stackoverflow.com/q/20756516/8031185
# https://stackoverflow.com/a/47614884/8031185
# https://stackoverflow.com/q/35381065/8031185
