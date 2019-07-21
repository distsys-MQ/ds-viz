from typing import List, Dict

import numpy as np
import PySimpleGUI as pSG

from job import Job
from job_failure import JobFailure
from server import Server, get_servers_from_system
from server_failure import ServerFailure

servers = get_servers_from_system("bf-100.txt", "fail-free-config100.xml")

l_width = 5
width = 1200
height = sum([s.cores for s in servers]) * l_width
margin = 30
end_time = 86400
x_offset = margin * 2

column = [
    [pSG.Graph(canvas_size=(width, height), graph_bottom_left=(0, 0), graph_top_right=(width, height), key="graph")]
]
layout = [
    [pSG.Column(column, scrollable=True, vertical_scroll_only=True, background_color="whitesmoke")]
]
window = pSG.Window("sim-viz", layout, background_color="whitesmoke", resizable=True)
window.Finalize()
graph = window.Element("graph")


def norm_jobs(jobs: List[Job]) -> List[Job]:
    if not jobs:
        return []

    arr = np.array([(j.start, j.end) for j in jobs])
    arr = np.interp(arr, (0, end_time), (x_offset, width - margin))

    return [Job(j.jid, j.cores, j.schd, start, end, j.failures)
            for (start, end), j in zip([(int(i), int(k)) for (i, k) in arr], jobs)]


def norm_job_failures(failures: List[JobFailure]) -> List[JobFailure]:
    if not failures:
        return []

    for jf in failures:
        if jf.start is None:
            print(f"{jf.s_kind} {jf.sid} {jf.reschd}")

    arr = np.array([jf.start for jf in failures])
    arr = np.interp(arr, (0, end_time), (x_offset, width - margin))

    return [JobFailure(jf.reschd, start, jf.s_kind, jf.sid) for start, jf in zip([int(r) for r in arr], failures)]


def norm_server_failures(failures: List[ServerFailure]) -> List[ServerFailure]:
    if not failures:
        return []

    arr = np.array([(f.fail, f.recover) for f in failures])
    arr = np.interp(arr, (0, end_time), (x_offset, width - margin))

    return [ServerFailure(fail, recover) for (fail, recover) in [(int(f), int(r)) for (f, r) in arr]]


def init_server_dict(svrs: List[Server]) -> Dict[str, Dict[int, int]]:
    s_dict = {}

    for s in svrs:
        if s.kind not in s_dict:
            s_dict[s.kind] = {}

        s_dict[s.kind][s.sid] = None

    return s_dict


def draw():
    svr_ys = init_server_dict(servers)
    top = height - margin
    last = top

    for i, s in enumerate(servers):
        offset = s.cores * l_width + l_width
        y = last - offset
        svr_ys[s.kind][s.sid] = y
        graph.DrawText("{} {}".format(s.kind, s.sid), (margin, y))

        if len(s.jobs) == 0:
            last -= s.cores * l_width + l_width

        for j in norm_jobs(s.jobs):
            if j.failures:
                j.failures = norm_job_failures(j.failures)

                for k in range(j.cores):
                    jy = y + k * l_width
                    last = min(last, jy)
                    graph.DrawLine((j.start + margin, jy), (j.failures[0].start, jy), width=l_width, color="blue")

                # next_starts = [jf.start for jf in j.failures[1:]]
                # next_starts.append(j.end)
                #
                # for jf, ns in zip(j.failures, next_starts):
                #     for k in range(j.cores):
                #         svr_y = svr_ys[jf.s_kind][jf.sid]
                #         jy = svr_y + k * l_width
                #         graph.DrawLine((jf.reschd + margin, jy), (ns, jy), width=l_width, color="blue")

            else:
                for k in range(j.cores):
                    jy = y + k * l_width
                    last = min(last, jy)
                    graph.DrawLine((j.start + margin, jy), (j.end, jy), width=l_width, color="green")

        for f in norm_server_failures(s.failures):
            f_y = y - 2
            graph.DrawRectangle((f.fail, f_y), (f.recover, f_y + s.cores * l_width), fill_color="red", line_color="red")


draw()

while True:
    event, values = window.Read()
