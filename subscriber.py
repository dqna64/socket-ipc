import socket
from constants import PORT
import sys

HOST = 'localhost'  # The remote host (replace with the server's hostname or IP address)
abort = False

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print("Connected to the publisher.")
    while True:
        try:
            data = s.recv(1024)
        except KeyboardInterrupt:
            sys.exit()

        if not data or data.decode().lower() == "please unsubscribe" or abort:
            print("Publisher has closed the connection.")
            break
        print('Received', repr(data.decode()))
        