import socket
import threading
import pytest
import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from protocol import SCRMessage, MutableString
from user import Client 

# Simple test server
class Server:
    def __init__(self, host='127.0.0.1', port=12345):
        self.host = host
        self.port = port
        self.received_messages = []
        self.recv_buffer = MutableString()

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.running = True

        def handle_client(client_socket):
            def read():
                return client_socket.recv(1024)
            def write(message):
                client_socket.send(message) 
            while self.running:
                try:
                    message = SCRMessage.read(self.recv_buffer, read, debug_mode = True)
                    if message == "":
                        time.sleep(2)
                    self.received_messages.append(message)
                    print(f"[Server::handle_client] received message is {message}")
                    SCRMessage.write("Get U " + message, write)
                except:
                    exc_type, exc_value, _ = sys.exc_info()
                    print("[Server::handle_client] Exception errors")
                    print(f"Exception type: {exc_type.__name__}")
                    print(f"Exception value: {exc_value}")
                    break
            client_socket.close()

        while self.running:
            client_socket, _ = self.server_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket,)).start()

    def stop(self):
        self.running = False
        self.server_socket.close()
        self.server_thread.join()

    def get_received_messages(self):
        return self.received_messages

# Tests
def test_client_connection():
    # Setup
    print("[test_client_connection] Init")

    server = Server()   

    print("[test_client_connection] Construct the server")    

    server_thread = threading.Thread(target=server.start)
    server_thread.start()

    print("[test_client_connection] Starting the server thread")

    username = "test_user"
    client = Client(username, SERVER_HOST = '127.0.0.1', SERVER_PORT = 12345, debug_mode = True)

    # Run the client in a separate thread
    client_thread = threading.Thread(target=client.start)
    client_thread.start()

    # Allow some time for the client to connect and interact
    time.sleep(2)

    # Check if the server received the username
    received_messages = server.get_received_messages()
    assert len(received_messages) > 0

    # Cleanup
    client_thread.join(timeout=5)
