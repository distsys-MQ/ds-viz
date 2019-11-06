# https://effbot.org/tkinterbook/pack.htm
# https://effbot.org/tkinterbook/grid.htm
# https://www.python-course.eu/tkinter_layout_management.php
# https://effbot.org/tkinterbook/tkinter-events-and-bindings.htm

import tkinter as tk
from tkinter import ttk, font

from custom_widgets import Slider

root = tk.Tk()
root.geometry("1600x800")
root.columnconfigure(0, weight=1)
root.rowconfigure(3, weight=1)

courier_8 = font.Font(family="Courier", size=8)
courier_11 = font.Font(family="Courier", size=11)
# ttk.Style().configure("Courier.TLabel", font=courier_11)

status = tk.Frame(root)
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

cur_server_text = tk.Text(cur_server_tab, height=3, font=courier_11)
cur_server_text.insert(tk.END, "testing")
cur_server_text.configure(state=tk.DISABLED)
cur_server_text.pack(fill=tk.X, expand=True)

cur_res_text = tk.Text(cur_res_tab, height=3, font=courier_11)
cur_res_text.insert(tk.END, "testing")
cur_res_text.configure(state=tk.DISABLED)
cur_res_text.pack(fill=tk.X, expand=True)


title = tk.Frame(root)
title.grid(row=1, column=0, sticky=tk.NSEW)

show_job_btn = tk.Button(title, text="Show Job", bg="red", fg="white", font=courier_8)
show_job_btn.pack(side=tk.LEFT)

filename = tk.Label(title, text="title", font=courier_11)
filename.pack(side=tk.LEFT, fill=tk.X, expand=True)

scale_label = tk.Label(title, text="Scale: ()", font=courier_11)
scale_label.pack(side=tk.LEFT)
scale_down_btn = tk.Button(title, text='-', bg="blue", fg="white", font=courier_8)
scale_down_btn.pack(side=tk.LEFT)
scale_up_btn = tk.Button(title, text='+', bg="blue", fg="white", font=courier_8)
scale_up_btn.pack(side=tk.LEFT)


controls = tk.Frame(root)
controls.grid(row=2, column=0, sticky=tk.NSEW)
controls.columnconfigure(0, weight=1)

server_slider = Slider(controls, "Slider", 0, 3, ("small 0", "small 1", "medium 0", "medium 1"))
server_slider.grid(row=0, column=0, sticky=tk.NSEW)
job_slider = Slider(controls, "Job", 0, 100, tuple(range(0, 101)))
job_slider.grid(row=1, column=0, sticky=tk.NSEW)
time_slider = Slider(controls, "Time", 0, 10000, tuple(range(0, 10001)))
time_slider.grid(row=2, column=0, sticky=tk.NSEW)


timeline = tk.Frame(root)
timeline.grid(row=3, column=0, sticky=tk.NSEW)
timeline.rowconfigure(0, weight=1)
timeline.columnconfigure(0, weight=1)

yscrollbar = tk.Scrollbar(timeline)
yscrollbar.grid(row=0, column=1, sticky=tk.NS)

t_width = 1600
t_height = 5000
t_canvas = tk.Canvas(timeline, yscrollcommand=yscrollbar.set, scrollregion=(0, 0, t_width, t_height))
t_canvas.grid(row=0, column=0, sticky=tk.NSEW)
yscrollbar.config(command=t_canvas.yview)
root.update()

margin = 50
t_canvas.create_line(margin, margin, margin, t_height)
t_canvas.create_line(margin, margin, t_canvas.winfo_width(), margin)

tk.mainloop()
