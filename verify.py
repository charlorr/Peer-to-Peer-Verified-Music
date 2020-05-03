#!/usr/bin/env python3

import hashlib
import sys

import acoustid as aid

import constant

def verify():

    path = f'{constant.FILE_PREFIX}/c.mp3'

    duration, fingerprint = aid.fingerprint_file(path)

    print(f'File:        {path}')
    print(f'Duration:    {duration} s')
    print(f'Hash:        {hash_file(path)}')
    print(f'Fingerprint: {repr(fingerprint[:32])}...') # Substring since this is super long
    print()

    print('Manual fingerprint matches:')
    print('-----------------------------')
    json_resp = aid.lookup(constant.API_KEY, fingerprint, duration)
    matches = aid.parse_lookup_result(json_resp)
    print_matches(matches)

    print('Auto fingerprint matches:')
    print('-----------------------------')
    print_matches(aid.match(constant.API_KEY, path))

def hash_file(path):
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

def print_matches(match_result, limit=3):
    '''
    Display acoustid match results.
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

if (__name__ == '__main__'):
    verify()
