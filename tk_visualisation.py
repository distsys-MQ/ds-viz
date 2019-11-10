import math
import os
import tkinter as tk
from operator import attrgetter
from tkinter import ttk, font, scrolledtext
from typing import Dict, List, Tuple, Union

import numpy as np

import job
import server
from custom_widgets import Slider
from job import Job
from server import Server
from server_failure import ServerFailure


def replace_text(element: tk.Text, text: str):
    element.config(state=tk.NORMAL)
    element.delete(1.0, tk.END)
    element.insert(tk.END, text)
    element.config(state=tk.DISABLED)


class Visualisation:
    def __init__(self):
        config = "./configs/personal-config16.xml"
        log = "./logs/personal-config16-pl05-bf.log"
        failures = "./failures/personal-config16-pl05-failures.txt"
        self.c_height = 10
        scale = 5
        margin = 40
        self.axis = margin * 2

        self.servers = server.get_servers_from_system(log, config, failures)
        # TODO Replace with calls to traverse_servers
        self.s_list = [s for s in server.traverse_servers(self.servers)]  # type: List[Server]
        self.unique_jids = sorted({j.jid for s in self.s_list for j in s.jobs})
        self.jobs = {
            jid: sorted([j for s in self.s_list for j in s.jobs if j.jid == jid], key=attrgetter("schd"))
            for jid in self.unique_jids
        }  # type: Dict[int, List[Job]]
        self.j_graph_ids = {jid: [] for jid in self.unique_jids}  # type: Dict[int, List[Tuple[int, str]]]

        self.max_scale = int(math.log(max(s.cores for s in self.s_list), 2))
        self.base_scale = min(scale, self.max_scale)
        self.s_factor = 2 ** self.base_scale

        t_width = 1600
        t_height = 600

        self.root = tk.Tk()
        self.root.geometry("{}x{}".format(t_width, t_height))
        self.root.columnconfigure(0, weight=1)  # Fill window width
        self.root.rowconfigure(3, weight=1)  # Timeline fills remaining window height

        # Fonts
        courier_8 = font.Font(family="Courier", size=8)
        courier_11 = font.Font(family="Courier", size=11)

        # Status section
        status = tk.Frame(self.root)
        status.columnconfigure(0, weight=1, uniform="notebook")
        status.columnconfigure(1, weight=1, uniform="notebook")
        status.grid(row=0, column=0, sticky=tk.NSEW)

        left_tabs = ttk.Notebook(status)
        cur_server_tab = tk.Frame(left_tabs)
        cur_job_tab = tk.Frame(left_tabs)
        left_tabs.add(cur_server_tab, text="Current Server")
        left_tabs.add(cur_job_tab, text="Current Job")
        left_tabs.grid(row=0, column=0, sticky=tk.NSEW)

        right_tabs = ttk.Notebook(status)
        cur_res_tab = tk.Frame(right_tabs)
        final_res_tab = tk.Frame(right_tabs)
        cur_server_jobs_tab = tk.Frame(right_tabs)
        right_tabs.add(cur_res_tab, text="Current Results")
        right_tabs.add(final_res_tab, text="Final Results")
        right_tabs.add(cur_server_jobs_tab, text="Current Server Jobs")
        right_tabs.grid(row=0, column=1, sticky=tk.NSEW)

        self.cur_server_text = tk.Text(cur_server_tab, height=3, font=courier_11)
        self.cur_server_text.pack(fill=tk.X, expand=True)
        self.cur_job_text = tk.Text(cur_job_tab, height=3, font=courier_11)
        self.cur_job_text.pack(fill=tk.X, expand=True)
        self.cur_res_text = tk.Text(cur_res_tab, height=3, font=courier_11)
        self.cur_res_text.pack(fill=tk.X, expand=True)
        self.cur_server_jobs_text = tk.Text(cur_server_jobs_tab, height=3, font=courier_8)
        self.cur_server_jobs_text.pack(fill=tk.X, expand=True)

        final_res_text = scrolledtext.ScrolledText(final_res_tab, height=3, font=courier_8)
        final_res_text.grid(row=0, column=0, sticky=tk.NSEW)
        final_res_tab.rowconfigure(0, weight=1)
        final_res_tab.columnconfigure(0, weight=1)
        final_res_text.insert(tk.END, server.get_results(log))
        final_res_text.configure(state=tk.DISABLED)

        # Title section
        title = tk.Frame(self.root)
        title.grid(row=1, column=0, sticky=tk.NSEW)

        self.show_job_btn = tk.Button(title, text="Show Job", bg="red", fg="white", font=courier_8)
        self.show_job_btn.pack(side=tk.LEFT)

        self.filename = tk.Label(title, text="Visualising: {}".format(os.path.basename(log)),
                                 font=font.Font(family="Courier", size=11, underline=True))
        self.filename.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.scale_label = tk.Label(title, text="Scale: ()", font=courier_11)
        self.scale_label.pack(side=tk.LEFT)
        btn_width = 4
        self.scale_down_btn = tk.Button(title, text='-', bg="blue", fg="white", font=courier_8, width=btn_width)
        self.scale_down_btn.pack(side=tk.LEFT)
        self.scale_up_btn = tk.Button(title, text='+', bg="blue", fg="white", font=courier_8, width=btn_width)
        self.scale_up_btn.pack(side=tk.LEFT)

        # Controls section
        controls = tk.Frame(self.root)
        controls.grid(row=2, column=0, sticky=tk.NSEW)
        controls.columnconfigure(0, weight=1)

        server_slider = Slider(controls, "Slider", 0, len(self.s_list) - 1,
                               tuple((str(s) for s in server.traverse_servers(self.servers))), self.update_server)
        server_slider.grid(row=0, column=0, sticky=tk.NSEW)
        job_slider = Slider(controls, "Job", min(self.unique_jids), max(self.unique_jids), tuple(self.unique_jids),
                            self.update_job)
        job_slider.grid(row=1, column=0, sticky=tk.NSEW)
        time_slider = Slider(controls, "Time", 0, Server.end_time, tuple(range(0, Server.end_time)), self.update_time)
        time_slider.grid(row=2, column=0, sticky=tk.NSEW)

        # Timeline section
        timeline = tk.Frame(self.root)
        timeline.grid(row=3, column=0, sticky=tk.NSEW)
        timeline.rowconfigure(0, weight=1)
        timeline.columnconfigure(0, weight=1)

        t_yscroll = tk.Scrollbar(timeline)
        t_yscroll.grid(row=0, column=1, sticky=tk.NS)

        self.height = self.calc_height(self.s_factor)
        self.graph = tk.Canvas(timeline, yscrollcommand=t_yscroll.set, scrollregion=(0, 0, t_width, self.height),
                               bg="white")
        self.graph.grid(row=0, column=0, sticky=tk.NSEW)
        t_yscroll.config(command=self.graph.yview)
        # https://stackoverflow.com/a/37858368/8031185
        timeline.bind('<Enter>', self.bound_to_mousewheel)
        timeline.bind('<Leave>', self.unbound_to_mousewheel)

        self.root.update()
        self.width = self.graph.winfo_width() - margin / 4
        self.graph.yview_moveto(0)  # Start scroll at top

        self.norm_time = self.axis
        self.timeline_cursor = None
        self.timeline_pointer = None
        self.s_pointer = None
        self.s_pointer_x = self.axis - 8
        self.server_ys = []  # type: List[int]
        self.s_index = 0

        self.cur_time = 0
        self.cur_server = self.s_list[0]  # type: Server
        self.cur_job = self.jobs[self.unique_jids[0]][0]  # type: Job

    def bound_to_mousewheel(self, event) -> None:
        self.graph.bind_all("<MouseWheel>", self.on_mousewheel)

    def unbound_to_mousewheel(self, event) -> None:
        self.graph.unbind_all("<MouseWheel>")

    def on_mousewheel(self, event) -> None:
        self.graph.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def norm_times(self, arr: np.ndarray) -> np.ndarray:
        return np.interp(arr, (0, Server.end_time), (self.axis, self.width))

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

    def calc_height(self, scale: int) -> int:
        return sum(min(s.cores, scale) for s in self.s_list) * self.c_height + self.c_height * 2

    def update_server(self, server_index: Union[str, int]) -> None:
        self.s_index = int(server_index)
        self.cur_server = self.s_list[self.s_index]
        self.move_to(self.s_pointer, self.s_pointer_x, self.server_ys[self.s_index])

        replace_text(self.cur_server_text, self.cur_server.print_server_at(self.cur_time))
        replace_text(self.cur_server_jobs_text, self.cur_server.print_job_info(self.cur_time))

    def update_job(self, job_id: Union[str, int]) -> None:
        self.cur_job = job.get_job_at(self.jobs[int(job_id)], self.cur_time)
        replace_text(self.cur_job_text, self.cur_job.print_job(self.cur_time))

    def update_time(self, time: Union[str, int]) -> None:
        self.cur_time = int(time)

        self.update_server(self.s_index)
        self.update_job(self.cur_job.jid)
        replace_text(self.cur_res_text, server.print_servers_at(self.s_list, self.cur_time))

        self.norm_time = int(self.norm_times(np.array([self.cur_time]))[0])
        self.move_to(self.timeline_cursor, self.norm_time, 0)
        self.move_to(self.timeline_pointer, self.norm_time, 0)

    def move_to(self, shape, x: int, y: int):
        xy = self.graph.coords(shape)
        self.graph.move(shape, x - xy[0], y - xy[1])

    def draw(self, scale: int = None) -> None:
        last = self.c_height
        axis = self.axis - 1
        tick = 3
        s_fact = 2 ** scale
        canvas_font = font.Font(family="Courier", size=8)
        s_height = None
        self.server_ys = []

        self.graph.create_line(axis, 0, self.width, 0)  # x-axis
        self.graph.create_line(axis, 0, axis, self.height)  # y-axis

        for type_ in list(self.servers):
            type_y = last
            s_type = type_
            s_type_x = 30

            self.graph.create_text(s_type_x, type_y, text=s_type, font=canvas_font)
            self.graph.create_line(axis - tick * 3, type_y, axis, type_y)  # Server type tick mark

            for i, s in enumerate(self.servers[type_].values()):
                s_scale = min(s.cores, s_fact)
                s_height = s_scale * self.c_height

                server_y = type_y + s_height * i
                self.graph.create_line(axis - tick * 2.5, server_y, axis, server_y)  # Server ID tick mark
                self.server_ys.append(server_y - 1)

                # self.graph.draw_line(axis, server_y, self.width - self.right_margin, server_y)  # Server border

                for k in range(s_scale):
                    core_y = server_y + self.c_height * k
                    self.graph.create_line(axis - tick, core_y, axis, core_y)  # Server core tick mark

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

                        self.j_graph_ids[jb.jid].append(
                            (self.graph.create_line(
                                jb.start, job_y,
                                jb.end, job_y,
                                width=self.c_height, fill=col),
                             col)
                        )

                for fail in self.norm_server_failures(s.failures):
                    fail_y1 = server_y
                    fail_y2 = server_y + s_height - 1
                    self.graph.create_rectangle(
                        fail.fail, fail_y1,
                        fail.recover, fail_y2,
                        fill="red", outline="red"
                    )

            last = type_y + s_height * len(self.servers[type_])

        # Need to redraw these for them to persist after 'erase' call
        self.timeline_cursor = self.graph.create_line(self.norm_time, 0, self.norm_time, self.height)

        self.timeline_pointer = self.graph.create_text(self.norm_time, 0, text='▼',
                                                       font=font.Font(family="Symbol", size=20))
        self.s_pointer = self.graph.create_text(self.s_pointer_x, self.server_ys[self.s_index] - 1,
                                                text='▶', font=font.Font(family="Symbol", size=12))


vis = Visualisation()
vis.draw(5)
vis.update_time(0)
tk.mainloop()
