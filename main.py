from asciimatics.screen import Screen

from server import get_servers

servers = get_servers()


def demo(screen: Screen):
    while True:
        screen.refresh()
        pos = 0
        for typ, dic in servers.items():
            for i, s in dic.items():
                screen.print_at("{} {}".format(typ, i), 0, pos)
                pos += s.cores * 3

        if screen.get_key() is Screen.KEY_DOWN:
            screen.scroll()
        elif screen.get_key() is Screen.KEY_UP:
            screen.scroll_to(2)


Screen.wrapper(demo, height=2000)
