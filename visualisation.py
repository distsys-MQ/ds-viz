import math
import os
import sys
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

# Constants
SCALE_STRING = "Scale: {} ({} max cores)"
HIGHLIGHT = "yellow"
RED = "#e50000"
BLUE = "#0000b2"
GREEN = "#005900"


def truncate(text: str, length: int = 10) -> str:
    return text if len(text) <= length else text[:length - 3] + ".."


def replace_text(element: Union[tk.Text, tk.Spinbox], text: Union[str, int]) -> None:
    if isinstance(element, tk.Text):
        index = 1.0
        element.config(state=tk.NORMAL)
        element.delete(index, tk.END)
        element.insert(tk.END, text)
        element.config(state=tk.DISABLED)
    else:
        index = 0
        element.delete(index, tk.END)
        element.insert(tk.END, text)


class Visualisation:
    def __init__(self, config: str, failures: str, log: str, core_height: int = 4, scale: int = 0, width: int = 1):
        self.core_height = core_height

        # Simulation log data
        self.servers = server.get_servers_from_system(log, config, failures)
        # Look into replacing server_list with calls to traverse_servers
        self.server_list = [s for s in server.traverse_servers(self.servers)]  # type: List[Server]
        self.unique_jids = sorted({j.jid for s in self.server_list for j in s.jobs})
        self.jobs = {
            jid: sorted([j for s in self.server_list for j in s.jobs if j.jid == jid], key=attrgetter("schd"))
            for jid in self.unique_jids
        }  # type: Dict[int, List[Job]]
        self.job_graph_ids = {jid: [] for jid in self.unique_jids}  # type: Dict[int, List[Tuple[int, str]]]

        self.max_scale = int(math.log(max(s.cores for s in self.server_list), 2))
        self.cur_scale = min(scale, self.max_scale)
        scale_factor = 2 ** self.cur_scale

        # GUI construction
        root = tk.Tk()
        root.title("ds-viz")
        root.columnconfigure(0, weight=1)  # Fill window width
        root.rowconfigure(3, weight=1)  # Timeline fills remaining window height

        # Fonts
        self.font_family = "Liberation Mono"
        self.font_family = self.font_family if self.font_family in font.families() else "Courier"
        small_font = font.Font(family=self.font_family, size=8)
        large_font = font.Font(family=self.font_family, size=11)

        background_colour = "white"
        text_colour = {"fg": "black", "bg": background_colour}
        root.configure(bg=background_colour)

        # Status section
        status = tk.Frame(root, bg=background_colour)
        status.columnconfigure(0, weight=1, uniform="notebook")
        status.columnconfigure(1, weight=1, uniform="notebook")
        status.grid(row=0, column=0, sticky=tk.NSEW)

        left_tabs = ttk.Notebook(status)
        cur_server_tab = tk.Frame(left_tabs, bg=background_colour)
        cur_job_tab = tk.Frame(left_tabs, bg=background_colour)
        left_tabs.add(cur_server_tab, text="Current Server")
        left_tabs.add(cur_job_tab, text="Current Job")
        left_tabs.grid(row=0, column=0, sticky=tk.NSEW)

        right_tabs = ttk.Notebook(status)
        cur_res_tab = tk.Frame(right_tabs, bg=background_colour)
        final_res_tab = tk.Frame(right_tabs, bg=background_colour)
        cur_server_jobs_tab = tk.Frame(right_tabs, bg=background_colour)
        right_tabs.add(cur_res_tab, text="Current Results")
        right_tabs.add(final_res_tab, text="Final Results")
        right_tabs.add(cur_server_jobs_tab, text="Current Server Jobs")
        right_tabs.grid(row=0, column=1, sticky=tk.NSEW)

        self.cur_server_text = tk.Text(cur_server_tab, height=3, font=large_font, **text_colour)
        self.cur_server_text.pack(fill=tk.X, expand=True)
        self.cur_job_text = tk.Text(cur_job_tab, height=3, font=large_font, **text_colour)
        self.cur_job_text.pack(fill=tk.X, expand=True)
        self.cur_res_text = tk.Text(cur_res_tab, height=3, font=large_font, **text_colour)
        self.cur_res_text.pack(fill=tk.X, expand=True)
        self.cur_server_jobs_text = tk.Text(cur_server_jobs_tab, height=4, font=small_font, **text_colour)
        self.cur_server_jobs_text.pack(fill=tk.X, expand=True)

        final_res_text = scrolledtext.ScrolledText(final_res_tab, height=3, font=small_font, **text_colour)
        final_res_text.grid(row=0, column=0, sticky=tk.NSEW)
        final_res_tab.rowconfigure(0, weight=1)
        final_res_tab.columnconfigure(0, weight=1)
        final_res_text.insert(tk.END, server.get_results(log))
        final_res_text.configure(state=tk.DISABLED)

        # Title section
        title = tk.Frame(root, bg=background_colour)
        title.grid(row=1, column=0, sticky=tk.NSEW)

        self.show_job = False
        self.show_job_btn = tk.Button(title, text="Show Job", bg=RED, fg="white", font=small_font,
                                      command=self.show_job_callback)
        self.show_job_btn.pack(side=tk.LEFT)

        self.filename = tk.Label(title, text="Visualising: {}".format(os.path.basename(log)),
                                 font=font.Font(family=self.font_family, size=11, underline=True), **text_colour)
        self.filename.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.scale_label = tk.Label(title, text=SCALE_STRING.format(self.cur_scale, scale_factor),
                                    font=large_font, **text_colour)
        self.scale_label.pack(side=tk.LEFT)
        btn_width = 4
        self.scale_down_btn = tk.Button(title, text='-', bg=BLUE, fg="white", font=small_font, width=btn_width,
                                        command=self.decrease_scale)
        self.scale_down_btn.pack(side=tk.LEFT)
        self.scale_up_btn = tk.Button(title, text='+', bg=BLUE, fg="white", font=small_font, width=btn_width,
                                      command=self.increase_scale)
        self.scale_up_btn.pack(side=tk.LEFT)

        # Controls section
        controls = tk.Frame(root, bg=background_colour)
        controls.grid(row=2, column=0, sticky=tk.NSEW)
        controls.columnconfigure(0, weight=1)

        self.server_slider = Slider(controls, "Server", 0, len(self.server_list) - 1,
                                    tuple((str(s) for s in server.traverse_servers(self.servers))),
                                    lambda s_index: self.update_server(int(s_index)), self.server_spin_callback)
        self.server_slider.grid(row=0, column=0, sticky=tk.NSEW)
        self.job_slider = Slider(controls, "Job", min(self.unique_jids), max(self.unique_jids), tuple(self.unique_jids),
                                 lambda jid: self.update_job(int(jid)), self.job_spin_callback)
        self.job_slider.grid(row=1, column=0, sticky=tk.NSEW)
        self.time_slider = Slider(controls, "Time", 0, Server.end_time, tuple(range(0, Server.end_time)),
                                  lambda t: self.update_time(int(t)), self.time_spin_callback)
        self.time_slider.grid(row=2, column=0, sticky=tk.NSEW)

        # Timeline section
        timeline = tk.Frame(root, bg=background_colour)
        timeline.grid(row=3, column=0, sticky=tk.NSEW)
        timeline.rowconfigure(0, weight=1)
        timeline.columnconfigure(0, weight=1)

        graph_xscroll = tk.Scrollbar(timeline, orient=tk.HORIZONTAL)
        graph_xscroll.grid(row=1, column=0, sticky=tk.EW)
        graph_yscroll = tk.Scrollbar(timeline)
        graph_yscroll.grid(row=0, column=1, sticky=tk.NS)

        self.height = self.calc_height(scale_factor)
        self.graph = tk.Canvas(timeline, bg=background_colour,
                               xscrollcommand=graph_xscroll.set, yscrollcommand=graph_yscroll.set)
        self.graph.grid(row=0, column=0, sticky=tk.NSEW)

        graph_xscroll.config(command=self.graph.xview)
        graph_yscroll.config(command=self.graph.yview)

        if sys.platform == "linux":
            root.attributes("-zoomed", True)
        else:
            root.state("zoomed")

        # Variables for runtime use
        margin = small_font.measure("0" * 6)
        self.axis = margin * 2
        self.norm_time = self.axis
        self.timeline_cursor = None
        self.timeline_pointer = None
        self.server_pointer = None
        self.server_pointer_x = self.axis - self.axis / 7
        self.pointer_size = self.server_pointer_x / 15
        self.server_ys = [self.core_height]  # type: List[int]

        self.cur_time = 0
        self.server_index = 0
        self.cur_server = self.server_list[self.server_index]  # type: Server
        self.cur_job = self.jobs[self.unique_jids[0]][0]  # type: Job

        self.width = 0  # Prevents an AttributeError when callback methods are executed during the update() call
        root.update()
        self.width = self.graph.winfo_width() * width - margin / 4
        self.graph.config(scrollregion=(0, 0, self.width, self.height))
        self.graph.yview_moveto(0)  # Start scroll at top

        # Windows scrolling
        self.graph.bind("<MouseWheel>", lambda e: self.graph.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        self.graph.bind("<Shift-MouseWheel>", lambda e: self.graph.xview_scroll(int(-1 * (e.delta / 120)), "units"))

        # Linux scrolling
        self.graph.bind("<4>", lambda _: self.graph.yview_scroll(-1, "units"))
        self.graph.bind("<5>", lambda _: self.graph.yview_scroll(1, "units"))
        self.graph.bind("<Shift-4>", lambda _: self.graph.xview_scroll(-1, "units"))
        self.graph.bind("<Shift-5>", lambda _: self.graph.xview_scroll(1, "units"))

    def server_spin_callback(self, _=None) -> None:
        server_info = self.server_slider.spin.get().split()  # type: List[str]

        if len(server_info) == 2:
            server_type = server_info[0]

            if server_info[1].isdigit():
                server_id = int(server_info[1])

                if server_type in self.servers and server_id in self.servers[server_type]:
                    cur_server = self.servers[server_type][server_id]
                    server_index = self.server_list.index(cur_server)
                    self.update_server(server_index)
                    self.server_slider.scale.set(server_index)

    def job_spin_callback(self, _=None) -> None:
        spin_value = self.job_slider.spin.get()  # type: str
        job_id = int(spin_value) if spin_value.isdigit() else -1

        if job_id in self.unique_jids:
            self.update_job(job_id)
            self.job_slider.scale.set(job_id)

    def time_spin_callback(self, _=None) -> None:
        spin_value = self.time_slider.spin.get()  # type: str
        time = int(spin_value) if spin_value.isdigit() else -1

        if time in range(0, Server.end_time):
            self.update_time(time)
            self.time_slider.scale.set(time)

    def show_job_callback(self) -> None:
        self.show_job = not self.show_job

        if self.show_job:
            self.show_job_btn.config(bg=GREEN)
            self.change_job_colour(self.cur_job, HIGHLIGHT)
        else:
            self.show_job_btn.config(bg=RED)
            self.reset_job_colour(self.cur_job)

    def change_job_colour(self, j: Job, col: str) -> None:
        for j_graph_id, _ in self.job_graph_ids[j.jid]:
            self.graph.itemconfig(j_graph_id, fill=col)

    def reset_job_colour(self, j: Job):
        for j_graph_id, orig_col in self.job_graph_ids[j.jid]:
            self.graph.itemconfig(j_graph_id, fill=orig_col)

    def change_scaling(self, scale: int) -> None:
        self.graph.delete("all")

        scale_factor = 2 ** scale
        self.height = self.calc_height(scale_factor)
        self.graph.config(height=self.height, scrollregion=(0, 0, self.width, self.height))

        self.draw(scale)
        self.scale_label.config(text=SCALE_STRING.format(scale, scale_factor))

        if self.show_job:
            self.change_job_colour(self.cur_job, HIGHLIGHT)

    def decrease_scale(self) -> None:
        if self.cur_scale <= 0:
            pass
        else:
            self.cur_scale -= 1
            self.change_scaling(self.cur_scale)

    def increase_scale(self) -> None:
        if self.cur_scale >= self.max_scale:
            pass
        else:
            self.cur_scale += 1
            self.change_scaling(self.cur_scale)

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
        return sum(min(s.cores, scale) for s in self.server_list) * self.core_height + self.core_height * 2

    def update_server(self, server_index: int) -> None:
        self.server_index = server_index
        self.cur_server = self.server_list[self.server_index]
        self.move_to(self.server_pointer, self.server_pointer_x, self.server_ys[self.server_index] - self.pointer_size)

        replace_text(self.cur_server_text, self.cur_server.print_server_at(self.cur_time))
        replace_text(self.cur_server_jobs_text, self.cur_server.print_job_info(self.cur_time))
        replace_text(self.server_slider.spin, "{} {}".format(self.cur_server.type_, self.cur_server.sid))

    def update_job(self, job_id: Union[str, int]) -> None:
        old_job = self.cur_job
        self.cur_job = job.get_job_at(self.jobs[job_id], self.cur_time)
        replace_text(self.cur_job_text, self.cur_job.print_job(self.cur_time))
        replace_text(self.job_slider.spin, self.cur_job.jid)

        if self.show_job:
            self.reset_job_colour(old_job)
            self.change_job_colour(self.cur_job, HIGHLIGHT)

    def update_time(self, time: int) -> None:
        self.cur_time = time

        self.update_server(self.server_index)
        self.update_job(self.cur_job.jid)
        replace_text(self.cur_res_text, server.print_servers_at(self.server_list, self.cur_time))
        replace_text(self.time_slider.spin, time)

        self.norm_time = int(self.norm_times(np.array([self.cur_time]))[0])
        self.move_to(self.timeline_cursor, self.norm_time, 0)
        self.move_to(self.timeline_pointer, self.norm_time, 0)

    def move_to(self, shape, x: int, y: int) -> None:
        if shape:
            xy = self.graph.coords(shape)
            self.graph.move(shape, x - xy[0], y - xy[1])

    def draw(self, scale: int) -> None:
        last = self.core_height
        axis = self.axis - 1
        scale_factor = 2 ** scale
        canvas_font = font.Font(family=self.font_family, size=8)
        tick = canvas_font.measure("0") / 2
        server_height = None
        self.server_ys = []

        self.graph.create_line(axis, 0, self.width, 0)  # x-axis
        self.graph.create_line(axis, 0, axis, self.height)  # y-axis

        for type_ in list(self.servers):
            server_type = truncate(type_)
            server_type_x = canvas_font.measure("0" * 5)
            server_type_y = last

            self.graph.create_text(server_type_x, server_type_y, text=server_type, font=canvas_font)
            self.graph.create_line(axis - tick * 3, server_type_y, axis, server_type_y)  # Server type tick mark

            for i, s in enumerate(self.servers[type_].values()):
                server_scale = min(s.cores, scale_factor)
                server_height = server_scale * self.core_height

                server_y = server_type_y + server_height * i
                self.graph.create_line(axis - tick * 2.5, server_y, axis, server_y)  # Server ID tick mark
                self.server_ys.append(server_y)

                # self.graph.draw_line(axis, server_y, self.width - self.right_margin, server_y)  # Server border

                for k in range(server_scale):
                    core_y = server_y + self.core_height * k
                    self.graph.create_line(axis - tick, core_y, axis, core_y)  # Server core tick mark

                jobs = self.norm_jobs(s.jobs)
                for jb in jobs:
                    job_scale = min(jb.cores, scale_factor)

                    # Only check if previous jobs are overlapping, later jobs should be stacked on previous jobs
                    overlap = list(filter(lambda j: j.is_overlapping(jb), jobs[:jobs.index(jb)]))
                    used_cores = overlap[-1].last_core + 1 if overlap else 0

                    # Draw a job bar for every core used by the job, up to the scaling factor
                    for k in range(job_scale):
                        # Offset by number of job's cores + sum of cores used by concurrent jobs
                        # If offset would exceed server height, reset to the top
                        # Also need to adjust y position by half c_height to align job bar edge with server ticks
                        job_core = (used_cores + k) % server_scale
                        job_y = server_y + job_core * self.core_height + self.core_height * 0.5
                        jb.last_core = job_core

                        if not jb.will_fail and jb.fails == 0:
                            colour = "green"
                        else:
                            base_colour = 180
                            fail_colour = max(base_colour - jb.fails, 0)  # Can't be darker than black (0, 0, 0)
                            colour = "#{0:02X}{0:02X}{0:02X}".format(fail_colour)

                        self.job_graph_ids[jb.jid].append(
                            (self.graph.create_line(
                                jb.start, job_y,
                                jb.end, job_y,
                                width=self.core_height, fill=colour),
                             colour)
                        )

                for fail in self.norm_server_failures(s.failures):
                    fail_y1 = server_y
                    fail_y2 = server_y + server_height - 1
                    self.graph.create_rectangle(
                        fail.fail, fail_y1,
                        fail.recover, fail_y2,
                        fill="red", outline="red"
                    )

            last = server_type_y + server_height * len(self.servers[type_])

        # Need to redraw these for them to persist after 'erase' call
        self.timeline_cursor = self.graph.create_line(
            self.norm_time, 0, self.norm_time, self.height)

        self.timeline_pointer = self.graph.create_text(
            self.norm_time, 0, text='▼', font=font.Font(family="Symbol", size=self.core_height + 5))

        server_pointer_coords = [
            self.server_pointer_x, self.server_ys[self.server_index] - self.pointer_size,
            axis, self.server_ys[self.server_index],
            self.server_pointer_x, self.server_ys[self.server_index] + self.pointer_size
        ]
        self.server_pointer = self.graph.create_polygon(server_pointer_coords, outline="black", fill="black")

    def run(self) -> None:
        self.draw(self.cur_scale)
        self.update_time(0)
        self.graph.tk.mainloop()
