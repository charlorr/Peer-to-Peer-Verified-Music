import curses
import time

import constant

RED = 1
GREEN = 2

class CursesBox:

    def __init__(self, h, w, y, x, title=None):

        self.title = title

        self.container_w = w
        self.container_h = h

        self.inner_w = w - 2
        self.inner_h = h - 2

        self.container = curses.newwin(h, w, y, x)
        self.container.box()

        if (title is not None):
            self.container.addstr(0, 1, title, curses.A_BOLD + curses.color_pair(RED))

        self.container.refresh()

        self.inner = curses.newwin(h - 2, w - 2, y + 1, x + 1)
        self.inner.refresh()

    def print(self, msg='', end='\n'):
        self.inner.addstr(f'{end}{msg}')
        self.inner.refresh()

    def input(self, max_chars=constant.MAX_CHARS):

        self.inner.addstr('>')

        curses.echo()
        res = self.inner.getstr(0, 2, max_chars).decode('UTF-8')
        curses.noecho()
        self.inner.clear()

        return res

    def refresh(self):
        self.container.refresh()
        self.inner.refresh()

class CLI:

    def __init__(self):

        self.display = curses.initscr()
        self.display.clear()
        self.display.keypad(True)
        curses.noecho()
        curses.cbreak()

        curses.start_color()
        curses.init_pair(RED, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(GREEN, curses.COLOR_GREEN, curses.COLOR_BLACK)

        self.command_window = CursesBox(3, curses.COLS - 1, curses.LINES - 3, 1)
        self.track_window = CursesBox(curses.LINES - 3, curses.COLS // 2 - 1, 0, 1, 'Available Tracks:')
        self.peer_window = CursesBox(curses.LINES - 3, curses.COLS // 2, 0, curses.COLS // 2 + 1, 'Connected Peers:')

    def run(self):

        while True:
            res = self.command_window.input()
            self.track_window.print(res)

    def __del__(self):

        self.display.keypad(False)
        curses.nocbreak()
        curses.echo()
        curses.endwin()

if (__name__ == '__main__'):
    cli = CLI()
    cli.run()
