import tkinter as tk
from operator import attrgetter
from tkinter import ttk, font, scrolledtext
from typing import Dict, List, Tuple

from custom_widgets import Slider
from job import Job
import server


class Visualisation:
    def __init__(self):
        config = "./configs/personal-config16.xml"
        log = "./logs/personal-config16-pl05-bf.log"
        failures = "./failures/personal-config16-pl05-failures.txt"

        self.servers = server.get_servers_from_system(log, config, failures)
        self.s_list = [s for s in server.traverse_servers(self.servers)]  # TODO Replace with calls to traverse_servers
        self.unique_jids = sorted({j.jid for s in self.s_list for j in s.jobs})
        self.jobs = {
            jid: sorted([j for s in self.s_list for j in s.jobs if j.jid == jid], key=attrgetter("schd"))
            for jid in self.unique_jids
        }  # type: Dict[int, List[Job]]
        self.j_graph_ids = {jid: [] for jid in self.unique_jids}  # type: Dict[int, List[Tuple[int, str]]]

        self.root = tk.Tk()
        self.root.geometry("1200x600")
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
        self.cur_server_text.insert(tk.END, "testing")
        self.cur_server_text.configure(state=tk.DISABLED)
        self.cur_server_text.pack(fill=tk.X, expand=True)

        self.cur_res_text = tk.Text(cur_res_tab, height=3, font=courier_11)
        self.cur_res_text.insert(tk.END, "testing")
        self.cur_res_text.configure(state=tk.DISABLED)
        self.cur_res_text.pack(fill=tk.X, expand=True)

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

        self.filename = tk.Label(title, text="title", font=courier_11)
        self.filename.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.scale_label = tk.Label(title, text="Scale: ()", font=courier_11)
        self.scale_label.pack(side=tk.LEFT)
        self.scale_down_btn = tk.Button(title, text='-', bg="blue", fg="white", font=courier_8)
        self.scale_down_btn.pack(side=tk.LEFT)
        self.scale_up_btn = tk.Button(title, text='+', bg="blue", fg="white", font=courier_8)
        self.scale_up_btn.pack(side=tk.LEFT)

        # Controls section
        controls = tk.Frame(self.root)
        controls.grid(row=2, column=0, sticky=tk.NSEW)
        controls.columnconfigure(0, weight=1)

        self.server_slider = Slider(controls, "Slider", 0, 3, ("small 0", "small 1", "medium 0", "medium 1"))
        self.server_slider.grid(row=0, column=0, sticky=tk.NSEW)
        self.job_slider = Slider(controls, "Job", 0, 100, tuple(range(0, 101)))
        self.job_slider.grid(row=1, column=0, sticky=tk.NSEW)
        self.time_slider = Slider(controls, "Time", 0, 10000, tuple(range(0, 10001)))
        self.time_slider.grid(row=2, column=0, sticky=tk.NSEW)

        # Timeline section
        timeline = tk.Frame(self.root)
        timeline.grid(row=3, column=0, sticky=tk.NSEW)
        timeline.rowconfigure(0, weight=1)
        timeline.columnconfigure(0, weight=1)

        t_yscroll = tk.Scrollbar(timeline)
        t_yscroll.grid(row=0, column=1, sticky=tk.NS)

        t_width = 1200
        t_height = 5000
        self.t_canvas = tk.Canvas(timeline, yscrollcommand=t_yscroll.set, scrollregion=(0, 0, t_width, t_height),
                                  bg="white")
        self.t_canvas.grid(row=0, column=0, sticky=tk.NSEW)
        t_yscroll.config(command=self.t_canvas.yview)
        # https://stackoverflow.com/a/37858368/8031185
        timeline.bind('<Enter>', self._bound_to_mousewheel)
        timeline.bind('<Leave>', self._unbound_to_mousewheel)

        self.root.update()
        margin = 50
        self.t_canvas.create_line(margin, margin, margin, t_height)
        self.t_canvas.create_line(margin, margin, self.t_canvas.winfo_width(), margin)

    def _bound_to_mousewheel(self, event):
        self.t_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.t_canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.t_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


Visualisation()
tk.mainloop()
