import PySimpleGUI as sg

size = 400
layout = [[sg.Graph((size, size), (0, size), (size, 0), key="graph")]]
window = sg.Window("test", layout, finalize=True)

graph = window["graph"]  # type: sg.Graph

font = ("Symbol", 20)
margin = 20
mid = int(size / 2)

graph.draw_text("{} {}".format(font[0], font[1]), (margin, margin), text_location=sg.TEXT_LOCATION_BOTTOM_LEFT)
graph.draw_text("◀", (margin, mid), font=font)
graph.draw_text("▲", (mid, margin), font=font)
graph.draw_text("▶", (size - margin, mid), font=font)
graph.draw_text("▼", (mid, size - margin), font=font)

while True:
    event, values = window.Read()
    if event is None or event == 'Exit':
        break
window.Close()
