import math
import os
import sys
from operator import attrgetter
from typing import Dict, List, Tuple

import PySimpleGUI as sg
import numpy as np

from job import Job, get_job_at
from server import get_servers_from_system, traverse_servers, Server, get_results, print_servers_at
from server_failure import ServerFailure


class Visualisation:
    def __init__(self, config: str, failures: str, log: str, c_height: int = 4, scale: int = 0):
        self.fnt_f = "Courier New"
        self.fnt_s = 10
        b_colour = "whitesmoke"
        sg.SetOptions(font=(self.fnt_f, self.fnt_s), background_color=b_colour, element_padding=(0, 0),
                      margins=(1, 1))

        self.servers = get_servers_from_system(log, config, failures)
        self.s_list = [s for s in traverse_servers(self.servers)]  # TODO Replace with calls to traverse_servers
        self.unique_jids = sorted({j.jid for s in self.s_list for j in s.jobs})
        self.jobs = {
            jid: sorted([j for s in self.s_list for j in s.jobs if j.jid == jid], key=attrgetter("schd"))
            for jid in self.unique_jids
        }  # type: Dict[int, List[Job]]
        self.j_graph_ids = {jid: [] for jid in self.unique_jids}  # type: Dict[int, List[Tuple[int, str]]]

        self.max_scale = int(math.log(max(s.cores for s in self.s_list), 2))
        self.base_scale = min(scale, self.max_scale)
        self.s_factor = 2 ** self.base_scale

        # Tk needs an active window to detect resolution
        dum_win = sg.Window("dummy", [[]], finalize=True)
        resolution = dum_win.GetScreenDimensions()
        base_px = sg.tkinter.font.Font().measure('A')  # ("Courier New", 16)
        f_px = sg.tkinter.font.Font(font=(self.fnt_f, self.fnt_s)).measure('A')
        dum_win.Close()

        self.c_height = c_height
        self.height = self.calc_height(self.s_factor)
        self.margin = 30
        self.width = int(resolution[0]) - self.margin

        # The following variables are just used to create the window
        f_ratio = base_px / f_px
        base_f_width = self.width / base_px
        f_width = base_f_width * f_ratio
        tab_size = (int(f_width / 2), 3)

        graph_column = [
            [sg.Graph(canvas_size=(self.width, self.height), graph_bottom_left=(0, self.height),
                      graph_top_right=(self.width, 0), change_submits=True, drag_submits=False,
                      background_color="white", key="graph")]
        ]
        left_tabs = sg.TabGroup(
            [[sg.Tab("Current Server",
                     [[sg.T("", size=tab_size, background_color=b_colour, key="current_server")]]),
              sg.Tab("Current Job",
                     [[sg.T("", size=tab_size, background_color=b_colour, key="current_job")]])
              ]],
            background_color=b_colour
        )
        right_tabs = sg.TabGroup(
            [[sg.Tab("Current Results",
                     [[sg.T("", size=tab_size, background_color=b_colour, key="current_results")]]),
              sg.Tab("Final Results",
                     [[sg.Multiline(get_results(log), size=tab_size, disabled=True,
                                    font=(self.fnt_f, self.fnt_s - 2))]])
              ]],
            background_color=b_colour
        )

        btn_width = 8
        btn_font = (self.fnt_f, self.fnt_s - 3)
        slider_label_size = (6, 1)
        slider_settings = {
            "size": (base_f_width, 5),
            "orientation": "h",
            "enable_events": True,
            "background_color": b_colour
        }
        scale_width = 30
        title_length = int(f_width - scale_width - btn_width * 2.3)

        layout = [
            [left_tabs, right_tabs],
            [sg.Button("Show Job", size=(btn_width, 1), font=btn_font, button_color=("white", "red"), key="show_job"),
             sg.T("Visualising: {}".format(os.path.basename(log)),
                  size=(title_length, 1), font=(self.fnt_f, self.fnt_s, "underline"),
                  background_color=b_colour, justification="center"),
             sg.T("Scale: {} ({} max cores)".format(self.base_scale, 2 ** self.base_scale),
                  size=(scale_width, 1), background_color=b_colour, justification="right", key="scale"),
             sg.Btn('-', size=(int(btn_width / 2), 1), font=btn_font, key="decrease_scale"),
             sg.Btn('+', size=(int(btn_width / 2), 1), font=btn_font, key="increase_scale")],
            [sg.T("Server", size=slider_label_size, background_color=b_colour),
             sg.Slider((0, len(self.s_list) - 1), default_value=self.s_list[0].sid, key="server_slider",
                       **slider_settings)],
            [sg.T("Job", size=slider_label_size, background_color=b_colour),
             sg.Slider((self.unique_jids[0], self.unique_jids[-1]), default_value=self.unique_jids[0], key="job_slider",
                       **slider_settings)],
            [sg.T("Time", size=slider_label_size, background_color=b_colour),
             sg.Slider((0, Server.last_time), default_value=0, key="time_slider", **slider_settings)],
            [sg.Column(graph_column, size=(int(resolution[0]), int(resolution[1])), scrollable=True, key="column")]
        ]

        self.window = sg.Window("sim-viz", layout, resizable=True, return_keyboard_events=True,
                                finalize=True, element_justification='c', background_color=b_colour)
        if sys.platform == 'linux':
            self.window.TKroot.attributes("-zoomed", True)
        else:
            self.window.Maximize()

        self.graph = self.window["graph"]

        # Not necessary for creating window, but needed for drawing visualisation in graph and handling user input
        # Could create other classes to handle these
        self.x_offset = self.margin * 2
        self.norm_time = self.x_offset
        self.timeline = None
        self.s_index = 0
        self.s_ticks = []
        self.highlight_x1 = self.x_offset - 10
        self.s_highlight = None

    def calc_height(self, scale: int) -> int:
        menu_offset = 50
        return sum(min(s.cores, scale) for s in self.s_list) * self.c_height + menu_offset

    def norm_jobs(self, jobs: List[Job]) -> List[Job]:
        if not jobs:
            return []

        arr = np.array([(j.start, j.end) for j in jobs])
        arr = np.interp(arr, (self.margin, Server.last_time), (self.x_offset, self.width))
        res = [j.copy() for j in jobs]

        for (begin, end), j in zip(arr, res):
            j.start = int(begin)
            j.end = int(end)

        return res

    def norm_server_failures(self, failures: List[ServerFailure]) -> List[ServerFailure]:
        if not failures:
            return []

        arr = np.array([(f.fail, f.recover) for f in failures])
        arr = np.interp(arr, (self.margin, Server.last_time), (self.x_offset, self.width))

        return [ServerFailure(fail, recover) for (fail, recover) in [(int(f), int(r)) for (f, r) in arr]]

    def draw(self, scale: int = None) -> None:
        if scale is None:
            scale = self.base_scale

        last = int(self.margin / 4)
        axis = self.x_offset - 1
        tick = 3
        s_fact = 2 ** scale

        max_s_length = 8
        font = (self.fnt_f, self.fnt_s - 3)

        s_height = None
        self.s_ticks = []  # type: List[int]

        self.graph.DrawLine((axis, 0), (axis, self.height))  # y-axis

        for type_ in list(self.servers):
            type_y = last
            s_type = type_ if len(type_) <= max_s_length else type_[:5] + ".."

            self.graph.DrawText(s_type, (self.margin, type_y), font=font)
            self.graph.DrawLine((axis - tick * 3, type_y), (axis, type_y))  # Server type tick mark

            for i, s in enumerate(self.servers[type_].values()):
                s_scale = min(s.cores, s_fact)
                s_height = s_scale * self.c_height

                sid_y = type_y + s_height * i
                self.graph.DrawLine((axis - tick * 2.5, sid_y), (axis, sid_y))  # Server ID tick mark
                self.s_ticks.append(sid_y)

                # self.graph.DrawLine((axis, sid_y), (self.width - self.right_margin, sid_y))  # Server border

                for k in range(s_scale):
                    core_y = sid_y + self.c_height * k
                    self.graph.DrawLine((axis - tick, core_y), (axis, core_y))  # Server core tick mark

                jobs = self.norm_jobs(s.jobs)
                for jb in jobs:
                    j_scale = min(jb.cores, s_fact)

                    # test_jobs = [8, 10, 13]
                    # test_server = "medium", 1
                    # if (jb.jid in test_jobs) and (s.type_ == test_server[0] and s.sid == test_server[1]):
                    #     print()

                    # Only check if previous jobs are overlapping, later jobs should be stacked on previous jobs
                    overlap = list(filter(lambda j: j.is_overlapping(jb), jobs[:jobs.index(jb)]))
                    used_cores = sum(j.cores for j in overlap)

                    # Draw a job bar for every core used by the job, up to the scaling factor
                    for k in range(j_scale):
                        # Offset by number of job's cores + sum of cores used by concurrent jobs
                        # If offset would exceed server height, reset to the top
                        # Also need to adjust y position by half c_height to align job bar edge with server ticks
                        job_core = (used_cores + k) % s_scale
                        job_y = sid_y + job_core * self.c_height + self.c_height * 0.5

                        # if (jb.jid in test_jobs) and (s.type_ == test_server[0] and s.sid == test_server[1]):
                        #     print("{}: {}".format(jb.jid, job_core))

                        if not jb.will_fail and jb.fails == 0:
                            col = "green"
                        else:
                            base_col = 180
                            fail_col = max(base_col - jb.fails, 0)  # Can't be darker than black (0, 0, 0)
                            col = "#{0:02X}{0:02X}{0:02X}".format(fail_col)

                        self.j_graph_ids[jb.jid].append(
                            (self.graph.DrawLine((jb.start, job_y), (jb.end, job_y),
                                                 width=self.c_height, color=col),
                             col)
                        )

                for fail in self.norm_server_failures(s.failures):
                    fail_y1 = sid_y
                    fail_y2 = sid_y + s_height - 1
                    self.graph.DrawRectangle(
                        (fail.fail, fail_y1), (fail.recover, fail_y2),
                        fill_color="red", line_color="red")

            last = type_y + s_height * len(self.servers[type_])

        # Need to redraw these for them to persist after 'erase' call
        self.timeline = self.graph.DrawLine(
            (self.norm_time, 0), (self.norm_time, self.height),
            color="grey")

        highlight_width = 5
        self.s_highlight = self.graph.DrawLine(
            (self.highlight_x1, self.s_ticks[self.s_index]), (axis, self.s_ticks[self.s_index]),
            width=highlight_width, color="green")

    def update_output(self, t: int, server: Server, job: Job):
        self.window["current_server"].Update(server.print_server_at(t))
        self.window["current_job"].Update(job.print_job(t))
        self.window["current_results"].Update(print_servers_at(self.s_list, t))

    def change_job_colour(self, jid: int, col: str):
        for j_graph_id, _ in self.j_graph_ids[jid]:
            self.graph.Widget.itemconfig(j_graph_id, fill=col)

    def reset_job_colour(self, jid: int):
        for j_graph_id, orig_col in self.j_graph_ids[jid]:
            self.graph.Widget.itemconfig(j_graph_id, fill=orig_col)

    def change_selected_job(self, jid: int, prev_jid: int):
        self.reset_job_colour(prev_jid)
        self.change_job_colour(jid, "yellow")

    def change_scaling(self, scale: int, show_job: bool, prev_jid: int):
        self.graph.Erase()

        s_fact = 2 ** scale
        self.height = self.calc_height(s_fact)
        self.window["column"].Widget.config(height=self.height)
        self.graph.Widget.config(height=self.height)

        self.draw(scale)
        self.window["scale"].Update("Scale: {} ({} max cores)".format(scale, 2 ** scale))

        if show_job:
            self.change_job_colour(prev_jid, "yellow")

    def run(self):
        prev_jid = self.unique_jids[0]
        show_job = False
        cur_scale = self.base_scale
        cur_server = self.s_list[0]
        cur_job = self.jobs[self.unique_jids[0]][0]
        time = 0

        self.draw(cur_scale)
        self.update_output(time, cur_server, cur_job)

        while True:
            event, values = self.window.Read()

            # Handle closing the window
            if event is None or event == 'Exit':
                break

            # Handle time slider movement
            if event == "time_slider":
                time = int(values["time_slider"])
                cur_job = get_job_at(self.jobs[cur_job.jid], time)
                self.norm_time = int(
                    np.interp(
                        np.array([time]),
                        (self.margin, Server.last_time),
                        (self.x_offset, self.width)
                    )[0]
                )
                self.graph.RelocateFigure(self.timeline, self.norm_time, 0)

                self.update_output(time, cur_server, cur_job)

            # Handle job slider movement
            if event == "job_slider":
                jid = int(values["job_slider"])
                cur_job = get_job_at(self.jobs[jid], time)
                self.update_output(time, cur_server, cur_job)

                if show_job:
                    self.change_selected_job(jid, prev_jid)
                    prev_jid = jid

            # Handle server slider movement
            if event == "server_slider":
                self.s_index = int(values["server_slider"])
                cur_server = self.s_list[self.s_index]
                self.graph.RelocateFigure(self.s_highlight, self.highlight_x1, self.s_ticks[self.s_index])
                self.update_output(time, cur_server, cur_job)

            # Handle clicking "show job" button
            if event == "show_job":
                show_job = not show_job
                jid = int(values["job_slider"])

                if show_job:
                    self.window["show_job"].Update(button_color=("white", "green"))
                    self.change_job_colour(jid, "yellow")
                else:
                    self.window["show_job"].Update(button_color=("white", "red"))
                    self.reset_job_colour(jid)

            # Handle pressing left/right arrow keys
            # Replace with this once PSG has been updated https://github.com/PySimpleGUI/PySimpleGUI/issues/1756
            elif "Left" in event:
                time = time - 1 if time > 1 else 0
                self.window["time_slider"].Update(time)
                self.update_output(time, cur_server, cur_job)
            elif "Right" in event:
                time = time + 1 if time < Server.last_time else Server.last_time
                self.window["time_slider"].Update(time)
                self.update_output(time, cur_server, cur_job)

            # Handle clicking on scale buttons
            elif event == "decrease_scale":
                cur_scale = cur_scale - 1 if cur_scale > 0 else 0
                self.change_scaling(cur_scale, show_job, prev_jid)
            elif event == "increase_scale":
                cur_scale = cur_scale + 1 if cur_scale < self.max_scale else self.max_scale
                self.change_scaling(cur_scale, show_job, prev_jid)

        self.window.Close()
