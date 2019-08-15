import math
import os
from argparse import ArgumentParser
from operator import attrgetter
from typing import List, Dict, Tuple

import numpy as np
import PySimpleGUI as pSG

from job import Job, get_job_at
from server import Server, get_servers_from_system, server_list_to_dict, get_results, print_servers_at
from server_failure import ServerFailure


# TODO Separate argument parsing from main program (i.e. 'sim-viz.py' and 'draw_ui.py')
#  Also need to improve argument checking (e.g. positive ints)
#  Could sub-class argparse https://stackoverflow.com/a/18700817/8031185

# https://stackoverflow.com/a/11541450/8031185
def is_valid_file(psr: ArgumentParser, arg: str) -> str:
    if not os.path.isfile(arg):
        psr.error("The file '{}' does not exist!".format(arg))
    else:
        return arg


# TODO cleanup code, revise scoping

parser = ArgumentParser(description="Visualises DS simulations")
parser.add_argument("config", type=lambda f: is_valid_file(parser, f), help="configuration file used in simulation")
parser.add_argument("failures", type=lambda f: is_valid_file(parser, f), help="resource-failures file from simulation")
parser.add_argument("log", type=lambda f: is_valid_file(parser, f), help="simulation log file to visualise")
parser.add_argument("-c", "--core_height", type=int, default=4, help="set core height")
parser.add_argument("-s", "--scale", type=int, default=0, help="set scaling factor of visualisation")
args = parser.parse_args()

servers = get_servers_from_system(args.log, args.config, args.failures)
s_dict = server_list_to_dict(servers)

unique_jids = sorted({j.jid for s in servers for j in s.jobs})
j_dict = {
    jid: sorted([j for s in servers for j in s.jobs if j.jid == jid], key=attrgetter("schd")) for jid in unique_jids
}  # type: Dict[int, List[Job]]
j_graph_ids = {jid: [] for jid in unique_jids}  # type: Dict[int, List[Tuple[int, str]]]

left_margin = 30
right_margin = 15
x_offset = left_margin * 2
tab_size = (75, 3)
c_height = args.core_height
base_scale = args.scale
last_time = Server.last_time
max_scale = int(math.log(max(s.cores for s in servers), 2))

fnt_f = "Courier New"
fnt_s = -13

width = 1200
menu_offset = 50
s_factor = 2 ** base_scale
height = sum(min(s.cores, s_factor) for s in servers) * c_height + menu_offset

mon_height = 1000
w_height = int(mon_height * 0.9)

pSG.SetOptions(font=(fnt_f, fnt_s), background_color="whitesmoke", element_padding=(0, 0), margins=(1, 1))

graph_column = [[pSG.Graph(canvas_size=(width, height), graph_bottom_left=(0, height), graph_top_right=(width, 0),
                           key="graph", change_submits=True, drag_submits=False)]]
left_tabs = pSG.TabGroup(
    [[pSG.Tab("Current Server",
              [[pSG.T("", size=tab_size, key="current_server")]]),
      pSG.Tab("Current Job",
              [[pSG.T("", size=tab_size, key="current_job")]])
      ]]
)
right_tabs = pSG.TabGroup(
    [[pSG.Tab("Current Results",
              [[pSG.T("", size=tab_size, key="current_results")]]),
      pSG.Tab("Final Results",
              [[pSG.Multiline(get_results(args.log), font=(fnt_f, fnt_s + 2), size=tab_size, disabled=True)]])
      ]]
)

btn_width = 8
btn_font = (fnt_f, fnt_s + 3)
slider_settings = {
    "size": (105, 5),
    "orientation": "h",
    "enable_events": True
}
slider_label_size = (6, 1)

