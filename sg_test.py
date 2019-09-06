import PySimpleGUI as sg

font = ("Courier New", 10)
sg.SetOptions(font=font, background_color="whitesmoke",
              element_padding=(0, 0), margins=(1, 1))

dum_win = sg.Window("dummy", [[]], finalize=True)
base_px = sg.tkinter.font.Font().measure('A')  # ("Courier New", 16)
f_px = sg.tkinter.font.Font(font=font).measure('A')

f_pxs = {
    10: sg.tkinter.font.Font(font=("Courier New", 10)).measure('A'),
    7: sg.tkinter.font.Font(font=("Courier New", 7)).measure('A'),
}

dum_win.Close()

length = 100
width = base_px * length
height = 100

graph_column = [[
    sg.Graph(canvas_size=(width, height), graph_bottom_left=(0, height),
             graph_top_right=(width, 0), background_color="white",
             key="graph")]]

slider_label_size = (6, 1)
slider_settings = {"range": (0, 100), "size": (length - 5, 5),
                   "orientation": "h", "enable_events": True}

title_f_width = (base_px / f_pxs[font[1]]) * length

btn_font = ("Courier New", 7)
btn_width = 8
btn_f_width = ((base_px / f_pxs[font[1]]) / (base_px / f_pxs[btn_font[1]])) * btn_width * 1.3

info_width = 30
title_length = int(title_f_width - info_width - btn_f_width * 2)

print("base font px:", base_px)
print("main font px:", f_pxs[font[1]])
print("btn font px:", f_pxs[btn_font[1]])
print("title font width:", title_f_width)

layout = [
    [sg.Button("Press", size=(btn_width, 1), font=btn_font, key="press"),
     sg.T("Title", size=(title_length, 1), justification="center"),
     sg.T("Info", size=(info_width, 1), justification="right"),
     sg.Btn('-', size=(int(btn_width / 2), 1), font=btn_font),
     sg.Btn('+', size=(int(btn_width / 2), 1), font=btn_font)],
    [sg.T('0' * int(title_f_width), font=font)],
    [sg.T('0' * 260,  font=btn_font)],
    [sg.Column([[sg.Sizer(width, base_px * 4)]], background_color="blue")],
    [sg.T("S1", size=slider_label_size), sg.Slider(**slider_settings)],
    [sg.T("S2", size=slider_label_size), sg.Slider(**slider_settings)],
    [sg.T("S3", size=slider_label_size), sg.Slider(**slider_settings)],
    [sg.Column(graph_column)]
]

window = sg.Window("test", layout, resizable=True, finalize=True)
print(window["press"].Widget.winfo_width())
graph = window["graph"]

g_font = ("Courier New", 15)
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
