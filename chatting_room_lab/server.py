import socket
import os
import sys
import select
import multiprocessing
import logging

logging.basicConfig(level=logging.DEBUG)
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
from protocol import SCRMessage, MutableString
from PCHashMap import ProcessSafeHashMap

class TCPServer:
    """
    The TCPServer class for simple chatting room communication.
    """
    def __init__(self, host_ip = "127.0.0.1", host_port = 12345, num_workers = 1):
        self.host_ip_ = host_ip
        self.host_port_ = host_port
        self.num_workers_ = num_workers
        self.client_name2socket_ = ProcessSafeHashMap()
        self.client_fd2name_ = ProcessSafeHashMap()

    def onConnection(self, server_socket, epoll):
        """Handle incoming connection requests."""
        client_socket, client_address = server_socket.accept()
        logging.debug(f"[TCPServer::onConnection] New connection from {client_address}")
        
        # Set the socket to non-blocking mode, preventing client attack
        client_socket.setblocking(False)
        # Use epoll for IO multiplexing
        # Register the client socket for read events
        epoll.register(client_socket.fileno(), select.EPOLLIN | select.EPOLLHUP | select.EPOLLERR | select.EPOLLET)
        logging.debug(f"[TCPServer::onConnection] fileno() is {client_socket.fileno()}")
        try:
            username = self.receive_username(client_socket)
            if username:
                self.client_name2socket_.put(username, client_socket)
                self.client_fd2name_.put(client_socket.fileno(), username)

                logging.debug(f"[TCPServer::onConnection] Received username: {username} from {client_address}")
                logging.debug(f"[TCPServer::onConnection] insert pair {client_socket.fileno()},{username} into client_fd2name")
            else:
                logging.debug(f"[TCPServer::onConnection] Failed to receive username from {client_address}")
        except Exception as e:
            logging.error(f"[TCPServer::onConnection] Error receiving username from {client_address}: {e}")
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
        
    def removeClient(self, epoll, fileno):
        epoll.unregister(fileno)
        client_name = self.client_fd2name_.get(fileno)
        self.client_name2socket_.get(client_name).close()
        self.client_name2socket_.remove(client_name)
        self.client_fd2name_.remove(fileno)

    @staticmethod
    def worker(queue, client_name2socket, client_fd2name):
        recv_buffer = MutableString()
        while True:
            if queue.empty():
                continue
            fileno = queue.get()
            client_name = client_fd2name.get(fileno)
            client_socket = client_name2socket.get(client_name)
            if client_socket is not None:
                def read():
                    return client_socket.recv(1024)
                while True:
                    message = SCRMessage.read(recv_buffer, read)
                    if message == "":
                        break
                    logging.debug(f"[worker] received message is {message}")

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
                        target_name, message_content = parse_message(message)
                    except ValueError:
                        SCRMessage.write("Format error. The format should be \'To XXX:MMMM\'", write_fallback)
                        continue 

                    logging.debug(f"[TCPServer::worker] target_name is {target_name}, msg_content is {message_content}")
                    
                    target_socket = client_name2socket.get(target_name)

                    logging.debug(f"[TCPServer::worker] sender_name is {client_name}, the IP used for searching is {client_socket.getpeername()}")

                    if target_socket is not None:
                        SCRMessage.write(message_content + " From " + client_name, write)
                    else:
                        SCRMessage.write("The target user cannot be reached.", write_fallback)

    def start(self):
        """Start the server and handle incoming connections and messages."""
        # Create the server socket
        queue = multiprocessing.Queue()
        for i in range(self.num_workers_):
            p = multiprocessing.Process(target=TCPServer.worker, args=(queue, 
                self.client_name2socket_, self.client_fd2name_), name=f"Process-{i}")
            p.start()

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host_ip_, self.host_port_))
        server_socket.listen()
        server_socket.setblocking(False)

        # Set up epoll for I/O multiplexing
        epoll = select.epoll()
        epoll.register(server_socket.fileno(), select.EPOLLIN)
        logging.debug(f"[TCPServer::start] TCPServer listening on {self.host_ip_}:{self.host_port_}")

        # Main event loop (Reactor)
        while True:
            events = epoll.poll()
            for fileno, event in events:
                if fileno == server_socket.fileno():
                    # Connection event
                    self.onConnection(server_socket, epoll)
                # NOTICE: when the client close the connection
                # Both EPOLLIN and EPOLLHUP will be triggerred
                # Therefore we have to handle EPOLLHUP / EPOLLERR first
                elif event & (select.EPOLLHUP | select.EPOLLERR):
                    logging.debug("[TCPServer::start] Connection closed by peer or error occurred")
                    self.removeClient(epoll, fileno)
                elif event & select.EPOLLIN:
                    try:
                        queue.put(fileno)
                    except OSError as e:
                        logging.error(f"Error creating socket from file descriptor: {e}")

if __name__ == "__main__":
    server = TCPServer('127.0.0.1', 12345)
    server.start()
