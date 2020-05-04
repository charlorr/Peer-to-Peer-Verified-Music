#!/usr/bin/env python3

import json

with open('secrets.json', 'r') as f:
    secrets = json.load(f)

PROG_NAME = 'Peer-to-Peer Verified Music'
API_KEY = secrets["API_KEY"]
FILE_PREFIX = 'content'
MAX_CHARS = 100
HASH_LEN = 4
