import tkinter as tk

root = tk.Tk()
root.geometry("600x200")

scale = tk.Scale(root, from_=100, to=500, orient=tk.HORIZONTAL)
scale.pack(fill=tk.X, expand=True)
canvas = tk.Canvas(root, bg="white")
canvas.pack(fill=tk.BOTH, expand=True)

canvas.create_line(100, 0, 100, 100, fill="red")
canvas.create_line(500, 0, 500, 100, fill="red")
line = canvas.create_line(100, 0, 100, 100)


def move_line(x):
    print("x: ", x)
    root.call(canvas, "moveto", line, int(x), 0)
    print("line pos: ", canvas.coords(line))


scale.configure(command=move_line)
root.mainloop()
