import tkinter as tk

root = tk.Tk()
root.columnconfigure(0, weight=1)
root.rowconfigure(1, weight=1)

canvas_xscroll = tk.Scrollbar(root, orient=tk.HORIZONTAL)
canvas_xscroll.grid(row=1, column=0, sticky=tk.EW)
canvas_yscroll = tk.Scrollbar(root)
canvas_yscroll.grid(row=0, column=1, sticky=tk.NS)

width = 1600
height = 800
canvas = tk.Canvas(root, bg="white", scrollregion=(0, 0, width, height),
                   xscrollcommand=canvas_xscroll.set, yscrollcommand=canvas_yscroll.set)
canvas.grid(row=0, column=0, sticky=tk.NSEW)

canvas_xscroll.config(command=canvas.xview)
canvas_yscroll.config(command=canvas.yview)

canvas.bind("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))
canvas.bind("<Shift-MouseWheel>", lambda event: canvas.xview_scroll(int(-1 * (event.delta / 120)), "units"))

canvas.bind("<4>", lambda event: canvas.yview_scroll(-1, "units"))
canvas.bind("<5>", lambda event: canvas.yview_scroll(1, "units"))


root.mainloop()
