#!/usr/bin/env python3

import base64
import json
import os.path
import socket
import sys
import threading
import traceback

import constant
from peer import Peer

class Server:
    def __init__(self, cli, port, tracks, local_tracks):
        self.host = '0.0.0.0' # Listen on all interfaces
        self.port = port
        self.cli = cli
        self.tracks = tracks
        self.local_tracks = local_tracks
        self.nodes = {}

    def start(self):

        # Create and init socket object
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.cli.log(f'Starting server on port {self.port}... ')

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

        self.cli.log(f'Done')

    def run(self):
        while True:
            # Establish connection with client.
            self.sock.listen()
            conn, addr = self.sock.accept()
            self.nodes[addr] = conn
            thread = ClientThread(self.cli, addr, conn, self.tracks, self.local_tracks)
            thread.start()

class ClientThread(threading.Thread):
    def __init__(self, cli, addr, conn, tracks, local_tracks):
        threading.Thread.__init__(self)
        self.cli = cli
        self.conn = conn
        self.tracks = tracks
        self.local_tracks = local_tracks
        self.peer = Peer(cli, *addr)

        self.cli.log(f'Got connection from {self.peer}')

    def read_file(self, path):
        '''
        Read the entire file into memory and encode to
        base64.
        '''

        with open(os.path.join(constant.FILE_PREFIX, path), 'rb') as f:
            data = f.read()

        return base64.b64encode(data).decode()

    def run(self):

        while True:
            try:
                data = self.conn.recv(constant.MAX_SOCK_READ).decode()

                if (len(data) == 0):
                    self.conn.close()
                    self.cli.log(f'Connection to {self.peer} closed')
                    break

                self.cli.log(data)

                str_resp = None

                if (data == 'ping'):
                    str_resp = 'pong'

                else:
                    str_resp = self.handle_json_req(data)
                    if (str_resp is None):
                        continue

                self.cli.log(str_resp)

                self.conn.sendall(str_resp.encode())

            except socket.timeout:
                self.conn.close()
                self.cli.log(f'Connection to {self.peer} closed')
                break
            except Exception:
                self.cli.log(traceback.format_exc())
                continue

    def handle_json_req(self, data):

        try:
            json_req = json.loads(data)
            action = json_req['action']
        except:
            self.cli.log('JSON parse failed')
            return None

        if (action == 'get_track_list'):

            json_resp = {
                'action': 'put_track_list',
                'tracks': [track.to_dict() for track in self.local_tracks.values()]
            }

        elif (action == 'get_track'):

            track_hash = json_req['hash']

            # Ignore requests for tracks we don't know
            if (track_hash not in self.local_tracks):
                return None

            track = self.local_tracks[track_hash]

            # Ignore requests for tracks we don't have
            if (not track.local):
                return None

            file_data = self.read_file(track.path)

            json_resp = {
                'action': 'put_track',
                'fileData': file_data
            }

        return json.dumps(json_resp)
