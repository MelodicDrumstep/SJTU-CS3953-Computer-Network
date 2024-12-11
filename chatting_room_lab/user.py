import socket
import threading
import sys
import fcntl
import os
import select

from protocol import SCRMessage, MutableString

class Client:
    def __init__(self, username, SERVER_HOST='10.0.0.4', SERVER_PORT=8080, debug_mode = False):
        self.username = username
        self.SERVER_HOST = SERVER_HOST
        self.SERVER_PORT = SERVER_PORT
        self.recv_buffer_ = MutableString()
        self.debug_mode_ = debug_mode

    def start(self):
        if self.debug_mode_:
            print("[Client::start] Beginning of start")
        
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.SERVER_HOST, self.SERVER_PORT))

        if self.debug_mode_:
            print("[Client::start] Successfully calling connect")
        
        client_socket.setblocking(False)
        # Set the client socket to be non-blocking

        stdin_fd = sys.stdin.fileno()
        old_flags = fcntl.fcntl(stdin_fd, fcntl.F_GETFL)
        fcntl.fcntl(stdin_fd, fcntl.F_SETFL, old_flags | os.O_NONBLOCK)
        # the file descriptor to get the input from the terminal
        # Also set to non-blocking

        def write(message):
            client_socket.send(message)
        SCRMessage.write(self.username, write)
        print(f"Sent username: {self.username}")

        def read():
            return client_socket.recv(1024).decode('utf-8')

        try:
            while True:
                # IO-multiplexing. Using select because it performs better when the 
                # number of file descriptor is small
                readable, _, _ = select.select([client_socket, stdin_fd], [], [], 0.1)

                for sock in readable:
                    if sock == client_socket:
                        while True:
                            message = SCRMessage.read(self.recv_buffer_, read)
                            if message:
                                print(f"{message}")
                            else:
                                break

                    elif sock == stdin_fd:
                        try:
                            message = sys.stdin.read()
                            if message:
                                message = message.strip()
                                if message.lower() == 'exit':
                                    client_socket.close()
                                    print("Exiting...")
                                    return
                                client_socket.send(message.encode('utf-8'))
                        except IOError:
                            pass 
        except KeyboardInterrupt:
            print("\nCaught KeyboardInterrupt. Closing socket...")
        finally:
            client_socket.close()
            print("Socket closed.")

if __name__ == "__main__":
    username = input("Enter your username: ")  # User enters their username
    Client(username=username).start()
