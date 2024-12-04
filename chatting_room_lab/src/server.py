import socket
import threading
import sys
import os

sys.path.append(os.path.abspath('src'))
sys.path.append(os.path.abspath('utils'))

from message import Message
from resolution_table import ResolutionTable

class Server:
    def __init__(host_ip, host_port):
        self.host_ip_ = host_ip
        self.host_port_ = host_port
        self.resolution_table_ = ResolutionTable()
        self.client_ = {}

    def register(dest_name, dest_ip)
        self.resolution_table_.register(dest_name, dest_ip)

    def handleClient(client_socket, client_address, resolution_table):
        """Function to handle each client connection."""
        while True:
            try:
                # Receive message from client
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break

                dest_name = message.dest_name_
                dest_ip = resolution_table[dest_name]
                content = message.content_

                
                # Send the message to the destination client
                if dest_client in clients:
                    clients[dest_client].send(f"{msg} From {client_address[0]}".encode('utf-8'))
                else:
                    client_socket.send("Destination client not found.".encode('utf-8'))
            except Exception as e:
                print(f"Error: {e}")
                break

        # Remove the client from the dictionary
        clients.pop(client_address[0], None)
        client_socket.close()

    def start():
        """Function to start the server and listen for incoming connections."""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Server listening on {HOST}:{PORT}")

        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address}")

            # Store the client connection in the dictionary
            clients[client_address[0]] = client_socket

            # Start a new thread to handle the client
            client_thread = threading.Thread(target=handleClient, args=(client_socket, client_address, self.resolution_table_))
            client_thread.start()

if __name__ == "__main__":
    Server server('10.0.0.4', 8080)
    server.start()