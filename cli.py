import atexit
import curses
import math
import os
import sys
import time
from typing import List

import constant
from peer import Peer
from track import Track

from client import Client
from server import Server

RED = 1
GREEN = 2

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
            self.container.addstr(0, 1, title, curses.A_BOLD + curses.color_pair(RED))

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

    def __init__(self):

        self.display = curses.initscr()
        self.display.clear()
        self.display.keypad(True)
        curses.noecho()
        curses.cbreak()

        curses.start_color()
        curses.init_pair(RED, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(GREEN, curses.COLOR_GREEN, curses.COLOR_BLACK)

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

    def run(self, port):

        # Start a server object to handle receiving connections/requests
        server = Server(self, port)
        server.start()

        # Start a client object to handle commands from the user
        client = Client(self)

        # Load peers
        self.log_window.print('Loading saved peers from disk... ')
        peers = Peer.load_from_disk()

        # Try to reconnect to each peer
        for peer in peers:
            peer.set_log(self.log_window)
            client.peer_manipulate(peer, 'add')

        self.update_connected_peers(peers)
        self.log_window.print('Done')
        self.log_window.print()

        # Load files
        self.log_window.print(f"Checking directory '{constant.FILE_PREFIX}' for media... ")

        # Only check 1 level deep
        tracks = []
        files = os.listdir(constant.FILE_PREFIX)
        for file in files:
            if (not os.path.isdir(file)):
                self.log_window.print(f"Processing '{file}'...")
                tracks.append(Track.from_file(file))

        self.update_available_tracks(tracks)
        self.log_window.print('Done')
        self.log_window.print()

        # Run forever
        while True:
            res = self.command_window.input()
            client.handle_commands(res)

    def update_available_tracks(self, track_list: List[Track]):
        '''
        Update the list of available tracks.
        '''

        self.track_window.clear()

        for track in track_list:
            if (track.local):
                self.track_window.print(track, curses.color_pair(GREEN))
            else:
                self.track_window.print(track)

    def update_connected_peers(self, peer_list: List[Peer]):
        '''
        Update the list of peers.
        '''

        self.peer_window.clear()

        for peer in peer_list:
            if (peer.connected):
                self.peer_window.print(peer, curses.color_pair(GREEN))
            else:
                self.peer_window.print(peer, curses.color_pair(RED))

    def cleanup(self):

        self.display.keypad(False)
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    def __del__(self):

        self.cleanup()

if (__name__ == '__main__'):

    # Check if port number is specified
    if len(sys.argv) < 2:
        print('usage: ./cli.py port')
        sys.exit()

    cli = CLI()
    cli.run(int(sys.argv[1]))
