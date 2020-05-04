#!/usr/bin/env python3

import socket
import sys
import threading

class Server:
    def __init__(self, cli, port):
        self.host = '0.0.0.0' # Listen on all interfaces
        self.port = port
        self.log = cli.log_window
        self.nodes = {}

    def start(self):

        # Create and init socket object
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.log.print(f'Listening on port {self.port}...')

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        while True:
            # Establish connection with client.
            self.sock.listen()
            conn, addr = self.sock.accept()
            self.nodes[addr] = conn
            thread = ClientThread(self.log, addr, conn)
            thread.start()

class ClientThread(threading.Thread):
    def __init__(self, log, addr, conn):
        threading.Thread.__init__(self)
        self.log = log
        self.conn = conn
        self.addr = addr

        self.log.print(f'Got connection from {self.addr}')

    def run(self):

        while True:
            try:
                data = self.conn.recv(4096).decode("utf-8")
                data = f'Thanks for sending \"{data}\"'
                self.conn.sendall(data.encode())
            except socket.timeout:
                self.conn.close()
                self.log.print(f'Connection at {self.addr} closed')
                break
            except Exception as e:
                self.log.print(f'Could not read from client socket. Closing connection at {self.addr}...')
                self.conn.close()
                break
