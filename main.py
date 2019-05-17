import argparse
import os
from typing import List
import numpy as np

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
    ind = ' ' * 2
    print(f"{ind}job {j.jid} ({j.cores} core(s))")
    ind *= 2
    for name, val in zip(["scheduled:", "started:", "ended:"], [j.schd, j.start, j.end]):
        print(f"{ind}{name:>10} {val}")


def print_vert(servers: List[Server]):
    for s in servers:
        print(f"{s.kind} {s.sid}")
        for j in s.jobs:
            print_job_vert(j)
        print('=' * WIDTH)


def multi_cat(*args):
    return '\n'.join(''.join(i) for i in zip(*[s.split('\n') for s in args]))
    # return '\n'.join(''.join(i) for i in zip(*map(str.split, args)))


def norm(jobs: List[Job]) -> List[Job]:
    arr = np.array([(j.start, j.end) for j in jobs])
    arr = np.interp(arr, (arr.min(), arr.max()), (0, WIDTH - 2))

    return [Job(j.jid, j.cores, j.schd, start, end)
            for (start, end), j in zip([(int(i), int(k)) for (i, k) in arr], jobs)]


def graph_jobs(s: Server) -> str:
    jobs = norm(s.jobs)
    next_starts = [j.start for j in jobs[1:]]
    next_starts.append(WIDTH - 2)
    res = ' ' * (jobs[0].start - 2)
    adjust = 0

    for c in range(s.cores):
        for j, ns in zip(jobs, next_starts):
            pref = f"j{j.jid}"

            if j.cores >= c + 1:
                res += pref
                time = j.end - j.start - len(pref)

                if time <= 0:
                    adjust += 1
                dif = time - adjust

                if dif >= 0:
                    adjust = 0
                else:
                    adjust = abs(adjust + dif)

                res += '/' * dif
                res += ' ' * (ns - j.end)
            else:
                res += ' ' * (ns - len(pref))
        if c + 1 < s.cores:
            res += '\n'
    return res


def graph_server(s: Server) -> str:
    if s.cores == 1:
        return f"[{graph_jobs(s)}]"
    else:
        start = '┌\n'
        for i in range(s.cores - 2):
            start += '|\n'
        start += '└\n'
        mid = graph_jobs(s)
        end = '┐\n'
        for i in range(s.cores - 2):
            end += '|\n'
        end += '┘\n'

        return multi_cat(start, mid, end)


def print_graph(servers: List[Server]):
    for s in servers:
        print(f"{s.kind} {s.sid}")
        print(graph_server(s))
        print('=' * WIDTH)


print_graph(get_servers(parser.parse_args().filename))
# print_vert(get_servers(parser.parse_args().filename))

# https://stackoverflow.com/q/20756516/8031185
# https://stackoverflow.com/a/47614884/8031185
# https://stackoverflow.com/q/35381065/8031185
