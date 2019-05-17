import argparse
import os
from typing import List

import timing  # TODO remove before submission
from job import Job, get_last_time
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


def norm(num: int, end: int) -> int:
    return int(num / int(end / WIDTH))


def make_graph_jobs(s: Server) -> str:
    s_end = get_last_time(s.jobs)
    next_starts = [j.start for j in s.jobs[1:]]
    next_starts.append(WIDTH)
    res = ' ' * norm(s.jobs[0].start - 2, s_end)

    for j, ns in zip(s.jobs, next_starts):
        pref = f"j{j.jid}"
        res += pref
        res += '/' * (norm(j.end - j.start, s_end) - (len(pref)))
        res += ' ' * norm(ns - j.end, s_end)

    return res


def make_graph_server(s: Server) -> str:
    return f"[{make_graph_jobs(s)}]"


def print_graph(servers: List[Server]):
    for s in servers:
        print(f"{s.kind} {s.sid}")
        print(make_graph_server(s))
        print("=" * WIDTH)


# if s.cores == 1:
#     print("[{}]".format(" " * (WIDTH - 2)))
# else:
#     print("┌{}┐".format(" " * (WIDTH - 2)))
#     for i in range(s.cores - 2):
#         print("│{}│".format(" " * (WIDTH - 2)))
#     print("└{}┘".format(" " * (WIDTH - 2)))

print_graph(get_servers(parser.parse_args().filename))


# https://stackoverflow.com/q/20756516/8031185
# https://stackoverflow.com/a/47614884/8031185
# https://stackoverflow.com/q/35381065/8031185
