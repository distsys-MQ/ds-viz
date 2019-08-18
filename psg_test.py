import PySimpleGUI as sg

width = 1200
height = 100
tab_size = (75, 3)
btn_width = 10
btn_font = ("Courier New", -10)
slider_settings = {"range": (0, 100), "size": (89, 5),
                   "orientation": "h", "enable_events": True}
slider_label_size = (6, 1)

sg.SetOptions(font=("Courier New", -13), background_color="whitesmoke",
              element_padding=(0, 0), margins=(1, 1))

graph_column = [[
    sg.Graph(canvas_size=(width, height), graph_bottom_left=(0, height),
             graph_top_right=(width, 0), background_color="white",
             key="graph")]]

left_tabs = sg.TabGroup(
    [[sg.Tab("T1", [[sg.T("", size=tab_size)]]),
      sg.Tab("T2", [[sg.T("", size=tab_size)]])]])
right_tabs = sg.TabGroup(
    [[sg.Tab("T3", [[sg.T("", size=tab_size)]]),
      sg.Tab("T4", [[sg.T("", size=tab_size)]])]])

layout = [
    [left_tabs, right_tabs],
    [sg.Button("Press", size=(btn_width, 1), font=btn_font, key="press"),
     sg.T("Title", size=(104, 1), justification="center"),
     sg.T("Info", size=(30, 1), justification="right"),
     sg.Btn('-', size=(int(btn_width / 2), 1), font=btn_font),
     sg.Btn('+', size=(int(btn_width / 2), 1), font=btn_font)],
    [sg.T("S1", size=slider_label_size), sg.Slider(**slider_settings)],
    [sg.T("S2", size=slider_label_size), sg.Slider(**slider_settings)],
    [sg.T("S3", size=slider_label_size), sg.Slider(**slider_settings)],
    [sg.Column(graph_column)]
]

window = sg.Window("test", layout)
# window = sg.Window("test", layout, size=(width + 35, height + 200))
graph = window.Finalize().Element("graph")

g_font = ("Courier New", -20)
pos = 10
graph.DrawText("X", (width / 2, height / 2), font=g_font)
graph.DrawText("1", (pos, pos), font=g_font)
graph.DrawText("2", (width - pos, pos), font=g_font)
graph.DrawText("3", (pos, height - pos), font=g_font)
graph.DrawText("4", (width - pos, height - pos), font=g_font)

while True:
    event, values = window.Read()

    if event is None or event == 'Exit':
        break

    if event == "press":
        height *= 2
        graph.Widget.config(height=height)

window.Close()
