import socket
import threading
import sys
import fcntl
import os
import select

class Client:
    def __init__(self, username, SERVER_HOST='10.0.0.4', SERVER_PORT=8080):
        self.username = username
        self.SERVER_HOST = SERVER_HOST
        self.SERVER_PORT = SERVER_PORT

    def start(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.SERVER_HOST, self.SERVER_PORT))
        
        client_socket.setblocking(False)
        # Set the client socket to be non-blocking

        stdin_fd = sys.stdin.fileno()
        old_flags = fcntl.fcntl(stdin_fd, fcntl.F_GETFL)
        fcntl.fcntl(stdin_fd, fcntl.F_SETFL, old_flags | os.O_NONBLOCK)
        # the file descriptor to get the input from the terminal
        # Also set to non-blocking

        # Send the username to the server after the connection is established
        client_socket.send(self.username.encode('utf-8'))
        print(f"Sent username: {self.username}")

        try:
            while True:
                # IO-multiplexing. Using select because it performs better when the 
                # number of file descriptor is small
                readable, _, _ = select.select([client_socket, stdin_fd], [], [], 0.1)

                for sock in readable:
                    if sock == client_socket:
                        try:
                            message = client_socket.recv(1024).decode('utf-8')
                            if message:
                                print(f"{message}")
                        except BlockingIOError:
                            pass  

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
