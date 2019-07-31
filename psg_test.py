import PySimpleGUI as pSG

pSG.SetOptions(font=("Helvetica", 10))
layout = [
    [pSG.Text("=" * 162)],
    [pSG.Slider(range=(0, 1000), default_value=0, size=(100, 15), orientation="h")]
]
window = pSG.Window("test", layout)
window.Finalize()

while True:
    event, values = window.Read()
