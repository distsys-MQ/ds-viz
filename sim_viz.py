import math
import os
from argparse import ArgumentParser
from typing import List, Dict, Tuple

import numpy as np
import PySimpleGUI as pSG

from job import Job
from server import Server, get_servers_from_system, server_list_to_dict, get_results, print_servers_at
from server_failure import ServerFailure


# https://stackoverflow.com/a/11541450/8031185
def is_valid_file(psr: ArgumentParser, arg: str) -> str:
    if not os.path.isfile(arg):
        psr.error("The file '{}' does not exist!".format(arg))
    else:
        return arg


# TODO cleanup code, revise scoping

parser = ArgumentParser(description="Visualises DS simulations")
parser.add_argument("log", type=lambda f: is_valid_file(parser, f), help="simulation log file to visualise")
parser.add_argument("config", type=lambda f: is_valid_file(parser, f), help="configuration file used in simulation")
args = parser.parse_args()

servers = get_servers_from_system(args.log, args.config)

s_dict = server_list_to_dict(servers)
s_boxes: Dict[range, Server] = {}

unique_jids = sorted({j.jid for s in servers for j in s.jobs})
j_graph_ids: Dict[int, List[Tuple[int, str]]] = {jid: [] for jid in unique_jids}

l_width = 5
width = 1200
height = int(sum([s.cores for s in servers]) * l_width * 1.5)
menu_height = 150
left_margin = 30
right_margin = 15
last_time = Server.last_time
x_offset = left_margin * 2

pSG.SetOptions(font=("Courier New", 10), background_color="whitesmoke", element_padding=(0, 0), margins=(1, 1))

graph_column = [[pSG.Graph(canvas_size=(width, height), graph_bottom_left=(0, 0), graph_top_right=(width, height),
                           key="graph", change_submits=True, drag_submits=False)]]
frame_size = (49, 6)
t_slider_width = 89
sj_btn_width = 10

layout = [
    [pSG.Frame("Current Server", [[pSG.Txt("", size=frame_size, key="current_server")]]),
     pSG.Frame("Current Results", [[pSG.Txt("", size=frame_size, key="current_results")]]),
     pSG.Frame("Final Results", [[
         pSG.Column([[pSG.Txt(get_results(args.log), font=("Courier New", 8))]], size=(400, 83), scrollable=True)]])],
    [pSG.Button("Show Job", size=(sj_btn_width, 1), button_color=("white", "red"), key="show_job"),
     pSG.Slider((unique_jids[0], unique_jids[-1]), default_value=unique_jids[0],
                size=(t_slider_width - sj_btn_width, 10), orientation="h", enable_events=True, key="job_slider")],
    [pSG.Slider((0, Server.last_time), default_value=0, size=(t_slider_width, 10), pad=((44, 0), 0),
                orientation="h", enable_events=True, key="time_slider")],
    [pSG.Column(graph_column, size=(width, height), scrollable=True, vertical_scroll_only=True)]
]

window = pSG.Window("sim-viz", layout, resizable=True, return_keyboard_events=True)
window.Finalize()
graph = window.Element("graph")
current_server = window.Element("current_server")
current_results = window.Element("current_results")
t_slider = window.Element("time_slider")
j_slider = window.Element("job_slider")
show_job = False


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
    last = height - l_width
    font = ("Courier New", 8)
    char_width = 2.5
    text_margin = int(char_width * 2)

    for kind, kind_dict in s_dict.items():
        kind_y = last - text_margin * 2
        graph.DrawText(f"{kind}", (left_margin, kind_y), font=font)

        for s in kind_dict.values():
            offset = s.cores * l_width + l_width

            box_y1 = last - offset - text_margin
            box_y2 = last - text_margin
            s_boxes[range(box_y1, box_y2)] = s
            graph.DrawRectangle((box_x1, box_y1), (box_x2, box_y2))

            # https://stackoverflow.com/a/2189827/8031185
            sid_length = 1 if s.sid == 0 else int(math.log10(s.sid)) + 1

            sid_x = x_offset - text_margin - (sid_length * char_width)
            sid_y = last - offset
            graph.DrawText(f"{s.sid}", (sid_x, sid_y), font=font)

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

                    col = f"#{job.fails * 100:06X}"
                    j_graph_ids[job.jid].append(
                        (graph.DrawLine((job.start, job_y), (job.end, job_y), width=l_width, color=col), col))

            for fail in norm_server_failures(s.failures):
                fail_y = sid_y - 2
                graph.DrawRectangle((fail.fail, fail_y), (fail.recover, fail_y + s.cores * l_width),
                                    fill_color="red", line_color="red")


prev_jid = unique_jids[0]


def update_output(t: int):
    current_server.Update(server.print_server_at(t))
    current_results.Update(print_servers_at(servers, t))


def change_job_colour(jid: int, col: str):
    for j_graph_id, _ in j_graph_ids[jid]:
        graph.Widget.itemconfig(j_graph_id, fill=col)


def reset_job_colour(jid: int):
    for j_graph_id, orig_col in j_graph_ids[jid]:
        graph.Widget.itemconfig(j_graph_id, fill=orig_col)


def change_selected_job(jid: int):
    global prev_jid

    change_job_colour(jid, "green")
    reset_job_colour(prev_jid)
    prev_jid = jid


draw()
timeline = graph.DrawLine((x_offset, height), (x_offset, 0), width=2, color="grey")
server = servers[0]
time = 0

while True:
    event, values = window.Read()

    if event is None or event == 'Exit':
        break

    # Handle time slider input
    if event == "time_slider":
        time = int(values["time_slider"])
        norm_time = int(np.interp(np.array([time]), (left_margin, last_time), (x_offset, width - right_margin))[0])
        graph.RelocateFigure(timeline, norm_time, height)

        update_output(time)

    if event == "job_slider" and show_job:
        jid = int(values["job_slider"])
        change_selected_job(jid)

    if event == "show_job":
        show_job = not show_job
        jid = int(values["job_slider"])

        if show_job:
            window.Element("show_job").Update(button_color=("white", "green"))
            change_job_colour(jid, "green")
        else:
            window.Element("show_job").Update(button_color=("white", "red"))
            reset_job_colour(jid)

    # Handle pressing left/right arrow keys
    # Replace with this once PSG has been updated https://github.com/PySimpleGUI/PySimpleGUI/issues/1756
    elif "Left" in event:
        time = time - 1 if time > 1 else 0
        t_slider.Update(time)
        update_output(time)
    elif "Right" in event:
        time = time + 1 if time < last_time else last_time
        t_slider.Update(time)
        update_output(time)

    # Handle clicking in the graph
    elif event == "graph":
        mouse = values["graph"]

        if mouse == (None, None):
            continue
        box_x = mouse[0]
        box_y = mouse[1]
        x_range = range(box_x1, box_x2)

        for y_range, s in s_boxes.items():
            if box_x in x_range and box_y in y_range:
                server = s
                update_output(time)
                break

window.Close()
