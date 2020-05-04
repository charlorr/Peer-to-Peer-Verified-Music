#!/usr/bin/env python3

import socket
import sys

class Client:
    def __init__(self, cli):
        self.connections = {}
        self.log = cli.log_window

    # Check if connection is already added and add or remove connection
    def peer_manipulate(self, host, port, method):

        already_connected = self.connections.get((host, port), None)

        if (already_connected == None and method == 'remove'):
            self.log.print(f'Invalid command: not connected to {host}:{port}')

        # Check if connections list is accurate
        if (already_connected != None): # We already have a connection to their server
            try:
                already_connected.send('ping isitchristmas.com')
            except:
                already_connected = None
                self.log.print('Updated connected nodes list')

        # already_connected is now REAL result of whether peer is actually connected

        if (method == 'remove' and already_connected != None):
            already_connected.tcp_conn.close()
            del self.connections[(host, port)]
            self.log.print(f'removed connection to {host}:{port}')

        elif (method == 'add' and already_connected == None):
            if (method == 'add'):
                # Create a new client connection and add to connections list
                conn = Connection(self.log, host, int(port))
                if (conn.connected):
                    self.connections[(host, port)] = conn

    def print_connected_peers(self):
        peers = self.connections.keys()
        for peer in peers:
            host, port = peer
            self.log.print(f'{host}:{port}')

    def handle_commands(self, command):
        if (command == 'help'):
            self.log.print('Available commands:')

            self.log.print('peer add [host]:[port]')
            self.log.print('peer remove [host]:[port]')

            self.log.print('track list')
            self.log.print('track get [host] [port]')
            return

        elif (command == 'exit' or command == 'quit'):
            self.log.print('Exiting...')

            # Do some work to notify neighboring nodes that you're going down?

            sys.exit()

        tokens = command.split()
        if (tokens[0] == 'peer'):
            if (len(tokens) < 3 or tokens[1] not in ['add', 'remove']):
                cli.log.print('usage: peer add|remove [host]:[port]')

            else:
                host, port = tokens[2].split(':')
                self.peer_manipulate(host, port, tokens[1])

        elif (tokens[0] == 'track'):
            # TODO
            self.log.print('todo')
        else:
            self.log.print('Invalid command. Type "help" for available commands')

        # self.log.print('connected peers: ')

class Connection:
    def __init__(self, log, host, port):
        self.log = log
        self.host = host
        self.port = port
        self.connected = True

        # Initialize a TCP client socket using SOCK_STREAM
        self.tcp_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # Establish connection to TCP server and exchange data
            self.tcp_conn.connect((self.host, self.port))
        except ConnectionRefusedError:
            self.log.print(f'Unable to connect to {host}:{port}')
            self.connected = False
            return None # This is what __init__ should return?

        self.log.print(f'Client connected to {host}:{port}')

    def send(self, data):

        self.tcp_conn.sendall(data.encode())

        # Read data from the TCP server and close the connection
        received = self.tcp_conn.recv(1024)
        self.log.print(f'Received: {received.decode()}')
