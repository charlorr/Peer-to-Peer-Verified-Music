#!/usr/bin/env python3

import json

with open('secrets.json', 'r') as f:
    secrets = json.load(f)

API_KEY = secrets["API_KEY"]
