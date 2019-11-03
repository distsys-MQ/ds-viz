#!/usr/bin/env python
"""
Based on cairo-demo/X11/cairo-demo.c
"""

import cairo
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
# https://stackoverflow.com/a/54707490/8031185

SIZE = 30


def draw(da, ctx):
    ctx.set_source_rgb(0, 0, 0)

    ctx.rectangle(50, 50, 300, 300)
    ctx.stroke()


def main():
    win = Gtk.Window()
    win.connect('destroy', lambda w: Gtk.main_quit())
    win.set_default_size(450, 550)

    drawingarea = Gtk.DrawingArea()
    win.add(drawingarea)
    drawingarea.connect('draw', draw)

    win.show_all()
    Gtk.main()


if __name__ == '__main__':
    main()
