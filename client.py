#!/usr/bin/env python3

import atexit
import socket
import sys

import constant
from peer import Peer

class Client:

    def __init__(self, cli):
        self.connections = {}
        self.cli = cli
        self.log = cli.log_window

        self.all_tracks = {}
        self.all_tracks_sh = {} # Short hash
        self.local_tracks = {}

        # Make sure the connection list gets stored to disk
        atexit.register(lambda: Peer.dump_to_disk(self.connections.values()))

    def add_tracks(self, track_list):
        '''
        Add tracks to the list of available tracks.
        '''

        for track in track_list:

            short_hash = track.short_hash()

            # Watch for hash collisions but don't chain for now
            if (short_hash in self.all_tracks_sh):
                if (self.all_tracks_sh[short_hash].hash != track.hash):
                    self.log.print('HASH COLLISION!!!')

            # Don't overwrite the local track info that we have
            if (
                track.local
                or
                track.hash not in self.all_tracks
                or
                not self.all_tracks[track.hash].local
            ):
                self.all_tracks[track.hash] = track
                self.all_tracks_sh[short_hash] = track

            if (track.local):
                self.local_tracks[track.hash] = track

    def peer_manipulate(self, peer, method):
        '''
        Add or remove peers.
        '''

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

    def do_track_list_update(self):
        '''
        Query all peers for an updated track list.
        '''

        self.log.print('Updating track list...')

        for peer in self.connections.values():

            if (peer.is_connected()):
                tracks = peer.request_track_list()
                self.add_tracks(tracks)

        self.log.print('Done')
        self.cli.update_available_tracks(self.all_tracks.values())

    def handle_commands(self, command):

        if (command in ['help', '?', '/?', 'h']):
            self.log.print('\nAvailable commands:')

            self.log.print('  peer add HOST:PORT')
            self.log.print('  peer remove HOST:PORT')

            self.log.print('  track list')
            self.log.print('  track get SHORT_HASH')
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
                self.log.print('usage: peer add|remove HOST:PORT')

            else:
                host, port = tokens[2].split(':')
                peer = Peer(host, port, log=self.log)
                self.peer_manipulate(peer, tokens[1])

        elif (tokens[0] == 'track'):
            if (len(tokens) < 2 or tokens[1] not in ['list', 'get'] or (tokens[1] == 'get' and len(tokens) < 3)):
                self.log.print('Usage:')
                self.log.print('  track list')
                self.log.print('  track get SHORT_HASH')

            elif (tokens[1] == 'list'):

                self.do_track_list_update()

            elif (tokens[1] == 'get'):

                short_hash = tokens[2]

                if (len(short_hash) != constant.HASH_LEN):
                    self.log.print(f'SHORT_HASH should be the {constant.HASH_LEN} character prefix to the left of the track')
                    return

                track = self.all_tracks_sh[short_hash]
                track.download(log=self.log)

        else:
            self.log.print('Invalid command. Type "help" for available commands')
