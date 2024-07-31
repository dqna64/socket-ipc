import socket
import threading
from typing import List, Callable

## TODO: create a Subscriber class to encapsulate socket and thread?

HOST = ''  # Symbolic name meaning all available interfaces
PORT = 50007  # Arbitrary non-privileged port

sub_sockets: List[socket.socket] = []
sub_threads: List[threading.Thread] = []
subs_lock: threading.Lock = threading.Lock()
stop_accepting_subs: threading.Event = threading.Event()

def handle_subscriber(conn: socket.socket, addr):
    with conn:
        print(f'Subscriber connected: {addr}')
        with subs_lock:
            sub_sockets.append(conn)
        try:
            while not stop_accepting_subs.is_set():
                data = conn.recv(1024)
                if not data:
                    break
        except Exception as e:
            print(f'Error with subscriber {addr}: {e}')
            raise e
        finally:
            print(f'Subscriber disconnected: {addr}')
            with subs_lock:
                sub_sockets.remove(conn)
            conn.close()

def accept_subscribers(server_socket: socket):
    while not stop_accepting_subs.is_set():
        try:
            # Q: why settimout
            server_socket.settimeout(1)
            conn, addr = server_socket.accept()
            thread = threading.Thread(target=handle_subscriber, args=(conn, addr))
            thread.start()
            sub_threads.append(thread)
        except socket.timeout:
            continue
        except socket.error as e:
            if stop_accepting_subs.is_set():
                break
            print(f'Error with accepting a new subscriber socket {conn}: {e}')

    # Clean up all subscriber threads
    for thread in sub_threads:
        thread.join()
        sub_threads.remove(thread)

def shutdown():
    stop_accepting_subs.set()
    with subs_lock:
        for subscriber in sub_sockets:
            try:
                subscriber.sendall(b"exit")
                # subscriber.close()
                # ^To close a socket, send the "exit" message to it.
            except Exception as e:
                print(f"Error sending to {subscriber.getpeername()}:")

def publish_messages(shutdown: Callable[[], None]):
    while True:
        message = input("Enter message to publish: ")
        if message.lower() == "exit":
            shutdown()
            break
        with subs_lock:
            for subscriber in sub_sockets:
                try:
                    subscriber.sendall(message.encode())
                    print(f"Published to {subscriber.getpeername()}: {message}")
                except Exception as e:
                    print(f"Error sending to {subscriber.getpeername()}: {e}")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print("Publisher started. Waiting for subscribers...")
    
    accept_subs_thread = threading.Thread(target=accept_subscribers, args=(server_socket,))
    accept_subs_thread.start()
    publish_messages(shutdown)
    
    # Close the server socket to unblock accept() call
    server_socket.close()
    accept_subs_thread.join()
