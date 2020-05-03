#!/usr/bin/env python3

from client import Client
import os
import socket
import sys
import threading

class Server:
    def __init__(self, port):
        self.host = '0.0.0.0' # Listen on all interfaces
        self.port = port
        self.nodes = {}

    def start(self):

        # Create and init socket object
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        print(f'Listening on port {self.port}...')

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        while True:
            # Establish connection with client.
            self.sock.listen()
            conn, addr = self.sock.accept()
            self.nodes[addr] = conn
            thread = ConnectionThread(addr, conn)
            thread.start()

class ConnectionThread(threading.Thread):
    def __init__(self, addr, conn):
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        print(f'Got connection from {self.addr}')
        print('enter a command: ')

    def run(self):

        # self.conn.settimeout(15)

        while True:

            try:
                request_str = self.conn.recv(4096).decode("utf-8")
            except socket.timeout:
                self.conn.close()
                print(f'Connection at {self.addr} closed')
                break
            except Exception as e:
                print(f'Could not read from client socket. Closing connection at {self.addr}...')
                self.conn.close()
                break

# Check if connection is already added and add or remove connection
def peer_manipulate(host, port, method):

    already_connected = connections.get((host, port), None)

    # Check if connections list is accurate
    if (already_connected != None): # We already have a connection to their server
        try:
            already_connected.send('test')
        except:
            already_connected = None
            print('Not connected prior to command')

    # already_connected is now REAL result of whether peer is actually connected

    if (method == 'remove' and already_connected != None):
        already_connected.close()
        del connections[(host, port)]
        print(f'removed connection from {host}:{port}')

    elif (method == 'add' and already_connected == None):
        if (method == 'add'):
            # Create a new client and add to connections list
            client = Client(host, int(port))
            connections[(host, port)] = client

def get_connected_peers():
    peers = connections.keys()
    for peer in peers:
        host, port = peer
        print(f'{host}:{port}')

if __name__ == '__main__':

    # Check if port number is specified
    if len(sys.argv) < 2:
        print('usage: p2p_verified [port]')
        sys.exit()

    # Start a server object to handle receiving connections/requests
    server = Server(int(sys.argv[1]))
    server.start()

    connections = {}

    while(True):
        command = input('Enter a command: ')

        if (command == 'help'):
            print('Available commands:')

            print('peer add [host]:[port]')
            print('peer remove [host]:[port]')

            print('track list')
            print('track get [host] [port]')
            continue

        elif (command == 'exit' or command == 'quit'):
            print('Exiting...')

            # Do some work to notify neighboring nodes that you're going down?

            sys.exit()
        #end if

        tokens = command.split()
        if (tokens[0] == 'peer'):
            if (len(tokens) < 3 or (tokens[1] != 'add' and tokens[1] != 'remove')):
                print('usage: peer add|remove [host]:[port]')

            else:
                host, port = tokens[2].split(':')
                peer_manipulate(host, port, tokens[1])

        elif (tokens[0] == 'track'):
            # TODO
            print('todo')
        else:
            print('Invalid command. Type "help" for available commands')

        print('connected peers: ')
        get_connected_peers()





