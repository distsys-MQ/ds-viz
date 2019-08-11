import PySimpleGUI as pSG

# https://github.com/PySimpleGUI/PySimpleGUI/issues/1380
# https://github.com/PySimpleGUI/PySimpleGUI/issues/1765
# https://github.com/PySimpleGUI/PySimpleGUI/issues/1362

pSG.SetOptions(font=("Courier New", -20), element_padding=(0, 0), margins=(0, 0))
btn_size = (4, 2)
h_spacer = pSG.T("=" * 17)
v_spacer = pSG.T("=\n" * 8)
layout = [
    [pSG.Btn("NW", size=btn_size), h_spacer, pSG.Btn("N", size=btn_size), h_spacer, pSG.Btn("NE", size=btn_size)],
    [v_spacer],
    [pSG.Btn("W", size=btn_size), h_spacer, pSG.Btn("+", size=btn_size), h_spacer, pSG.Btn("E", size=btn_size)],
    [v_spacer],
    [pSG.Btn("SW", size=btn_size), h_spacer, pSG.Btn("S", size=btn_size), h_spacer, pSG.Btn("SE", size=btn_size)]
]
window = pSG.Window("test", layout, size=(600, 600))

while True:
    event, values = window.Read()

    if event is None or event == 'Exit':
        break

window.Close()
