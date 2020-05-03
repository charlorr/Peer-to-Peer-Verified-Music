#!/usr/bin/env python3

import os
import socket
import sys

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        # Initialize a TCP client socket using SOCK_STREAM
        self.tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Establish connection to TCP server and exchange data
        self.tcp_client.connect((self.host, self.port))

        print(f'Connected to {host}:{port} by client')

    def send(self, data):

        self.tcp_client.sendall(data.encode())

        # Read data from the TCP server and close the connection

        received = self.tcp_client.recv(1024)
        print(f'Received: {received.decode()}')

# Example usage:
#     client = Client(sys.argv[1], int(sys.argv[2]))
#     client.send()