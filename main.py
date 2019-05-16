import argparse
import os
import textwrap
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


def print_job_as_list(j: Job):
    job = f"  job {j.jid} ({j.cores} cores)"
    prefix = job + ":\n  "
    expanded_indent = textwrap.fill(prefix + '$', replace_whitespace=False)
    subsequent_indent = ' ' * len(expanded_indent)
    wrapper = textwrap.TextWrapper(initial_indent=prefix,
                                   subsequent_indent=subsequent_indent)
    print(wrapper.fill(f"scheduled: {j.schd}\nstarted: {j.start}\nended: {j.end}"))


def print_list(servers: List[Server]):
    for s in servers:
        print(f"{s.kind} {s.sid}")
        for j in s.jobs:
            print_job_as_list(j)
        print()
        print("=" * WIDTH)


print_list(get_servers(parser.parse_args().filename))

# for s in servers:
#     print(f"{s.kind} {s.sid}")
#     print()
#     for j in s.jobs:
#         print(f"j{j.jid} s{j.start} e{j.end}", end=" ")
#     print()
#     print("|\n" * s.cores)
#     print("=" * WIDTH)


# https://stackoverflow.com/q/20756516/8031185
# https://stackoverflow.com/a/47614884/8031185
# https://stackoverflow.com/q/35381065/8031185
