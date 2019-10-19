import math
import os
from typing import List

import PySimpleGUI as sg
import numpy as np

from job import Job
from server import get_servers_from_system, traverse_servers, Server
from server_failure import ServerFailure


def truncate(text: str, length: int = 8) -> str:
    return text if len(text) <= length else text[:5] + ".."


# TODO figure out how to use a truncated server type as a key
def truncate_server(server: Server) -> str:
    return "{} {}".format(truncate(server.type_), server.sid)


class Visualisation:
    def __init__(self, config: str, failures: str, log: str, c_height: int = 4, scale: int = 0):
        self.fnt_f = "Courier"
        self.fnt_s = 10
        b_colour = "whitesmoke"
        sg.set_options(font=(self.fnt_f, self.fnt_s), element_padding=(0, 0), margins=(1, 1),
                       background_color=b_colour, text_element_background_color=b_colour,
                       element_background_color=b_colour, input_elements_background_color=b_colour)

        self.servers = get_servers_from_system(log, config, failures)
        self.s_list = [s for s in traverse_servers(self.servers)]  # TODO Replace with calls to traverse_servers

        self.max_scale = int(math.log(max(s.cores for s in self.s_list), 2))
        self.base_scale = min(scale, self.max_scale)
        self.s_factor = 2 ** self.base_scale

        # Tk needs an active window to detect resolution
        # dum_win = sg.Window("dummy", [[]], finalize=True)
        # resolution = dum_win.get_screen_dimensions()
        # base_px = sg.tkinter.font.Font().measure('A')  # ("Courier New", 16) on Windows
        # font_px_sizes = {i: sg.tkinter.font.Font(font=(self.fnt_f, i)).measure('A')
        #                  for i in range(self.fnt_s - 3, self.fnt_s + 1)}
        # dum_win.close()

        self.c_height = c_height
        self.height = self.calc_height(self.s_factor)
        self.margin = 30
        self.width = 1200 - self.margin

        graph_column = [
            [sg.Graph(canvas_size=(self.width, self.height), graph_bottom_left=(0, self.height),
                      graph_top_right=(self.width, 0), change_submits=True, drag_submits=False,
                      background_color="white", key="graph")]
        ]
        timeline = sg.Column(graph_column, size=(int(self.width + self.margin / 3), self.height + c_height),
                             scrollable=True, key="column")
        title = sg.T("Visualising: {}".format(os.path.basename(log)), font=(self.fnt_f, self.fnt_s, "underline"))

        layout = [
            [title],
            [timeline]
        ]

        self.window = sg.Window("ds-viz", layout, resizable=True, finalize=True,
                                element_justification="center", keep_on_top=True)
        self.graph = self.window["graph"]  # type: sg.Graph

        # Not necessary for creating window, but needed for drawing visualisation in graph and handling user input
        # Could create other classes to handle these
        self.x_offset = self.margin * 2

    def calc_height(self, scale: int) -> int:
        menu_offset = 50
        return sum(min(s.cores, scale) for s in self.s_list) * self.c_height + menu_offset

    def norm_times(self, arr: np.ndarray) -> np.ndarray:
        return np.interp(arr, (0, Server.end_time), (self.x_offset, self.width))

    def norm_jobs(self, jobs: List[Job]) -> List[Job]:
        if not jobs:
            return []

        arr = np.array([(j.start, j.end) for j in jobs])
        arr = self.norm_times(arr)
        res = [j.copy() for j in jobs]

        for (begin, end), j in zip(arr, res):
            j.start = int(begin)
            j.end = int(end)

        return res

    def norm_server_failures(self, failures: List[ServerFailure]) -> List[ServerFailure]:
        if not failures:
            return []

        arr = np.array([(f.fail, f.recover) for f in failures])
        arr = self.norm_times(arr)

        return [ServerFailure(fail, recover) for (fail, recover) in [(int(f), int(r)) for (f, r) in arr]]

    def draw(self, scale: int = None) -> None:
        if scale is None:
            scale = self.base_scale

        last = self.c_height
        axis = self.x_offset - 1
        tick = 3
        s_fact = 2 ** scale
        font = (self.fnt_f, self.fnt_s - 3)
        s_height = None
        self.graph.draw_line((axis, 0), (axis, self.height))  # y-axis

        for type_ in list(self.servers):
            type_y = last
            s_type = truncate(type_)

            self.graph.draw_text(s_type, (self.margin, type_y), font=font)
            self.graph.draw_line((axis - tick * 3, type_y), (axis, type_y))  # Server type tick mark

            for i, s in enumerate(self.servers[type_].values()):
                s_scale = min(s.cores, s_fact)
                s_height = s_scale * self.c_height

                server_y = type_y + s_height * i
                self.graph.draw_line((axis - tick * 2.5, server_y), (axis, server_y))  # Server ID tick mark

                for k in range(s_scale):
                    core_y = server_y + self.c_height * k
                    self.graph.draw_line((axis - tick, core_y), (axis, core_y))  # Server core tick mark

                jobs = self.norm_jobs(s.jobs)
                for jb in jobs:
                    j_scale = min(jb.cores, s_fact)

                    # Only check if previous jobs are overlapping, later jobs should be stacked on previous jobs
                    overlap = list(filter(lambda j: j.is_overlapping(jb), jobs[:jobs.index(jb)]))
                    used_cores = sum(j.cores for j in overlap)

                    # Draw a job bar for every core used by the job, up to the scaling factor
                    for k in range(j_scale):
                        # Offset by number of job's cores + sum of cores used by concurrent jobs
                        # If offset would exceed server height, reset to the top
                        # Also need to adjust y position by half c_height to align job bar edge with server ticks
                        job_core = (used_cores + k) % s_scale
                        job_y = server_y + job_core * self.c_height + self.c_height * 0.5

                        if not jb.will_fail and jb.fails == 0:
                            col = "green"
                        else:
                            base_col = 180
                            fail_col = max(base_col - jb.fails, 0)  # Can't be darker than black (0, 0, 0)
                            col = "#{0:02X}{0:02X}{0:02X}".format(fail_col)

                        self.graph.draw_line((jb.start, job_y), (jb.end, job_y), width=self.c_height, color=col)

                for fail in self.norm_server_failures(s.failures):
                    fail_y1 = server_y
                    fail_y2 = server_y + s_height - 1
                    self.graph.draw_rectangle(
                        (fail.fail, fail_y1), (fail.recover, fail_y2),
                        fill_color="red", line_color="red")

            last = type_y + s_height * len(self.servers[type_])

    def run(self):
        cur_scale = self.base_scale
        self.draw(cur_scale)

        while True:
            event, values = self.window.read()

            # Handle closing the window
            if event is None or event == 'Exit':
                break

        self.window.close()
