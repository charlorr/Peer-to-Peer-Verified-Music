#!/usr/bin/env python3

import constant
import acoustid
import sys


def verify():

    path = 'content/c.mp3'

    for score, recording_id, title, artist in acoustid.match(constant.API_KEY, path):
        x = 4
        print(f"hello")
        print(f"The song title is {title}")


if __name__ == "__main__":
    # execute only if run as a script
    verify()


