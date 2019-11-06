import tkinter as tk
from tkinter import font
from typing import Union, Tuple


class Slider(tk.Frame):
    def __init__(self, parent: tk.Widget, slider_label: str, from_: int, to: int,
                 values: Union[Tuple[int, ...], Tuple[str, ...]]):
        tk.Frame.__init__(self, parent)

        label_width = 6
        label_font = font.Font(family="Courier", size=11)
        self.label = tk.Label(self, text=slider_label, width=label_width, font=label_font)
        self.label.pack(side=tk.LEFT)

        self.scale = tk.Scale(self, from_=from_, to=to, orient=tk.HORIZONTAL, showvalue=False)
        self.scale.pack(side=tk.LEFT, fill=tk.X, expand=True)

        spin_width = 12
        spin_font = font.Font(family="Courier", size=8)
        self.spin = tk.Spinbox(self, values=values, width=spin_width, font=spin_font)
        self.spin.pack(side=tk.LEFT)