# https://effbot.org/tkinterbook/pack.htm
# https://effbot.org/tkinterbook/grid.htm
# https://www.python-course.eu/tkinter_layout_management.php

import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.geometry("800x100")

status = tk.Frame(root)

left_tabs = ttk.Notebook(status)
tab_a = tk.Frame(left_tabs)
tab_b = tk.Frame(left_tabs)
left_tabs.add(tab_a, text="a")
left_tabs.add(tab_b, text="b")
# left_tabs.pack(side=tk.LEFT, fill=tk.X, expand=True)
left_tabs.grid(row=0, column=0, sticky=tk.NSEW)

right_tabs = ttk.Notebook(status)
tab_c = tk.Frame(right_tabs)
tab_d = tk.Frame(right_tabs)
tab_e = tk.Frame(right_tabs)
right_tabs.add(tab_c, text="c")
right_tabs.add(tab_d, text="d")
right_tabs.add(tab_e, text="a very very very long tab title")
# right_tabs.pack(side=tk.LEFT, fill=tk.X, expand=True)
right_tabs.grid(row=0, column=1, sticky=tk.NSEW)

tk.Label(tab_a, text="testing").pack()
tk.Label(tab_c, text="testing").pack()

status.columnconfigure(0, weight=1)
status.columnconfigure(1, weight=1)
status.pack(fill=tk.X)

title = tk.Label(root, text="title", bg="grey")
title.pack(fill=tk.X)

tk.mainloop()
