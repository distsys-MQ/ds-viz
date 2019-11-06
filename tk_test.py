import tkinter as tk

root = tk.Tk()
root.geometry("1600x800")
root.columnconfigure(0, weight=1)
root.rowconfigure(1, weight=1)


upper = tk.Label(root, text="upper", bg="black", fg="white")
upper.grid(row=0, column=0, sticky=tk.NSEW)


middle = tk.Frame(root)
middle.grid(row=1, column=0, sticky=tk.NSEW)
middle.rowconfigure(0, weight=1)
middle.columnconfigure(0, weight=1)

yscrollbar = tk.Scrollbar(middle)
yscrollbar.grid(row=0, column=1, sticky=tk.NS)

canvas = tk.Canvas(middle, yscrollcommand=yscrollbar.set)
canvas.grid(row=0, column=0, sticky=tk.NSEW)
yscrollbar.config(command=canvas.yview)

x = 400
y1 = 50
y2 = 1500
canvas.create_line(x, y1, x, y2)

canvas.config(scrollregion=(0, 0, 1600, 1600))


lower = tk.Label(root, text="lower", bg="black", fg="white")
lower.grid(row=2, column=0, sticky=tk.NSEW)


root.mainloop()
