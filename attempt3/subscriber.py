import socket

HOST = 'localhost'  # The remote host (replace with the server's hostname or IP address)
PORT = 50007        # The same port as used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print("Connected to the publisher.")
    while True:
        data = s.recv(1024)
        if not data or data.decode().lower() == "exit":
            print("Publisher has closed the connection.")
            break
        print('Received', repr(data.decode()))
