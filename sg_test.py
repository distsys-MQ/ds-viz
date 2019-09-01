import PySimpleGUI as sg

font = ("Courier New", 10)
b_colour = "blue"
sg.SetOptions(font=font, element_padding=(0, 0), margins=(1, 1), background_color=b_colour,
              text_element_background_color=b_colour, element_background_color=b_colour,
              input_elements_background_color=b_colour)

layout = [
    [sg.TabGroup(
        [[sg.Tab("T1", [[sg.T("Tab1")]]),
          sg.Tab("T2", [[sg.T("Tab2")]])]]
    )],
    [sg.T("Testing Text")],
    [sg.Slider((0, 100), orientation='h')]
]

window = sg.Window("test", layout, finalize=True)

while True:
    event, values = window.Read()

    if event is None or event == 'Exit':
        break

window.Close()
