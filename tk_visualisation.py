import tkinter as tk
from tkinter import ttk, font

from custom_widgets import Slider


class Visualisation:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("1600x800")
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

        yscrollbar = tk.Scrollbar(timeline)
        yscrollbar.grid(row=0, column=1, sticky=tk.NS)

        t_width = 1600
        t_height = 5000
        self.t_canvas = tk.Canvas(timeline, yscrollcommand=yscrollbar.set, scrollregion=(0, 0, t_width, t_height))
        self.t_canvas.grid(row=0, column=0, sticky=tk.NSEW)
        yscrollbar.config(command=self.t_canvas.yview)

        self.root.update()
        margin = 50
        self.t_canvas.create_line(margin, margin, margin, t_height)
        self.t_canvas.create_line(margin, margin, self.t_canvas.winfo_width(), margin)


Visualisation()
tk.mainloop()
