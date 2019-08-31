import PySimpleGUI as sg

font = ("Courier New", -16)
sg.set_options(font=font, element_padding=(0, 0), margins=(0, 0))

dum_win = sg.Window("dummy", [[]], finalize=True)
f_px = sg.tkinter.font.Font(font=font).measure('A')
print(f_px)
dum_win.Close()

num = 16
text = ['.'.join(hex(k * num + i)[2:].zfill(2) for i in range(num)) for k in range(num)]
col = [[
    sg.T('\n'.join(text))
]]

width = len(text[0]) * f_px + f_px
height = num * f_px * 2
layout = [
    [sg.Column(col, size=(width, height))]
]

window = sg.Window("test", layout, finalize=True)

while True:
    event, values = window.read()

    if event is None or event == 'Exit':
        break

window.Close()
