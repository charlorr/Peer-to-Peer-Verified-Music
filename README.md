# Peer-to-Peer-Verified-Music #
Peer-to-Peer file sharing platform that uses Acoustic Fingerprinting to verify the content of music files

## Installation

For easy setup, run
```
./setup.sh
```

Python 3.6+ is required.

## Running the program

To start the program, run
```
python3 ./cli.py PORT
```
The folder used as the source of local content for a node started this way is the default: `./content/`

Alternately, for a custom path to the folder that is used as the source of local content, run
```
python3 ./cli.py PORT CONTENT_PATH
```

The following configuration is suggested to test sharing the files between two directories:
```
python3 ./cli.py 9090
python3 ./cli.py 9091 content-2
```
Note that in the node hosted at `localhost:9091`, the content folder is `./content-2/`

Note: if lines do not border boxes in UI as pictured in `Report.pdf`, run the following command in terminal before re-running:
```
export NCURSES_NO_UTF8_ACS=1
```

## UI & Startup Tour

**Available Tracks:**
The top-left box shows the tracks available on the network within the content folders of all connected nodes. Tracks located in the local folder are in green.

**Peers:**
The top-right box shows the added peer nodes. If the current node has established a successful connection, it is green. Disconnected nodes are in red. All of these peers are saved to `config.json`, which will attempt to connect to all of these peers automatically on startup.

**Status:**
The bottom box shows the status of the node, including output detailing recently executed commands and commands executed on it by peers.

On startup, in addition to attempting to connect to peers in `config.json`, all files available for download in each node's content folder on the network are listed in the **Available Tracks** window. Each track's file contents is hashed using acoustic fingerprinting. The hashes are searched for matches in the acoustic fingerprint database [Acoustid](https://acoustid.org/). If a match is found to a song in the database, the track is named in the format
`[hash] Track Title -- Artist Name`. The format `[hash] Track hash -- Unknown` is used if a match is not found.

A complete description of the expected behavior and design of Peer-to-Peer Verified Music is available in the last section of `Report.pdf`.

## Commands

`help`: Lists available commands

`exit`: Closes all connections with node and exits

`peer add HOST:PORT`: Adds node hosted at `host:port` to connections that will be saved in `config.json`. If a connection is failed, the `host:port` will be shown in the **Peers** window in red.

`peer remove HOST:PORT`: Removes node hosted at `host:port` from connections

`track list`: Updates list of all tracks available for download on file sharing network and updates **Available Tracks** window. Local files are shown in green. As on startup, the tracks are verified by comparing their acoustic fingerprints to database.

`track get HASH`: Downloads a file to node's content folder. The desired file must be identified by its shortened hash, which is shown at the beginning of each file listing in the **Available Tracks** window.
