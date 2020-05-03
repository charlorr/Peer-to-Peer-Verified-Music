#!/usr/bin/env python3

import constant
import acoustid
import sys

class Server:
    def __init__(self, port):
        self.host = '0.0.0.0' # Listen on all interfaces
        self.port = port

    def start(self):

        # Create and init socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        print(f'Listening on port {self.port}...')

        while True:
            # Establish connection with client.
            sock.listen()
            conn, addr = sock.accept()
            thread = ClientThread(addr, conn)
            thread.start()

class ClientThread(threading.Thread):
    def __init__(self, addr, conn):
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        print(f'Got connection from {self.addr}')

    def run(self):

        self.conn.settimeout(15)

        while True:

            try:
                request_str = self.conn.recv(4096).decode("utf-8")
            except socket.timeout:
                self.conn.close()
                print(f'Connection at {self.addr} closed')
                break
            except Exception as e:
                print(f'Could not read from client socket. Closing connection at {self.addr}...')
                self.conn.close()
                break

            # Set some defaults
            response_code = 200
            response_msg = 'OK'

            # Check if connection needs to be closed
            connection_pos = request_str.find('\r\nConnection: close')
            close_connection = (connection_pos != -1)

            method = request_str.split(' ')[0]
            if ((method != 'GET') and (method != 'HEAD')):
                response_code = 405
                response_msg = 'Method Not Allowed'
            else:
                # Get file name
                file = request_str.split(' ')[1]
                if ((file == '/') or (file == '/index.html')):
                    file = 'index.html'
                else:
                    os.path.dirname(__file__)
                    file = f'Upload{file}'
                    if not os.path.exists(file):
                        response_code = 404
                        response_msg = 'Not Found'
                    elif not os.access(file, os.R_OK):
                        response_code = 403
                        response_msg = 'Forbidden'

            if (response_code == 200):
                # Check content-type
                file_ext = file.split('.')[1]
                if (file_ext == 'html'):
                    content_type = 'text/html'
                elif (file_ext == 'png'):
                    content_type = 'image/png'
                elif (file_ext == 'jpg'):
                    content_type = 'image/jpeg'
                else:
                    content_type = 'text/plain'

                # Get the content and its length
                content_length, body = self.get_content(file)

                # Fill the response with gathered data
                response = f'HTTP/1.1 {response_code} {response_msg}\r\n'.encode()
                response += f'Content-Length: {content_length}\r\n'.encode()
                response += f'Content-Type: {content_type}\r\n'.encode()
                response += '\r\n'.encode()
                if (method == 'GET'):
                    response += body

            else:
                # Fill the response with data (for errors)
                display_msg = f'Error {response_code}: {response_msg}'

                response = f'HTTP/1.1 {response_code} {response_msg}\r\n'
                response += f'Content-Length: {len(display_msg)}\r\n'
                response += '\r\n'
                response += display_msg # response body
                response = response.encode()

            # Send response incrementally
            bytes_sent = 0
            SEND_LIMIT = 140160
            mem_view = memoryview(response)

            try:
                while bytes_sent < len(response):
                    bytes_sent += self.conn.send(bytes(mem_view[bytes_sent:(bytes_sent + SEND_LIMIT)]))
            except Exception as e:
                print(f'Could not write to client socket. Closing connection at {self.addr}...')
                self.conn.close()
                break

            if close_connection:
                self.conn.close()
                print(f'Connection at {self.addr} closed')
                break

    # Returns length then content
    def get_content(self, file):
        # Get the content length
        file_size = os.stat(file).st_size

        # Get the content body
        with open(file, 'rb') as infile:
            file_contents = infile.read()

        return (str(file_size), file_contents)

# Start example client
#!/usr/bin/env python3

import os
import socket
import sys

class Client:
    def __init__(self, host, port, filenames, methods):
        self.host = host
        self.port = port
        self.filenames = filenames
        self.methods = methods

    def send(self):
        # Initialize a TCP client socket using SOCK_STREAM
        tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Establish connection to TCP server and exchange data
        tcp_client.connect((self.host, self.port))

        for j in range(len(self.methods)):

            request = f'{self.methods[j]} {self.filenames[j]} HTTP/1.1\r\n'
            if len(self.filenames) - 1 == j:
                request += 'Connection: close\r\n'

            tcp_client.sendall(request.encode())

            # Read data from the TCP server and close the connection

            received = tcp_client.recv(1024)

            # Check response code
            i = 0
            while str(chr(received[i])) != ' ':
                i += 1
            error_occurred =  str(chr(received[i + 1])) != '2'

            if (self.methods[j] == 'GET') and not error_occurred:

                received_str = ''
                i = 0
                # Find end of response so it can be printed / searched
                while str(chr(received[i])) != '\r' or str(chr(received[i + 1])) != '\n' or str(chr(received[i + 2])) != '\r' or str(chr(received[i + 3])) != '\n':
                    received_str += str(chr(received[i]))
                    i += 1

                received_str += '\r\n\r\n'
                print(received_str)

                # Get content length
                length_index = received_str.find('Content-Length: ') + 16
                content_length = ''

                while received_str[length_index] != '\r':
                    content_length += received_str[length_index]
                    length_index += 1

                # Make sure entire message has been delivered
                request_length = len(received_str) + int(content_length)
                while request_length > len(received):
                    received += tcp_client.recv(4096)

                # Create byte array of body of response
                body = received[i + 4: len(received)]

                # Download file
                if self.filenames[j] == '/':
                    self.filenames[j] += 'index.html'
                if not os.path.exists(f'Download{self.filenames[j]}'):
                    with open(f'Download{self.filenames[j]}', 'wb') as file:
                        file.write(bytes(body))
            # Response does not include body, or it is all human-readable
            else:
                print(received.decode())

if __name__ == '__main__':

    if (len(sys.argv) < 5) or ((sys.argv[4] != 'GET') and (sys.argv[4] != 'HEAD')) or (len(sys.argv) % 2 != 1):
        print('usage: myclient.py serverIP serverPort filename command(GET or HEAD)')
        exit()

    # Parse arguments, making sure file names have leading /'s
    num_requests = int((len(sys.argv) - 3) / 2)
    filenames = []
    methods = []
    for i in range(num_requests):
        filenames.append(sys.argv[3 + (i * 2)])
        if filenames[i][0] != '/':
            filenames[i] = '/' + filenames[i]
        methods.append(sys.argv[4 + (i * 2)])

    client = Client(sys.argv[1], int(sys.argv[2]), filenames, methods)
    client.send()

