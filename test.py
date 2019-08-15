import PySimpleGUI as pSG

pSG.SetOptions(font=("Courier New", -13), element_padding=(0, 0), margins=(1, 1))
tab_size = (70, 7)
col_size = (500, 200)

left_tabs = pSG.TabGroup(
    [[pSG.Tab("T1", [[pSG.T("Test1")]]),
      pSG.Tab("T2", [[pSG.T("Test2")]])]])
right_tabs = pSG.TabGroup(
    [[pSG.Tab("T3", [[pSG.T("Test3", size=tab_size)]]),
      pSG.Tab("T4", [[pSG.T("Test4", size=tab_size)]])]])

layout = [
    [pSG.Column([[left_tabs]], size=col_size, background_color="white"),
     pSG.Column([[right_tabs]], size=col_size, background_color="white")]
]

window = pSG.Window("test", layout, background_color="grey")

while True:
    event, values = window.Read()

    if event is None or event == 'Exit':
        break

window.Close()
