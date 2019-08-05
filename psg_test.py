import PySimpleGUI as pSG

width = 200
height = 600
layout = [
    [pSG.Graph((width, height), (0, height), (width, 0), key="graph", enable_events=True)],
    [pSG.Btn('<', key="left_arrow"), pSG.Btn('>', key="right_arrow")]
]
window = pSG.Window("test", layout, margins=(0, 0), size=(400, 1000))
graph = window.Finalize().Element("graph")

step = 50
tup = (0, step)


def draw(bounds):
    y = 10

    for i in range(*bounds):
        y += 10
        graph.DrawText(i, (width / 2, y), font=("Courier New", 10))


draw(tup)

while True:
    event, values = window.Read()

    if event is None or event == 'Exit':
        break

    elif event == "left_arrow":
        graph.Erase()
        tup = tuple((i - step for i in tup))
        draw(tup)

    elif event == "right_arrow":
        graph.Erase()
        tup = tuple(i + step for i in tup)
        draw(tup)

window.Close()
