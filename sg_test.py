import PySimpleGUI as sg

num = 4
text = '\n'.join(
    ['.'.join(hex(k * num + i)[2:].zfill(2) for i in range(num)) for k in range(num)]
)

mult_size = (num * 3 - 1, num)
font_sizes = [10, 15, 20]
layout = [
    [sg.Multiline(text, size=mult_size, font=("Courier New", i), key=str(i))]
    for i in font_sizes
]
layout.append([sg.B('test')])
window = sg.Window("test", layout, margins=(0, 0), finalize=True)

while True:
    event, values = window.read()
    if event is None or event == 'Exit':
        break
    for i in font_sizes:
        window[str(i)].Widget.config(width=8)

window.close()