layout = [
    [left_tabs, right_tabs],
    [pSG.Button("Show Job", size=(btn_width, 1), font=btn_font, button_color=("white", "red"), key="show_job"),
     pSG.T("Visualising: {}".format(os.path.basename(args.log)),
           size=(99, 1), font=(fnt_f, fnt_s, "underline"), justification="center"),
     pSG.T("Scale: {} ({} max cores)".format(base_scale, 2 ** base_scale),
           size=(30, 1), justification="right", key="scale"),
     pSG.Btn('-', size=(int(btn_width / 2), 1), font=btn_font, key="decrease_scale"),
     pSG.Btn('+', size=(int(btn_width / 2), 1), font=btn_font, key="increase_scale")],
    [pSG.T("Server", size=slider_label_size),
     pSG.Slider((0, len(servers) - 1), default_value=servers[0].sid, key="server_slider", **slider_settings)],
    [pSG.T("Job", size=slider_label_size),
     pSG.Slider((unique_jids[0], unique_jids[-1]), default_value=unique_jids[0], key="job_slider", **slider_settings)],
    [pSG.T("Time", size=slider_label_size),
     pSG.Slider((0, Server.last_time), default_value=0, key="time_slider", **slider_settings)],
    [pSG.Column(graph_column, size=(width, w_height), scrollable=True, vertical_scroll_only=True,
                key="column")]
]

window = pSG.Window("sim-viz", layout, size=(width + left_margin, w_height), resizable=True,
                    return_keyboard_events=True)
window.Finalize()
graph = window.Element("graph")
current_server = window.Element("current_server")
current_job = window.Element("current_job")
current_results = window.Element("current_results")
t_slider = window.Element("time_slider")
scale_output = window.Element("scale")
column = window.Element("column")


def norm_jobs(jobs: List[Job]) -> List[Job]:
    if not jobs:
        return []

    arr = np.array([(j.start, j.end) for j in jobs])
    arr = np.interp(arr, (left_margin, last_time), (x_offset, width - right_margin))
    res = [j.copy() for j in jobs]

    for (begin, end), j in zip(arr, res):
        j.start = int(begin)
        j.end = int(end)

    return res


def norm_server_failures(failures: List[ServerFailure]) -> List[ServerFailure]:
    if not failures:
        return []

    arr = np.array([(f.fail, f.recover) for f in failures])
    arr = np.interp(arr, (left_margin, last_time), (x_offset, width - right_margin))

    return [ServerFailure(fail, recover) for (fail, recover) in [(int(f), int(r)) for (f, r) in arr]]


axis = x_offset - 1
norm_time = x_offset
timeline = None
s_index = 0
s_ticks = []

start = int(right_margin / 2)
highlight_x1 = axis - 9
s_highlight = None


def draw(scale: int = base_scale) -> None:
    global timeline, s_highlight, s_ticks

    last = start
    font = (fnt_f, fnt_s + 4)
    max_s_length = 8
    tick = 3
    graph.DrawLine((axis, 0), (axis, height))  # y-axis
    s_height = None
    s_fac = 2 ** scale
    s_ticks = []

    for kind in list(s_dict):
        kind_y = last
        s_kind = kind if len(kind) <= max_s_length else kind[:5] + ".."

        graph.DrawText(s_kind, (left_margin, kind_y), font=font)
        graph.DrawLine((axis - tick * 3, kind_y), (axis, kind_y))  # Server type tick mark

        for i, s in enumerate(s_dict[kind].values()):
            s_scale = min(s.cores, s_fac)
            s_height = s_scale * c_height

            sid_y = kind_y + s_height * i
            graph.DrawLine((axis - tick * 2, sid_y), (axis, sid_y))  # Server ID tick mark
            s_ticks.append(sid_y)

            for k in range(s_scale):
                core_y = sid_y + c_height * k
                graph.DrawLine((axis - tick, core_y), (axis, core_y))  # Server core tick mark

            jobs = norm_jobs(s.jobs)
            for jb in jobs:
                j_scale = min(jb.cores, s_fac)
                overlap = list(filter(lambda j: j.is_overlapping(jb), jobs[:jobs.index(jb)]))

                for k in range(j_scale):
                    # job_y = sid_y + k * c_height

                    # Offset by number of job's cores + number of concurrent jobs
                    # If offset would exceed server height, reset to the top
                    used_cores = k + len(overlap)
                    job_offset = used_cores if used_cores < s_scale else 0
                    job_y = sid_y + job_offset * c_height

                    base_col = 200
                    fail_col = max(base_col - jb.fails, 0)  # Can't be darker than black (0, 0, 0)
                    col = "green" if not jb.failed else "#{0:02X}{0:02X}{0:02X}".format(fail_col)

                    job_y_adj = job_y + c_height * 0.5
                    j_graph_ids[jb.jid].append(
                        (graph.DrawLine((jb.start, job_y_adj), (jb.end, job_y_adj), width=c_height, color=col), col))

            for fail in norm_server_failures(s.failures):
                fail_y1 = sid_y
                fail_y2 = sid_y + s_height - 1
                graph.DrawRectangle((fail.fail, fail_y1), (fail.recover, fail_y2), fill_color="red", line_color="red")

        last = kind_y + s_height * len(s_dict[kind])

    # Need to redraw these for them to persist after 'erase' call
    timeline = graph.DrawLine((norm_time, 0), (norm_time, height), color="grey")
    s_highlight = graph.DrawLine((highlight_x1, s_ticks[s_index]), (axis, s_ticks[s_index]), width=5, color="green")


