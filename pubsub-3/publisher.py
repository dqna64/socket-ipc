import socket
import threading
from typing import Any, Dict
from constants import DEBUG, PORT

class Subscription:
    def __init__(self, addr, conn: socket.socket):
        self.conn = conn
        self.addr = addr
        self.thread = threading.Thread(target=self.handle_subscription)
    
    def __enter__(self):
        '''
        `.__enter__()` and `.__exit__()` are implemented for the context manager
        protocol, making this class a 'context manager object'. 
        
        ```
        with Subscriber(addr, conn) as subscriber:
            ## do stuff with subcriber
            pass
        ```

        `.__enter__()` is called by the `with` statement to enter the runtime
        context.

        The return value of `.__enter__` is put into the `as subscriber`
        variable.
        '''
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        '''
        `.__exit__()` is called when execution leaves the context of the `with`
        block.
        '''
        DEBUG and print(f"Waiting for thread {self.thread.name} handling subscriber {self.addr} to finish...")
        self.thread.join()
        DEBUG and print(f"Thread {self.thread.name} handling subscriber {self.addr} finished.")

    def handle_subscription(self):
        with self.conn:
            try:
                while not stop_accepting_subs.is_set():
                    data = self.conn.recv(1024)
                    if not data:
                        DEBUG and print(f"None data received by subscriber {self.addr}, terminating subscription.")
                        break
            except Exception as e:
                print(f"Error with subscriber {self.addr} receiving data, terminating subscription")
                raise e

            ## `self.conn` will automatically close when execution leaves the
            # `with self.conn` block.

    @staticmethod
    def create_subscription(addr, conn: socket.socket):
        return Subscription(addr, conn)

    def request_unsubscribe(self):
        try:
            self.conn.sendall(b"exit")
        except Exception as e:
            print(f"Error sending to {self.conn.getpeername()}:")
            raise e

class Subscriptions:
    def __init__(self):
        self.subscriptions: Dict[Any, Subscription]  = dict()

    def accept_subscriber(self, addr, conn: socket.socket):
        '''
        Make sure to run this method in a thread.
        '''
        with Subscription.create_subscription(addr, conn) as subscription:
            ## This runtime context loops undefinitely until the subscriber
            # terminates its socket connection.
            self.add_subcription(addr, subscription)

        self.remove_subscription(addr)

    def add_subcription(self, addr, subscription: Subscription):
        with subs_lock:
            self.subscriptions[addr] = subscription

    def remove_subscription(self, addr):
        with subs_lock:
            del self.subscriptions[addr]

    def broadcast(self, message: str):
        with subs_lock:
            for subscription in self.subscriptions.values():
                try:
                    subscription.conn.sendall(message.encode())
                    print(f"Published to {subscription.conn.getpeername()}: {message}")
                except Exception as e:
                    print(f"Error sending to {subscription.conn.getpeername()}: {e}")


    def request_unsubscribe_all(self):
        '''
        Ask all subscribers to unsubscribe.
        Does not guarantee that they will actually subscribe.
        '''
        stop_accepting_subs.set()
        for subscription in self.subscriptions.values():
            subscription.request_unsubscribe()



HOST = ''  # Symbolic name meaning all available interfaces

subscribers = Subscriptions() 
subs_lock: threading.Lock = threading.Lock()
stop_accepting_subs: threading.Event = threading.Event()

def accept_subscribers(server_socket: socket.socket):
    while not stop_accepting_subs.is_set():
        try:
            # Q: why settimout
            server_socket.settimeout(1)
            conn, addr = server_socket.accept()
            thread = threading.Thread(target=subscribers.accept_subscriber, args=(addr, conn))
            thread.start()
            # sub_threads.append(thread)
        except socket.timeout:
            continue
        except socket.error as e:
            print(e)
            if stop_accepting_subs.is_set():
                print(f'Terminate accept_subscribers')
                break
            print(f'Error with accepting a new subscriber socket {conn}: {e}')

def publish_messages():
    while True:
        message = input("Enter message to publish: ")
        if message.lower() == "exit":
            subscribers.request_unsubscribe_all()
            # shutdown()
            break
        subscribers.broadcast(message)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print("Publisher started. Waiting for subscribers...")
    
    accept_subscribers_thread = threading.Thread(target=accept_subscribers, args=(server_socket,))
    accept_subscribers_thread.start()
    publish_messages()
    
    accept_subscribers_thread.join()
    DEBUG and print(f"Thread {accept_subscribers_thread.name} handling accepting new subscribers has finished.")

