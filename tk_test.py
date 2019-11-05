# https://effbot.org/tkinterbook/pack.htm
# https://effbot.org/tkinterbook/grid.htm
# https://www.python-course.eu/tkinter_layout_management.php
# https://effbot.org/tkinterbook/tkinter-events-and-bindings.htm

import tkinter as tk
from tkinter import ttk, font

root = tk.Tk()
root.geometry("800x400")
root.columnconfigure(0, weight=1)

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
cur_server_text.pack()

cur_res_text = tk.Text(cur_res_tab, height=3, font=courier_11)
cur_res_text.insert(tk.END, "testing")
cur_res_text.configure(state=tk.DISABLED)
cur_res_text.pack()


title = tk.Frame(root)
title.grid(row=1, column=0, sticky=tk.NSEW)

show_job_btn = tk.Button(title, text="Show Job", bg="red", fg="white", font=courier_8)
show_job_btn.pack(side=tk.LEFT)

filename = tk.Label(title, text="title", bg="grey", font=courier_11)
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

server_slider = tk.Frame(controls)
server_slider.grid(row=0, column=0, sticky=tk.NSEW)
server_label = tk.Label(server_slider, text="Server", font=courier_11, width=6)
server_label.pack(side=tk.LEFT)
server_scale = tk.Scale(server_slider, from_=0, to=100, orient=tk.HORIZONTAL, showvalue=False)
server_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
server_spin = tk.Spinbox(server_slider, from_=0, to=100, width=12, font=courier_8)
server_spin.pack(side=tk.LEFT)


tk.mainloop()
