'''
Scans a range of ports to find the first available port.
An available port (ie 'closed' port) is a port that is not being used
by an application or service to actively listen for connections.
So it is available to be used for such a purpose. Doing so will
make the port 'open'.
'''

from contextlib import closing
import socket

# Determines what port is lended to a debugging session for Unix socket
# communications between the server and gdb subprocess.
# Increments from MIN_SOCKET_PORT to MAX_SOCKET_PORT.
MIN_SOCKET_PORT = 11000
PORT_RANGE = 100

def find_new_port():
    for _ in range(PORT_RANGE):
        curr_socket_port = MIN_SOCKET_PORT + (find_new_port.curr_socket_port_offset%PORT_RANGE)
        find_new_port.curr_socket_port_offset += 1
        if check_port_valid_and_available(curr_socket_port):
            return curr_socket_port
    raise RuntimeError("Could not find valid and available port")

# Determines what port is lended to a debugging session for Unix socket
# communications between the server and gdb subprocess.
# Increments from MIN_SOCKET_PORT to MAX_SOCKET_PORT.
find_new_port.curr_socket_port_offset = MIN_SOCKET_PORT

def check_port_valid_and_available(port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        # Timeout after 2 seconds if the port cannot be
        # connected, maybe because the port is not open.
        sock.settimeout(2)
        for _ in range(2):
            try:
                print(f'check port {port}')
                # result = sock.connect_ex(("127.0.0.1", port))
                result = sock.connect_ex(("127.0.0.1", port))
                print(f'result {result}')
                return result != 0
            except ConnectionRefusedError as e:
                raise e
            except TimeoutError:
                return False

def open_port(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', port))
    sock.listen()
    print(f'listening to port {port}')
    return sock

if __name__ == '__main__':
    # If I don't return the sockets from the open_port function
    # and store here, it closes automatically. wtf
    open_socks = []

    # Open ports 11000-11004
    for port in range(11000, 11005):
        open_socks.append(open_port(port))

    # Find a valid and available port. 11000-11004 are taken.
    found_port = find_new_port()
    print(f'found available port {found_port}') # 11005