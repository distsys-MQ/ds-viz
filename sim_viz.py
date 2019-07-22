from typing import List

import numpy as np
import PySimpleGUI as pSG

from job import Job
from server import Server, get_servers_from_system
from server_failure import ServerFailure

servers = get_servers_from_system("./logs/personal-config6-fail.xml.your.log", "./configs/personal-config6.xml")

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
window.Finalize()
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

    for i, s in enumerate(servers):
        offset = s.cores * l_width + l_width
        y = last - offset
        graph.DrawText("{} {}".format(s.kind, s.sid), (margin, y))

        if len(s.jobs) == 0:
            last -= s.cores * l_width + l_width

        jobs = norm_jobs(s.jobs)
        for job in jobs:
            overlap = list(filter(lambda j: j.is_overlapping(job), jobs[:jobs.index(job)]))

            for k in range(job.cores):
                job_offset = min(k + len(overlap), s.cores - 1)
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
