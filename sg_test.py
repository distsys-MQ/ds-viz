import sys

import PySimpleGUI as sg


def maximise(win):
    if sys.platform == "linux":
        win.TKroot.attributes("-zoomed", True)
    else:
        win.maximize()


win1 = sg.Window("win1", [[]], finalize=True)
res = win1.get_screen_dimensions()
win1.close()

win2 = sg.Window("win2", [[sg.Sizer(res[0], res[1])]], resizable=True,
                 margins=(0, 0), element_padding=(0, 0), finalize=True)
maximise(win2)
size = win2.Size
win2.close()

window = sg.Window("window", [[sg.Column([[sg.Sizer(size[0], size[1])]], background_color="blue")]],
                   margins=(0, 0), element_padding=(0, 0), resizable=True, return_keyboard_events=True, finalize=True)

print("res:", res)
print("size:", size)

while True:
    event, values = window.Read()
    if event is None or event == 'Exit':
        break
    if event == "a":
        print(window.Size)
window.Close()
