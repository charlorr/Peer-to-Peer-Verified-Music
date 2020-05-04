import atexit
import curses
import math
import os
import sys
import time
import traceback

import constant

from client import Client
from server import Server

class CursesBox:

    def __init__(self, h, w, y, x, title=None, scroll=True):

        self.title = title

        self.container_w = w
        self.container_h = h

        self.inner_w = w - 2
        self.inner_h = h - 2

        self.container = curses.newwin(h, w, y, x)
        self.container.box()

        if (title is not None):
            self.container.addstr(0, 1, title, curses.A_BOLD + curses.color_pair(CLI.YELLOW))

        self.container.refresh()

        self.inner = curses.newwin(h - 2, w - 2, y + 1, x + 1)
        self.inner.scrollok(scroll)
        self.inner.refresh()

    def print(self, msg='', attrs=curses.A_NORMAL, end='\n'):
        self.inner.addstr(f'{msg}{end}', attrs)
        self.inner.refresh()

    def input(self, max_chars=constant.MAX_CHARS):

        self.inner.addstr('>')

        curses.echo()
        res = self.inner.getstr(0, 2, max_chars).decode('UTF-8')
        curses.noecho()
        self.inner.clear()

        return res

    def clear(self):

        self.inner.clear()

    def refresh(self):
        self.container.refresh()
        self.inner.refresh()

class CLI:

    WHITE = 1
    RED = 2
    GREEN = 3
    YELLOW = 4

    __instance = None

    @staticmethod
    def get_instance():
        if (CLI.__instance is None):
            CLI()
        return CLI.__instance

    def __init__(self):

        if (not CLI.__instance is None):
            raise Exception('CLI is a singleton')

        self.display = curses.initscr()
        self.display.clear()
        self.display.keypad(True)
        curses.noecho()
        curses.cbreak()

        curses.start_color()
        curses.init_pair(CLI.WHITE, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(CLI.RED, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(CLI.GREEN, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(CLI.YELLOW, curses.COLOR_YELLOW, curses.COLOR_BLACK)

        lines = curses.LINES
        cols = curses.COLS
        command_h = 3
        log_percent = 40
        avail_lines = lines - command_h
        log_h = math.ceil(avail_lines * log_percent / 100.0)
        panel_h = math.floor(avail_lines * (100 - log_percent) / 100.0)

        # Side by side panels
        self.track_window = CursesBox(panel_h, cols // 2 - 1, 0, 1, 'Available Tracks:')
        self.peer_window = CursesBox(panel_h, cols // 2, 0, cols // 2 + 1, 'Peers:')

        self.log_window = CursesBox(log_h, cols - 1, avail_lines - log_h, 1, 'Status:')
        self.command_window = CursesBox(3, cols - 1, lines - command_h, 1, scroll=False)

        atexit.register(self.cleanup)

        CLI.__instance = self

    def run(self, port):

        # Start a client object to handle commands from the user
        self.client = Client(self)

        self.client.add_local_tracks()
        self.log()

        # Start a server object to handle receiving connections/requests
        self.server = Server(self, port, tracks=self.client.all_tracks, local_tracks=self.client.local_tracks)
        self.server.start()
        self.log()

        self.client.restore_peers()
        self.log()

        # Run forever
        while True:
            try:
                res = self.command_window.input()
                self.client.handle_commands(res)
            except Exception:
                self.log(traceback.format_exc())

    def log(self, msg='', color=WHITE, end='\n'):

        self.log_window.print(msg, attrs=curses.color_pair(color), end=end)

    def update_available_tracks(self, track_list):
        '''
        Update the list of available tracks.
        '''

        self.track_window.clear()

        for track in track_list:
            if (track.local):
                self.track_window.print(track, curses.color_pair(CLI.GREEN))
            else:
                self.track_window.print(track)

    def update_connected_peers(self, peer_list):
        '''
        Update the list of peers.
        '''

        self.peer_window.clear()

        for peer in peer_list:
            if (peer.connected):
                self.peer_window.print(peer, curses.color_pair(CLI.GREEN))
            else:
                self.peer_window.print(peer, curses.color_pair(CLI.RED))

    def cleanup(self):

        # return

        self.display.keypad(False)
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    def __del__(self):

        self.cleanup()

if (__name__ == '__main__'):

    # Check if port number is specified
    if (len(sys.argv) < 2):
        print('usage: ./cli.py port [folder]')
        sys.exit()

    if (len(sys.argv) >= 3):
        constant.FILE_PREFIX = sys.argv[2]

    cli = CLI.get_instance()
    cli.run(int(sys.argv[1]))
