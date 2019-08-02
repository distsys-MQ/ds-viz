import PySimpleGUI as pSG

width = 100
height = 60
text = "testing"
font = ("Courier New", 10)

pSG.SetOptions(font=font, element_padding=(0, 0))
layout = [
    [pSG.Text("Testing0")],
    [pSG.Graph((width, height), graph_bottom_left=(0, height), graph_top_right=(width, 0),
               key="graph", pad=(0, 0))]
]

window = pSG.Window("test", layout, margins=(0, 0))
graph = window.Finalize().Element("graph")
graph.DrawText("Testing1", (0, 0), font=font)
graph.DrawText("Testing2", (width, 0), font=font)
graph.DrawText("Testing3", (25, 15), font=font)
graph.DrawText("Testing4", (width/2, height/2), font=font)
graph.DrawText("Testing5", (0, height), font=font)
graph.DrawText("Testing6", (width, height), font=font)
graph.DrawText("X", (7, 45), font=font)

while True:
    event, values = window.Read()

    if event is None or event == 'Exit':
        break

window.Close()
