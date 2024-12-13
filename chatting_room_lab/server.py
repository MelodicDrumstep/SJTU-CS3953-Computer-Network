import socket
import os
import sys
import select
import multiprocessing

sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
from protocol import SCRMessage, MutableString
from PCHashMap import ProcessSafeHashMap

class TCPServer:
    def __init__(self, host_ip = "127.0.0.1", host_port = 12345, num_workers = 1, debug_mode = False):
        self.host_ip_ = host_ip
        self.host_port_ = host_port
        self.num_workers_ = num_workers
        self.client_name2socket_ = ProcessSafeHashMap()
        self.client_ip2name_ = ProcessSafeHashMap()
        self.client_sockets = []
        self.debug_mode_ = debug_mode

    def onConnection(self, server_socket, epoll):
        """Handle incoming connection requests."""
        client_socket, client_address = server_socket.accept()
        print(f"New connection from {client_address}")
        
        # Set the socket to non-blocking mode
        client_socket.setblocking(False)
        
        # Register the client socket for read events
        epoll.register(client_socket.fileno(), select.EPOLLIN | select.EPOLLET)
        if self.debug_mode_:
            print(f"[TCPServer::onConnection] fileno() is {client_socket.fileno()}")

        try:
            os.fstat(client_socket.fileno())
            print("[Serever::onConnection] YES")
        except OSError:
            print("[Serever::onConnection] NONONO")

        try:
            username = self.receive_username(client_socket)
            if username:
                self.client_sockets.append(client_socket)
                self.client_name2socket_.put(username, client_socket)
                self.client_ip2name_.put(client_socket.getpeername(), username)
                print(f"Received username: {username} from {client_address}")
                print(f"insert pair {client_socket.getpeername()},{username} into client_ip2name")
            else:
                print(f"Failed to receive username from {client_address}")
        except Exception as e:
            print(f"Error receiving username from {client_address}: {e}")
            # self.removeClient(client_socket)  

    def receive_username(self, client_socket):
        """Helper method to receive the username sent by the client."""
        try:
            def read():
                return client_socket.recv(1024)
            # Receive data from the client (non-blocking)
            return SCRMessage.read(MutableString(), read)
        except BlockingIOError:
            return None

    # def removeClient(self, client_socket):
    #     """Remove client from the list and close socket."""
    #     print(f"Removing client {self.client_names[client_socket.fileno()]}")
    #     epoll.unregister(client_socket.fileno())
    #     client_socket.close()
    #     del self.client_sockets[client_socket.fileno()]
    #     del self.client_names[client_socket.fileno()]

    @staticmethod
    def worker(queue, client_name2socket, client_ip2name, debug_mode = False):
        recv_buffer = MutableString()
        while True:
            if queue.empty():
                continue
            client_socket = queue.get()
            if client_socket is not None:
                def read():
                    return client_socket.recv(1024)
                while True:
                    message = SCRMessage.read(recv_buffer, read, debug_mode = True)
                    if message == "":
                        break
                    print(f"[worker] received message is {message}")

                    def parse_message(message):
                        if not message.startswith("To "):
                            raise ValueError("Message must start with 'To '")
                        
                        parts = message.split(":", 1)  
                        if len(parts) < 2:
                            raise ValueError("Message must contain ':' after the recipient name")

                        to_part = parts[0]
                        to_parts = to_part.split(" ", 1) 
                        if len(to_parts) < 2:
                            raise ValueError("Message must contain a recipient name after 'To '")
                        
                        name = to_parts[1]
                        msg = parts[1]
                        
                        return name, msg
                    
                    def write(message):
                        target_socket.send(message) 
                    def write_fallback(message):
                        client_socket.send(message) 
                    try:
                        name, message_content = parse_message(message)
                    except ValueError:
                        SCRMessage.write("Format error. The format should be \'To XXX: MMMM\'", write_fallback)
                        continue 

                    if debug_mode:
                        print(f"[TCPServer::worker] name is {name}, msg_content is {message_content}")
                    
                    target_socket = client_name2socket.get(name)
                    sender_name = client_ip2name.get(client_socket.getpeername())

                    print(f"[TCPServer::worker] sender_name is {sender_name}, the IP used for searching is {client_socket.getpeername()}")

                    if target_socket is not None:
                        SCRMessage.write(message_content + " From " + sender_name, write)
                    else:
                        SCRMessage.write("The target user cannot be reached.", write_fallback)


    def start(self):
        """Start the server and handle incoming connections and messages."""
        # Create the server socket
        queue = multiprocessing.Queue()
        for i in range(self.num_workers_):
            p = multiprocessing.Process(target=TCPServer.worker, args=(queue, 
                self.client_name2socket_, self.client_ip2name_, self.debug_mode_), name=f"Process-{i}")
            p.start()

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host_ip_, self.host_port_))
        server_socket.listen()
        server_socket.setblocking(False)

        # Set up epoll for I/O multiplexing
        epoll = select.epoll()
        epoll.register(server_socket.fileno(), select.EPOLLIN)
        print(f"TCPServer listening on {self.host_ip_}:{self.host_port_}")

        # Main event loop (Reactor)
        while True:
            events = epoll.poll()
            for fileno, event in events:
                if fileno == server_socket.fileno():
                    # Connection event
                    self.onConnection(server_socket, epoll)
                elif event & select.EPOLLIN:
                    # Readable event (client message)
                    # if self.debug_mode_:
                    #     print(f"[TCPServer::start] fileno is {fileno}")

                    try:
                        os.fstat(fileno)
                        print("YES")
                    except OSError:
                        print("NONONO")

                    try:
                        client_socket = socket.fromfd(fileno, socket.AF_INET, socket.SOCK_STREAM)
                        queue.put(client_socket)
                    except OSError as e:
                        print(f"Error creating socket from file descriptor: {e}")

if __name__ == "__main__":
    server = TCPServer('127.0.0.1', 12345, debug_mode = True)
    server.start()
