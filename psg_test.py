import PySimpleGUI as pSG

width = 400
height = 200
layout = [
    [pSG.Graph((width, height), (0, height), (width, 0), key="graph", enable_events=True)]
]
window = pSG.Window("test", layout, margins=(0, 0))
graph = window.Finalize().Element("graph")          # type: pSG.Graph

x1 = 40
y1 = 20
x2 = 360
y2 = 180
colour = "black"
rid = graph.DrawRectangle((x1, y1), (x2, y2), fill_color=colour)

while True:
    event, values = window.Read()

    if event is None or event == 'Exit':
        break

    elif event == "graph":
        mouse = values["graph"]

        if mouse == (None, None):
            continue
        if mouse[0] in range(x1, x2) and mouse[1] in range(y1, y2):
            colour = "red" if colour == "black" else "black"
            graph.Widget.itemconfig(rid, fill=colour)

window.Close()
