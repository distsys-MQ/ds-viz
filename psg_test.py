import PySimpleGUI as pSG

width = 200
height = 600
layout = [
    [pSG.Graph((width, height), (0, height), (width, 0), key="graph", enable_events=True)]
]
window = pSG.Window("test", layout, margins=(0, 0))
graph = window.Finalize().Element("graph")

margin = 10
axis = width / 2
step = 5
min_tick_size = 3
maj_tick_size = min_tick_size * 2
graph.DrawLine((axis, margin), (axis, height - margin))

for i in range(margin, height - margin, step):
    graph.DrawLine((axis - min_tick_size, i), (axis, i))

for i in range(margin, height - margin, step * 3):
    graph.DrawLine((axis - maj_tick_size, i), (axis, i))

while True:
    event, values = window.Read()

    if event is None or event == 'Exit':
        break

window.Close()
