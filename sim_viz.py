import os
from argparse import ArgumentParser
from typing import List

import numpy as np
import PySimpleGUI as pSG

from job import Job
from server import Server, get_servers_from_system, get_results
from server_failure import ServerFailure


# https://stackoverflow.com/a/11541450/8031185
def is_valid_file(psr: ArgumentParser, arg: str) -> str:
    if not os.path.isfile(arg):
        psr.error("The file '{}' does not exist!".format(arg))
    else:
        return arg


parser = ArgumentParser(description="Visualises DS simulations")
parser.add_argument("log", type=lambda f: is_valid_file(parser, f), help="simulation log file to visualise")
parser.add_argument("config", type=lambda f: is_valid_file(parser, f), help="configuration file used in simulation")
args = parser.parse_args()

servers = get_servers_from_system(args.log, args.config)

l_width = 5
width = 1200
height = int(sum([s.cores for s in servers]) * l_width * 3)
margin = 30
last_time = Server.last_time
x_offset = margin * 2

column = [
    [pSG.Graph(canvas_size=(width, height), graph_bottom_left=(0, 0), graph_top_right=(width, height), key="graph")]
]
layout = [
    [pSG.Column(column, scrollable=True, vertical_scroll_only=True, background_color="whitesmoke")]
]
window = pSG.Window("sim-viz", layout, size=(width + 60, height), background_color="whitesmoke", resizable=True)
window2 = pSG.Window("details", [[pSG.Text(get_results(args.log))]], background_color="whitesmoke", resizable=True)
window.Finalize()
window2.Finalize()
graph = window.Element("graph")


def norm_jobs(jobs: List[Job]) -> List[Job]:
    if not jobs:
        return []

    arr = np.array([(j.start, j.end) for j in jobs])
    arr = np.interp(arr, (margin, last_time), (x_offset, width - margin))

    return [Job(j.jid, j.cores, j.schd, start, end, j.failed)
            for (start, end), j in zip([(int(i), int(k)) for (i, k) in arr], jobs)]


def norm_server_failures(failures: List[ServerFailure]) -> List[ServerFailure]:
    if not failures:
        return []

    arr = np.array([(f.fail, f.recover) for f in failures])
    arr = np.interp(arr, (margin, last_time), (x_offset, width - margin))

    return [ServerFailure(fail, recover) for (fail, recover) in [(int(f), int(r)) for (f, r) in arr]]


def draw():
    top = height - margin
    last = top

    for s in servers:
        offset = s.cores * l_width + l_width
        y = last - offset
        graph.DrawText("{} {}".format(s.kind, s.sid), (margin, y))

        if len(s.jobs) == 0:  # Add empty space for jobless servers
            last -= s.cores * l_width + l_width

        jobs = norm_jobs(s.jobs)
        for job in jobs:
            overlap = list(filter(lambda j: j.is_overlapping(job), jobs[:jobs.index(job)]))

            for k in range(job.cores):
                # Offset by number of job's cores + number of concurrent jobs
                # If offset would exceed server height, reset to the bottom
                used_cores = k + len(overlap)
                job_offset = used_cores if used_cores < s.cores else 0

                job_y = y + job_offset * l_width
                last = min(last, job_y)

                colour = "blue" if job.failed else "black"
                graph.DrawLine((job.start, job_y), (job.end, job_y), width=l_width, color=colour)

        for fail in norm_server_failures(s.failures):
            fail_y = y - 2
            graph.DrawRectangle((fail.fail, fail_y), (fail.recover, fail_y + s.cores * l_width),
                                fill_color="red", line_color="red")


draw()

while True:
    event, values = window.Read()
