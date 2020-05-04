#!/bin/bash

export NCURSES_NO_UTF8_ACS=1
sudo apt install -y ffmpeg libchromaprint-dev

pip3 install -r requirements.txt

python ./cli.py 9090
