import json
from typing import List

class Peer:

    @staticmethod
    def save_to_disk(peers):
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
    def read_from_disk():
        '''
        Generate a List of Peers from the config file on disk.
        '''

        with open('config.json', 'r') as f:
            json_dict = json.load(f)

        peers = []
        for peer_info in json_dict['peers']:
            peers.append(Peer(peer_info['host'], peer_info['port']))

        return peers

    def __init__(self, host, port):

        self.host = host
        self.port = int(port)

    def to_json(self):
        '''
        JSON representation of a peer.
        '''

        return {
            'host': self.host,
            'port': self.port
        }

    def __str__(self):

        return f'{self.host} [{self.port}]'

if (__name__ == '__main__'):

    peers = []
    peers.append(Peer('127.0.0.1', 8080))
    peers.append(Peer('127.0.0.1', 8081))
    peers.append(Peer('127.0.0.1', 8082))

    for peer in peers:
        print(peer)

    Peer.save_to_disk(peers)

    print()

    peers2 = Peer.read_from_disk()

    for peer in peers2:
        print(peer)
