#!/usr/bin/env python3

import atexit
import os
import socket
import sys

import constant
from peer import Peer
from track import Track

class Client:

    def __init__(self, cli):
        self.connections = {}
        self.cli = cli

        self.all_tracks = {}
        self.all_tracks_sh = {} # Short hash
        self.local_tracks = {}

        self.should_update = True

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
                    self.cli.log('HASH COLLISION!!!')

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

        self.update_tracks()

    def add_local_tracks(self):
        '''
        Scan the content folder and add local tracks.

        This only scans the top level folder. No subdirectories.
        '''

        # Create a bogus track to fix the issue
        # where the screen clears itself
        # This trigger the delayed import of CLI
        t = Track('', '', 0, '', b'', '')

        self.cli.log(f"Checking directory '{constant.FILE_PREFIX}' for media... ")

        # Only check 1 level deep
        tracks = []
        files = os.listdir(constant.FILE_PREFIX)
        for file in files:
            if (os.path.isfile(os.path.join(constant.FILE_PREFIX, file))):
                self.cli.log(f"Processing '{file}'...")
                tracks.append(Track.from_file(file))

        self.add_tracks(tracks)

        self.cli.log('Done')

    def do_track_list_update(self):
        '''
        Query all peers for an updated track list.
        '''

        for peer in self.connections.values():

            if (peer.is_connected()):
                tracks = peer.request_track_list()

                if (tracks is None):
                    continue

                self.add_tracks(tracks)

        self.update_tracks()

    def restore_peers(self):
        '''
        Restore and connect to each peer.
        '''

        # Load peers
        self.cli.log('Loading saved peers from disk... ')
        peers = Peer.load_from_disk(cli=self.cli)

        # Try to reconnect to each peer
        for peer in peers:
            self.peer_manipulate(peer, 'add')

        self.cli.log('Done')

    def peer_manipulate(self, peer, method):
        '''
        Add or remove peers.
        '''

        if (method == 'remove' and peer not in self.connections):
            self.cli.log(f'Invalid command: not connected to {peer}')

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
                self.cli.log(f'Peer {peer} is already connected')
            else:
                # Initiate client connection and add to connections list
                success = peer.connect()
                self.connections[peer] = peer

                if (success):

                    # Get the new tracks
                    tracks = peer.request_track_list()
                    if (tracks is not None):
                        self.add_tracks(tracks)

        self.update_peers()

    def update(self):
        self.update_tracks()
        self.update_peers()

    def update_tracks(self):
        if (self.should_update):
            self.cli.update_available_tracks(self.all_tracks.values())

    def update_peers(self):
        if (self.should_update):
            self.cli.update_connected_peers(self.connections.values())

    def handle_commands(self, command):

        if (command in ['help', '?', '/?', 'h']):
            self.cli.log('\nAvailable commands:')

            self.cli.log('  peer add HOST:PORT')
            self.cli.log('  peer remove HOST:PORT')

            self.cli.log('  track list')
            self.cli.log('  track get SHORT_HASH')
            return

        elif (command == 'exit' or command == 'quit'):
            self.cli.log('Exiting...')

            # Do some work to notify neighboring nodes that you're going down?

            sys.exit()

        tokens = command.split()
        if (len(tokens) == 0):
            return

        if (tokens[0] == 'peer'):
            if (len(tokens) < 3 or tokens[1] not in ['add', 'remove']):
                self.cli.log('usage: peer add|remove HOST:PORT')

            else:
                host, port = tokens[2].split(':')
                peer = Peer(self.cli, host, port)
                self.peer_manipulate(peer, tokens[1])

        elif (tokens[0] == 'track'):
            if (len(tokens) < 2 or tokens[1] not in ['list', 'get'] or (tokens[1] == 'get' and len(tokens) < 3)):
                self.cli.log('Usage:')
                self.cli.log('  track list')
                self.cli.log('  track get SHORT_HASH')

            elif (tokens[1] == 'list'):

                self.do_track_list_update()

            elif (tokens[1] == 'get'):

                short_hash = tokens[2]

                if (len(short_hash) != constant.HASH_LEN):
                    self.cli.log(f'SHORT_HASH should be the {constant.HASH_LEN} character prefix to the left of the track')
                    return

                track = self.all_tracks_sh[short_hash]
                track.download(self.cli)

                self.update_tracks()

        else:
            self.cli.log('Invalid command. Type "help" for available commands')
