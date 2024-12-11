import socket
import threading
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from protocol import SCRMessage, MutableString
from user import Client 

# Simple test server
class TestServer:
    def __init__(self, host='127.0.0.1', port=12345):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.running = True
        self.received_messages = []
        self.recv_buffer = MutableString()

    def start(self):
        def handle_client(client_socket):
            def read():
                return client_socket.recv(1024).decode('utf-8')
            while self.running:
                try:
                    message = SCRMessage.read(self.recv_buffer, read, debug_mode = True)
                    self.received_messages.append(message)
                except:
                    break
            client_socket.close()

        def run_server():
            while self.running:
                client_socket, _ = self.server_socket.accept()
                threading.Thread(target=handle_client, args=(client_socket,)).start()

        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.start()

    def stop(self):
        self.running = False
        self.server_socket.close()
        self.server_thread.join()

    def get_received_messages(self):
        return self.received_messages

# Pytest fixtures
@pytest.fixture
def test_server():
    server = TestServer()
    server.start()
    yield server
    server.stop()

# Tests
def test_client_connection(test_server):
    # Setup
    username = "test_user"
    client = Client(username, SERVER_HOST='127.0.0.1', SERVER_PORT=12345)

    # Run the client in a separate thread
    client_thread = threading.Thread(target=client.start)
    client_thread.start()

    # Allow some time for the client to connect and interact
    import time
    time.sleep(2)

    # Check if the server received the username
    received_messages = test_server.get_received_messages()
    print(f"[test_client_connection] received_messages is {received_messages}")
    assert len(received_messages) > 0
    assert SCRMessage(username).serialize() in received_messages

    # Cleanup
    client_thread.join(timeout=5)
