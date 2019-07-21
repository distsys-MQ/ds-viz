import PySimpleGUI as pSG

width = 1200
height = 35000
margin = 30

column = [[pSG.Graph(canvas_size=(width, height), graph_bottom_left=(0, 0),
                     graph_top_right=(width, height), key="graph")]]
layout = [[pSG.Column(column, scrollable=True, vertical_scroll_only=True,
                      background_color="whitesmoke")]]
window = pSG.Window("test", layout, background_color="whitesmoke", resizable=True)
window.Finalize()
graph = window.Element("graph")

for i in range(4000):
    if i == 3273:
        print(height - i)
    y = height - (i * 10 + margin)
    graph.DrawText(f"{i}", (margin, y))

while True:
    event, values = window.Read()