prev_jid = unique_jids[0]


def update_output(t: int):
    current_server.Update(server.print_server_at(t))
    current_job.Update(job.print_job(t))
    current_results.Update(print_servers_at(servers, t))


def change_job_colour(jid: int, col: str):
    for j_graph_id, _ in j_graph_ids[jid]:
        graph.Widget.itemconfig(j_graph_id, fill=col)


def reset_job_colour(jid: int):
    for j_graph_id, orig_col in j_graph_ids[jid]:
        graph.Widget.itemconfig(j_graph_id, fill=orig_col)


def change_selected_job(jid: int):
    global prev_jid

    reset_job_colour(prev_jid)
    change_job_colour(jid, "yellow")
    prev_jid = jid


def change_scaling(scale: int):
    global height
    graph.Erase()

    fac = 2 ** scale
    height = sum(min(s.cores, fac) for s in servers) * c_height + menu_offset
    column.Widget.config(height=height)
    graph.Widget.config(height=height)

    draw(scale)
    scale_output.Update("Scale: {} ({} max cores)".format(scale, 2 ** scale))

    if show_job:
        change_job_colour(prev_jid, "yellow")


show_job = False
cur_scale = base_scale
draw(base_scale)
server = servers[0]
job = j_dict[unique_jids[0]][0]
time = 0
update_output(time)

while True:
    event, values = window.Read()

    # Handle closing the window
    if event is None or event == 'Exit':
        break

    # Handle time slider movement
    if event == "time_slider":
        time = int(values["time_slider"])
        job = get_job_at(j_dict[job.jid], time)
        norm_time = int(np.interp(np.array([time]), (left_margin, last_time), (x_offset, width - right_margin))[0])
        graph.RelocateFigure(timeline, norm_time, 0)

        update_output(time)

    # Handle job slider movement
    if event == "job_slider":
        jid = int(values["job_slider"])
        job = get_job_at(j_dict[jid], time)
        update_output(time)

        if show_job:
            change_selected_job(jid)

    # Handle server slider movement
    if event == "server_slider":
        s_index = int(values["server_slider"])
        server = servers[s_index]
        graph.RelocateFigure(s_highlight, highlight_x1, s_ticks[s_index])
        update_output(time)

    # Handle clicking "show job" button
    if event == "show_job":
        show_job = not show_job
        jid = int(values["job_slider"])

        if show_job:
            window.Element("show_job").Update(button_color=("white", "green"))
            change_job_colour(jid, "yellow")
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

    # Handle clicking on scale buttons
    elif event == "decrease_scale":
        cur_scale = cur_scale - 1 if cur_scale > 0 else 0
        change_scaling(cur_scale)
    elif event == "increase_scale":
        cur_scale = cur_scale + 1 if cur_scale < max_scale else max_scale
        change_scaling(cur_scale)

window.Close()
