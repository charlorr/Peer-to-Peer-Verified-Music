# Peer-to-Peer-Verified-Music
Peer-to-Peer file sharing system that verifies the content of the files matches its title

Installation:
  pip3 install pyacoustid

Steps:

Generate chromaprint from music file received (using pyacoustid)

Send chromaprint as compressed post request to get musicbrainz

...
1. Detect unverified music on the network
2. Identify music
3. Name music file said name

1. If any files are in content folder, send msg to all other nodes that it exists
- Keep list of all nodes for this reason?

1. User commands can include get-file, list-files, update-file-list?

- If multiple servers have a file, we can use them to

6. Each node needs to be able to:
- Serve files
- Request files
7. And keeps track of:
- How many nodes and at what address?
- Which nodes have which files

Questions:
- How do we handle disconnection??

