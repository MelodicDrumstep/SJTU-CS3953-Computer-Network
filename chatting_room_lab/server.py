import socket
import os
import sys
import select
import multiprocessing

class Server:
    def __init__(self, host_ip, host_port, max_workers=4):
        self.host_ip_ = host_ip
        self.host_port_ = host_port
        self.max_workers = max_workers
        self.client_sockets = {}
        self.client_names2sockets = {}

    def onConnection(self, server_socket, epoll):
        """Handle incoming connection requests."""
        client_socket, client_address = server_socket.accept()
        print(f"New connection from {client_address}")
        
        # Set the socket to non-blocking mode
        client_socket.setblocking(False)
        
        # Register the client socket for read events
        epoll.register(client_socket.fileno(), select.EPOLLIN)
        
        # Store the client socket and address
        self.client_sockets[client_socket.fileno()] = client_socket
        print(f"Registered client {client_address}")

        try:
            username = self.receive_username(client_socket)
            if username:
                self.client_names[client_socket.fileno()] = username
                print(f"Received username: {username} from {client_address}")
            else:
                print(f"Failed to receive username from {client_address}")
        except Exception as e:
            print(f"Error receiving username from {client_address}: {e}")
            self.removeClient(client_socket)  

    def receive_username(self, client_socket):
        """Helper method to receive the username sent by the client."""
        username = ""
        while True:
            try:
                # Receive data from the client (non-blocking)
                data = client_socket.recv(1024).decode('utf-8')
                if data:
                    username += data
                    if "\n" in username:
                        username = username.strip()
                        return username
                else:
                    return None
            except BlockingIOError:
                continue


    def onMessage(self, client_socket):
        """Handle incoming message from a client."""
        try:
            message_data = client_socket.recv(1024).decode('utf-8')
            if message_data:
                # Process the message
                message = Message(message_data)
                dest_name = message.dest_name_
                content = message.content_

                # Look up destination client IP
                dest_ip = self.resolution_table_[dest_name]
                if dest_ip:
                    # Find the socket of the destination client
                    for client in self.client_sockets.values():
                        if client.getpeername()[0] == dest_ip:
                            # Send the formatted message to the destination client
                            forwarded_message = f"{content} : From {self.client_names[client_socket.fileno()]}"
                            client.send(forwarded_message.encode('utf-8'))
                            break
                    else:
                        client_socket.send("Destination client not found.".encode('utf-8'))
                else:
                    client_socket.send("Client not found in resolution table.".encode('utf-8'))
            else:
                # Client disconnected
                self.removeClient(client_socket)
        except Exception as e:
            print(f"Error in message handling: {e}")
            self.removeClient(client_socket)

    def removeClient(self, client_socket):
        """Remove client from the list and close socket."""
        print(f"Removing client {self.client_names[client_socket.fileno()]}")
        epoll.unregister(client_socket.fileno())
        client_socket.close()
        del self.client_sockets[client_socket.fileno()]
        del self.client_names[client_socket.fileno()]

    def start(self):
        """Start the server and handle incoming connections and messages."""
        # Create the server socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host_ip_, self.host_port_))
        server_socket.listen()
        server_socket.setblocking(False)

        # Set up epoll for I/O multiplexing
        epoll = select.epoll()
        epoll.register(server_socket.fileno(), select.EPOLLIN)
        print(f"Server listening on {self.host_ip_}:{self.host_port_}")

        # Create worker processes
        for _ in range(self.max_workers):
            worker_process = multiprocessing.Process(target=self.worker, args=(epoll,))
            worker_process.daemon = True
            worker_process.start()

        # Main event loop (Reactor)
        while True:
            events = epoll.poll()
            for fileno, event in events:
                if fileno == server_socket.fileno():
                    # Connection event
                    self.onConnection(server_socket, epoll)
                elif event & select.EPOLLIN:
                    # Readable event (client message)
                    client_socket = self.client_sockets[fileno]
                    self.onMessage(client_socket)

    def worker(self, epoll):
        """Worker process that processes messages."""
        while True:
            events = epoll.poll()
            for fileno, event in events:
                if event & select.EPOLLIN:
                    client_socket = self.client_sockets[fileno]
                    self.onMessage(client_socket)

if __name__ == "__main__":
    server = Server('10.0.0.4', 8080)
    server.start()
