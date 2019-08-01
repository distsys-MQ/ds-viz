import os
from argparse import ArgumentParser
from typing import List

import numpy as np
import PySimpleGUI as pSG

from job import Job
from server import Server, get_servers_from_system, server_list_to_dict, get_results
from server_failure import ServerFailure


# https://stackoverflow.com/a/11541450/8031185
# def is_valid_file(psr: ArgumentParser, arg: str) -> str:
#     if not os.path.isfile(arg):
#         psr.error("The file '{}' does not exist!".format(arg))
#     else:
#         return arg
# parser = ArgumentParser(description="Visualises DS simulations")
# parser.add_argument("log", type=lambda f: is_valid_file(parser, f), help="simulation log file to visualise")
# parser.add_argument("config", type=lambda f: is_valid_file(parser, f), help="configuration file used in simulation")
# args = parser.parse_args()

log = "./logs/personal-config6-fail.xml.your.log"
system = "./configs/personal-config6-fail.xml"
servers = get_servers_from_system(log, system)
s_dict = server_list_to_dict(servers)
s_boxes = dict()

l_width = 5
width = 1200
height = sum([s.cores for s in servers]) * l_width * 2
menu_height = 150
left_margin = 30
right_margin = 15
last_time = Server.last_time
x_offset = left_margin * 2

pSG.SetOptions(font=("Helvetica", 10), background_color="whitesmoke", element_padding=(0, 0))

graph_column = [[pSG.Graph(canvas_size=(width, height), graph_bottom_left=(0, 0), graph_top_right=(width, height),
                           key="graph", change_submits=True, drag_submits=False)]]
frame_size = (47, 6)
layout = [
    [pSG.Frame("Current Server", [[pSG.Txt("", size=frame_size, key="current_server")]]),
     pSG.Frame("Current Results", [[pSG.Txt("", size=frame_size, key="current_results")]]),
     pSG.Frame("Final Results", [[
         pSG.Column([[pSG.Txt(get_results(log), font=("Helvetica", 7))]],
                    size=(350, 85), scrollable=True)]])],
    [pSG.Slider(range=(0, Server.last_time), default_value=0, size=(89, 15), pad=((x_offset - 7, 0), 0),
                orientation="h", enable_events=True, key="slider")],
    [pSG.Column(graph_column, size=(width, height), scrollable=True, vertical_scroll_only=True)]
]
window = pSG.Window("sim-viz", layout, size=(width + 60, height + menu_height),
                    resizable=True, return_keyboard_events=True)
# window.Finalize()
graph = window.Element("graph")


def norm_jobs(jobs: List[Job]) -> List[Job]:
    if not jobs:
        return []

    arr = np.array([(j.start, j.end) for j in jobs])
    arr = np.interp(arr, (left_margin, last_time), (x_offset, width - right_margin))
    res = [j.copy() for j in jobs]

    for (start, end), j in zip(arr, res):
        j.start = int(start)
        j.end = int(end)

    return res


def norm_server_failures(failures: List[ServerFailure]) -> List[ServerFailure]:
    if not failures:
        return []

    arr = np.array([(f.fail, f.recover) for f in failures])
    arr = np.interp(arr, (left_margin, last_time), (x_offset, width - right_margin))

    return [ServerFailure(fail, recover) for (fail, recover) in [(int(f), int(r)) for (f, r) in arr]]


box_x1 = 3
box_x2 = x_offset - 2


def draw() -> None:
    top = height - left_margin
    last = top

    for kind, kind_dict in s_dict.items():
        # Get first server of the current kind to calculate the kind's offset
        # Defining a 'kind' separately could make this easier
        kind_offset = list(kind_dict.values())[0].cores * l_width + l_width
        text_margin = 6
        graph.DrawText(f"{kind}", (left_margin - text_margin, last - kind_offset))

        for s in kind_dict.values():
            offset = s.cores * l_width + l_width

            box_y1 = last - offset - text_margin
            box_y2 = last - text_margin
            s_boxes[range(box_y1, box_y2)] = s
            graph.DrawRectangle((box_x1, box_y1), (box_x2, box_y2))

            sid_y = last - offset
            graph.DrawText(f"{s.sid}", (x_offset - text_margin, sid_y))

            if len(s.jobs) == 0:  # Add empty space for jobless servers
                last -= s.cores * l_width + l_width

            jobs = norm_jobs(s.jobs)
            for job in jobs:
                overlap = list(filter(lambda j: j.is_overlapping(job), jobs[:jobs.index(job)]))

                for k in range(job.cores):
                    # Offset by number of job's cores + number of concurrent jobs
                    # If offset would exceed server height, reset to the bottom
                    # TODO Fix job representation
                    used_cores = k + len(overlap)
                    job_offset = used_cores if used_cores < s.cores else 0

                    job_y = sid_y + job_offset * l_width
                    last = min(last, job_y)

                    colour = f"#{job.fails * 100:06X}"
                    graph.DrawLine((job.start, job_y), (job.end, job_y), width=l_width, color=colour)

            for fail in norm_server_failures(s.failures):
                fail_y = sid_y - 2
                graph.DrawRectangle((fail.fail, fail_y), (fail.recover, fail_y + s.cores * l_width),
                                    fill_color="red", line_color="red")


# draw()
# timeline = graph.DrawLine((x_offset, height), (x_offset, 0), width=2, color="grey")
# server = servers[0]
# time = 0
#
# while True:
#     event, values = window.Read()
#
#     if event is not None:
#         # Handle slider input
#         if event == "slider":
#             time = int(values["slider"])
#             norm_time = int(np.interp(np.array([time]), (left_margin, last_time), (x_offset, width - right_margin))[0])
#             graph.RelocateFigure(timeline, norm_time, height)
#
#             window.Element("current_server").Update(server.print_server_at(time))
#
#         # Handle pressing left/right arrow keys
#         # Probably not necessary https://github.com/PySimpleGUI/PySimpleGUI/issues/1756
#         elif "Left" in event:
#             time = time - 1 if time > 1 else 0
#             window.Element("slider").Update(time)
#             window.Element("current_server").Update(server.print_server_at(time))
#         elif "Right" in event:
#             time = time + 1 if time < last_time else last_time
#             window.Element("slider").Update(time)
#             window.Element("current_server").Update(server.print_server_at(time))
#
#         # Handle clicking in the graph
#         elif event == "graph":
#             mouse = values["graph"]
#
#             if mouse == (None, None):
#                 continue
#             box_x = mouse[0]
#             box_y = mouse[1]
#             x_range = range(box_x1, box_x2)
#
#             for y_range, s in s_boxes.items():
#                 if box_x in x_range and box_y in y_range:
#                     server = s
#                     window.Element("current_server").Update(server.print_server_at(time))
#                     break
#     else:
#         break
