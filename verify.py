#!/usr/bin/env python3

import pprint
import sys

import acoustid as aid

import constant

def verify():

    path = f'{constant.FILE_PREFIX}/c.mp3'

    duration, fingerprint = aid.fingerprint_file(path)

    print(f'File:        {path}')
    print(f'Duration:    {duration} s')
    print(f'Fingerprint: {repr(fingerprint[:16])}...')
    print()

    print('Manual fingerprint matches:')
    print('-----------------------------')
    json_resp = aid.lookup(constant.API_KEY, fingerprint, duration)
    matches = aid.parse_lookup_result(json_resp)
    print_matches(matches)

    print('Auto fingerprint matches:')
    print('-----------------------------')
    print_matches(aid.match(constant.API_KEY, path))

def print_matches(match_result, limit=3):

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
