import hashlib
import json
import os.path

import acoustid as aid

import constant

class Track:

    @staticmethod
    def from_file(file_name: str):
        '''
        Construct a Track object from a file.
        '''

        path = os.path.join(constant.FILE_PREFIX, file_name)

        duration, fingerprint = aid.fingerprint_file(path)
        file_hash = hash_file(path)

        # Use AcoustID
        json_resp = aid.lookup(constant.API_KEY, fingerprint, duration)
        matches = aid.parse_lookup_result(json_resp)

        try:
            # Ignore score and recording_id
            _, _, title, artist = next(matches)
        except StopIteration:
            title = 'Track ' + file_hash[:constant.HASH_LEN]
            artist = 'Unknown'

        return Track(title, artist, duration, file_hash, fingerprint, path=file_name, local=True)

    @staticmethod
    def from_json(json_str: str, peer):
        '''
        Construct a Track object from JSON.
        '''

        json_dict = json.loads(json_str)

        return from_dict(json_dict, peer)

    @staticmethod
    def from_dict(json_dict: dict, peer):
        '''
        Construct a Track object from a JSON dictionary.
        '''

        duration = json_dict['duration']
        fingerprint = json_dict['fingerprint']
        file_hash = json_dict['hash']
        title = json_dict['title']
        artist = json_dict['artist']

        return Track(title, artist, duration, file_hash, fingerprint, peer=peer, local=False)

    def __init__(self,
        title: str,
        artist: str,
        duration_s: float,
        file_hash: str,
        fingerprint: bytes,
        path: str = None,
        peer = None,
        local: bool = False
    ):

        self.title = title
        self.artist = artist
        self.duration = duration_s
        self.hash = file_hash
        self.fingerprint = fingerprint
        self.path = path
        self.peer = peer
        self.local = local

        print(peer)

    def download(self, log):
        '''
        Request the track from its peer.
        '''

        if (self.local):
            log.print(f'Track {self.short_hash()} is already local')
            return

        if (self.peer is None):
            log.print('Download failed: Track has no peer')
            return

        success = self.peer.request_track(self)
        return success

    def to_dict(self):

        json_dict = {
            'title': self.title,
            'artist': self.artist,
            'duration': self.duration,
            'hash': self.hash,
            'fingerprint': '' # self.fingerprint # Trouble sending this because it's bytes
        }

        return json_dict

    def to_json(self):

        return json.dumps(self.to_dict())

    def short_hash(self):

        return self.hash[:constant.HASH_LEN]

    def __str__(self):

        return f'[{self.short_hash()}] {self.title} -- {self.artist}'

def hash_file(path: str) -> str:
    '''
    Calculate and return the SHA-256 hash of the given file.
    '''

    SIZE = 65536
    hasher = hashlib.sha256()

    with open(path, 'rb') as f:

        segment = f.read(SIZE)
        while len(segment) > 0:
            hasher.update(segment)
            segment = f.read(SIZE)

    res = hasher.hexdigest()
    return res

def print_acoustid_matches(match_result, limit=3):
    '''
    Dump acoustid match results.
    '''

    i = 0
    for score, recording_id, title, artist in match_result:
        print(f'ID:      {recording_id}')
        print(f'Title:   {title}')
        print(f'Artist:  {artist}')
        print()

        i += 1
        if (i >= limit):
            break