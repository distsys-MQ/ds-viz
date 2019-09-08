import PySimpleGUI as sg

text = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud
exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure
dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit
anim id est laborum."""

font1 = ("Times", 12)
font2 = ("Courier", 9)
font3 = ("Helvetica", 11)
font4 = ("Comic", 8)

top_tabs = sg.TabGroup(
    [[sg.Tab("Testing1", [[sg.T(text, font=font1)]], font=font1),
      sg.Tab("Testing2", [[sg.T(text, font=font2)]], font=font2)]],
    font=font1, title_color="blue", selected_title_color="red", background_color="green"
)
bottom_tabs = sg.TabGroup(
    [[sg.Tab("Testing3", [[sg.T(text, font=font3)]], font=font3),
      sg.Tab("Testing4", [[sg.T(text, font=font4)]], font=font4)]],
    font=font2
)

layout = [[top_tabs], [bottom_tabs]]
window = sg.Window("test", layout, finalize=True)

while True:
    event, values = window.Read()
    if event is None or event == 'Exit':
        break
window.Close()
