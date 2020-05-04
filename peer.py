#!/usr/bin/env python3

import json
import socket
from typing import List

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
    def load_from_disk():
        '''
        Generate a List of Peers from the config file on disk.
        '''

        with open('config.json', 'r') as f:
            json_dict = json.load(f)

        peers = []
        for peer_info in json_dict['peers']:
            peers.append(Peer(peer_info['host'], peer_info['port']))

        return peers

    @staticmethod
    def from_list(tuples):
        '''
        Take list of tuple(host, port) and turn it into a list of Peers
        '''

        peers = []
        for host, port in tuples:
            peers.append(Peer(host, port))

        return peers

    def __init__(self, host, port, connected=False, log=None):

        self.host = host
        self.port = int(port)
        self.connected = connected
        self.tcp_conn = None
        self.log_window = log

    def log(self, msg):

        if (self.log_window):
            self.log_window.print(msg)

    def set_log(self, log):

        self.log_window = log

    def connect(self):

        # Initialize a TCP client socket using SOCK_STREAM
        if (self.tcp_conn is None):
            self.tcp_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # Establish connection to TCP server and exchange data
            self.tcp_conn.connect(self.to_tuple())
            self.connected = True
            self.log(f'Connected to {self}')
        except ConnectionRefusedError:
            self.connected = False
            self.log(f'Connection to {self} failed')
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
            self.log(f'Connection to {self} died')

        return self.connected

    def send(self, data, is_str=True):
        '''
        Send data.
        '''

        if (is_str):
            data = data.encode()

        try:
            self.tcp_conn.sendall(data)
            self.log(f'Sent {len(data)} bytes to {self}')
        except:
            self.log('Failed to send data')
            return False

        return True

    def recv(self, timeout=3, size=1024, to_str=True):
        '''
        Read from the socket. Returns `None` if response does
        not arrive before `timeout`.
        '''

        self.tcp_conn.settimeout(timeout)

        try:
            resp = self.tcp_conn.recv(1024)
        except socket.timeout:
            return None

        if (to_str):
            resp = resp.decode()

        return resp

    def disconnect(self):

        if (self.tcp_conn):
            self.tcp_conn.close()

        self.connected = False

        self.log(f'Disconnected from {self}')

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
