import PySimpleGUI as pSG

width = 1200
height = 600
tab_size = (74, 3)
btn_width = 10
btn_font = ("Courier New", -10)
slider_settings = {"range": (0, 100), "size": (89, 5),
                   "orientation": "h", "enable_events": True}
slider_label_size = (6, 1)

pSG.SetOptions(font=("Courier New", -13), background_color="whitesmoke",
               element_padding=(0, 0), margins=(1, 1))

graph_column = [[
    pSG.Graph(canvas_size=(width, height), graph_bottom_left=(0, height),
              graph_top_right=(width, 0), background_color="white",
              key="graph")]]

left_tabs = pSG.TabGroup(
    [[pSG.Tab("T1", [[pSG.T("Test1", size=tab_size)]]),
      pSG.Tab("T2", [[pSG.T("Test2", size=tab_size)]])]])
right_tabs = pSG.TabGroup(
    [[pSG.Tab("T3", [[pSG.T("Test3", size=tab_size)]]),
      pSG.Tab("T4", [[pSG.T("Test4", size=tab_size)]])]])

col_width = width + 28
layout = [
    [pSG.Column([[left_tabs, right_tabs]], size=(col_width, 85))],
    [pSG.Column([[
        pSG.Button("Press", size=(btn_width, 1), font=btn_font),
        pSG.T("Title", size=(104, 1), justification="center"),
        pSG.T("Info", size=(30, 1), justification="right"),
        pSG.Btn('-', size=(int(btn_width / 2), 1), font=btn_font),
        pSG.Btn('+', size=(int(btn_width / 2), 1), font=btn_font)]], size=(col_width, 30))],
    [pSG.Column([
        [pSG.T("S1", size=slider_label_size), pSG.Slider(**slider_settings)],
        [pSG.T("S2", size=slider_label_size), pSG.Slider(**slider_settings)],
        [pSG.T("S3", size=slider_label_size), pSG.Slider(**slider_settings)]], size=(col_width, 90))],
    [pSG.Column(graph_column, size=(col_width, height))],
]

window = pSG.Window("test", layout)
# window = pSG.Window("test", layout, size=(width + 35, height + 200))
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

window.Close()
