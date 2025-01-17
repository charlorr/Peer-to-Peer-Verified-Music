#!/usr/bin/env python3

import base64
import json
import os.path
import socket
from typing import List

import constant
from track import Track, hash_file

class Peer:

    @staticmethod
    def dump_to_disk(peers):
        '''
        Write the given list of peers to the config file on disk.
        '''

        peer_list = []
        for peer in peers:
            peer_list.append(peer.to_json())

        final_peers_dict = {
            'peers': peer_list
        }

        with open('config.json', 'w') as f:
            json.dump(final_peers_dict, f, indent=2)

    @staticmethod
    def load_from_disk(cli):
        '''
        Generate a List of Peers from the config file on disk.
        '''

        with open('config.json', 'r') as f:
            json_dict = json.load(f)

        peers = []
        for peer_info in json_dict['peers']:
            peers.append(Peer(cli, peer_info['host'], peer_info['port']))

        return peers

    def __init__(self, cli, host, port, connected=False):

        self.host = host
        self.port = int(port)
        self.connected = connected
        self.tcp_conn = None
        self.cli = cli

    def connect(self):

        # Initialize a TCP client socket using SOCK_STREAM
        if (self.tcp_conn is None):
            self.tcp_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # Establish connection to TCP server and exchange data
            self.tcp_conn.connect(self.to_tuple())
            self.connected = True
            self.cli.log(f'Connected to {self}')
        except ConnectionRefusedError:
            self.connected = False
            self.cli.log(f'Connection to {self} failed')
            return False

        return True

    def is_connected(self):

        return self.connected

    def ping(self):
        '''
        Check if the peer is alive.
        '''

        if (not self.connected):
            return False

        self.send('ping')
        resp = self.recv(timeout=1)

        self.connected = (resp == 'pong')

        if (not self.connected):
            self.cli.log(f'Connection to {self} died')
            self.disconnect()

        return self.connected

    def request_track_list(self):
        '''
        Fetch the list of available tracks.
        '''

        self.cli.log(f'Requesting track list for {self}...')

        self.send({'action': 'get_track_list'}, is_json=True)
        json_dict = self.recv(to_json=True)

        if (json_dict is None):
            self.cli.log('Request failed')
            return None

        tracks = []
        for track_dict in json_dict['tracks']:

            track = Track.from_dict(track_dict, self)
            self.cli.log(f"Found track '{track.title}'")

            tracks.append(track)

        return tracks

    def request_track(self, track):

        self.cli.log(f"Requesting '{track}'...")

        self.send({'action': 'get_track', 'hash': track.hash}, is_json=True)
        json_dict = self.recv(to_json=True)

        if (json_dict is None):
            self.cli.log('Request failed')
            return False

        b64_data = json_dict['fileData']

        file_name = f'{track.hash}.{track.extension}'
        file_path = os.path.join(constant.FILE_PREFIX, file_name)
        file_data = base64.b64decode(b64_data)

        with open(file_path, 'wb') as f:
            f.write(file_data)

        self.cli.log(f'Wrote {file_name}')

        final_hash = hash_file(file_path)

        if (track.hash != final_hash):
            self.cli.log('Track hashes did not match! File may have been corrupted')
        else:
            self.cli.log('File hashes match')

        # Mark the file as local
        track.local = True
        track.path = file_name

        self.cli.log('Download successful')

        return True

    def send(self, data, is_str=True, is_json=False):
        '''
        Send data.
        '''

        if (is_json):
            data = json.dumps(data)

        if (is_str or is_json):
            data = data.encode()

        try:
            self.tcp_conn.sendall(data)
            self.tcp_conn.sendall('\r\n\r\n'.encode())
            self.cli.log(f'Sent {len(data)} bytes to {self}')
        except:
            self.cli.log('Failed to send data')
            return False

        return True

    def read_into_buffer(self):
        '''
        Read bytes into a buffer until seeing \r\n\r\n.
        '''

        buffer = bytes()

        while True:
            try:
                received = self.tcp_conn.recv(constant.MAX_SOCK_READ)
                buffer += received
            except socket.timeout:
                self.cli.log('Request timed out')
                return None

            if (received is None or len(received) == 0):
                self.cli.log(f'Connection to {self} closed')
                self.disconnect()
                return None

            try:
                last_four = buffer[-4:]
                last_four = last_four.decode()

                if (last_four == '\r\n\r\n'):
                    buffer = buffer[:-4]
                    break

            except Exception as e:
                self.cli.log(e)

        self.cli.log(f'Buffered {len(buffer)} bytes')

        return buffer

    def recv(self, timeout=5, to_str=True, to_json=False):
        '''
        Read from the socket. Returns `None` if response does
        not arrive before `timeout`.
        '''

        self.tcp_conn.settimeout(timeout)

        resp = self.read_into_buffer()
        if (resp is None):
            return None

        if (to_str or to_json):
            resp = resp.decode()

        if (to_json):
            resp = json.loads(resp)

        return resp

    def disconnect(self):

        if (self.tcp_conn):
            self.tcp_conn.close()

        self.tcp_conn = None
        self.connected = False

        self.cli.log(f'Disconnected from {self}')
        self.cli.client.update_peers()

    def __eq__(self, other):

        return self.host == other.host and self.port == other.port

    def __hash__(self):

        return (self.host, self.port).__hash__()

    def __str__(self):

        return f'{self.host}:{self.port}'

    def to_tuple(self):

        return (self.host, self.port)

    def to_json(self):
        '''
        JSON representation of a peer.
        '''

        return {
            'host': self.host,
            'port': self.port
        }

if (__name__ == '__main__'):

    peers = []
    peers.append(Peer('127.0.0.1', 8080))
    peers.append(Peer('127.0.0.1', 8081))
    peers.append(Peer('127.0.0.1', 8082))

    for peer in peers:
        print(peer)

    Peer.dump_to_disk(peers)

    print()

    peers2 = Peer.load_from_disk()

    for peer in peers2:
        print(peer)
