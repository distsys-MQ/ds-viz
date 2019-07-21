import PySimpleGUIQt as pSG

width = 1000
height = 1000

layout = [[pSG.Graph(canvas_size=(width, height), graph_bottom_left=(0, 0),
                     graph_top_right=(width, height), key="graph")]]
window = pSG.Window("test", layout)
window.Finalize()
graph = window.Element("graph")

graph.DrawRectangle((200, 800), (800, 200))

while True:
    event, values = window.Read()
