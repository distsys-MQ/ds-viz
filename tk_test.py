# https://effbot.org/tkinterbook/pack.htm
# https://effbot.org/tkinterbook/grid.htm
# https://www.python-course.eu/tkinter_layout_management.php

import tkinter as tk
from tkinter import ttk, font

root = tk.Tk()
root.geometry("800x100")
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

tk.Label(cur_server_tab, text="testing", font=courier_11).pack()
tk.Label(cur_res_tab, text="testing", font=courier_11).pack()


title = tk.Frame(root)
title.grid(row=1, column=0, sticky=tk.NSEW)

show_job_btn = tk.Button(title, text="Show Job", bg="red", fg="white", font=courier_8)
show_job_btn.pack(side=tk.LEFT)

filename = tk.Label(title, text="title", bg="grey", font=courier_11)
filename.pack(side=tk.LEFT, fill=tk.X, expand=True)

scale_label = tk.Label(title, text="Scale: ()", font=courier_11)
scale_label.pack(side=tk.LEFT)
scale_down_btn = tk.Button(title, text="-", bg="blue", fg="white", font=courier_8)
scale_down_btn.pack(side=tk.LEFT)
scale_up_btn = tk.Button(title, text="+", bg="blue", fg="white", font=courier_8)
scale_up_btn.pack(side=tk.LEFT)

tk.mainloop()
