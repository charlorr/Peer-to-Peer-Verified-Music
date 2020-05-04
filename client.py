#!/usr/bin/env python3

import atexit
import socket
import sys

from peer import Peer

class Client:

    def __init__(self, cli):
        self.connections = {}
        self.cli = cli
        self.log = cli.log_window

        # Make sure the connection list gets stored to disk
        atexit.register(lambda: Peer.dump_to_disk(self.connections.values()))

    # Check if connection is already added and add or remove connection
    def peer_manipulate(self, peer, method):

        if (method == 'remove' and peer not in self.connections):
            self.log.print(f'Invalid command: not connected to {peer}')

        # The peer coming in could be a temporary peer to attempt look up the real Peer
        # The real Peer will actually have the TCP connection if one is open
        # Otherwise it will indicate that it isn't connected
        peer = self.connections.get(peer, peer)

        # Make sure the connection is actually alive
        peer.ping()

        # peer.is_connected() is now REAL result of whether peer is actually connected

        if (method == 'remove'):
            peer.disconnect()
            del self.connections[peer]

        elif (method == 'add'):
            if (peer.is_connected()):
                self.log.print(f'Peer {peer} is already connected')
            else:
                # Initiate client connection and add to connections list
                peer.connect()
                self.connections[peer] = peer

        self.cli.update_connected_peers(self.connections.values())

    def handle_commands(self, command):

        if (command in ['help', '?', '/?', 'h']):
            self.log.print('Available commands:')

            self.log.print('  peer add host:port')
            self.log.print('  peer remove host:port')

            self.log.print('  track list')
            self.log.print('  track get hash|name')
            return

        elif (command == 'exit' or command == 'quit'):
            self.log.print('Exiting...')

            # Do some work to notify neighboring nodes that you're going down?

            sys.exit()

        tokens = command.split()
        if (len(tokens) == 0):
            return

        if (tokens[0] == 'peer'):
            if (len(tokens) < 3 or tokens[1] not in ['add', 'remove']):
                self.log.print('usage: peer add|remove [host]:[port]')

            else:
                host, port = tokens[2].split(':')
                peer = Peer(host, port, log=self.log)
                self.peer_manipulate(peer, tokens[1])

        elif (tokens[0] == 'track'):
            if (len(tokens) < 2 or tokens[1] not in ['list', 'get'] or (tokens[1] == 'get' and len(tokens) < 3)):
                self.log.print('Usage:')
                self.log.print('  track list')
                self.log.print('  track get hash|name')

            elif (tokens[1] == 'list'):

                # TODO: Ask servers for any updates?
                # TODO: Push new file list
                pass

            elif (tokens[1] == 'get'):

                track_name_or_id = tokens[3]
                self.log.print(track_name_or_id)

                # TODO: Look at which server has this and start a download

        else:
            self.log.print('Invalid command. Type "help" for available commands')
