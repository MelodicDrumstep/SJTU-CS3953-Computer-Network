import socket
import threading
import sys
import fcntl
import os
import select
import logging
import time

logging.basicConfig(level=logging.INFO)

sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
from protocol import SCRMessage, MutableString

class TCPClient:
    """
    The TCPClient class for simple chatting room communication.
    Once it's launched, the user should type in the user name first,
    then the user can send message in the format of 'To XX:MMMM',
    e.g. To h1:Hello World!
    """
    def __init__(self, username, server_ip = '127.0.0.1', server_port = 12345):
        self.username_ = username
        self.server_ip_ = server_ip
        self.server_port_ = server_port
        self.recv_buffer_ = MutableString()
        logging.debug("[TCPClient::__init__] Finish construction")

    def start(self):
        logging.debug("[TCPClient::start] Beginning of start")
        
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.server_ip_, self.server_port_))

        logging.debug("[TCPClient::start] Successfully calling connect")
        
        client_socket.setblocking(False)
        # Set the client socket to be non-blocking
        # In this way, if the server send a huge message to the client
        # And the server is down after sending parts of it
        # the client can detect it and doesn't have to wait forever

        stdin_fd = sys.stdin.fileno()       
        old_flags = fcntl.fcntl(stdin_fd, fcntl.F_GETFL)
        fcntl.fcntl(stdin_fd, fcntl.F_SETFL, old_flags | os.O_NONBLOCK)
        # The file descriptor to get the input from the terminal
        # Also set to non-blocking, otherwise the terminal readable event will block
        # the other events

        def write(message):
            client_socket.send(message)
        def read():
            return client_socket.recv(1024)

        # send the user name to the server
        # the server will store it in a hashmap
        SCRMessage.write(self.username_, write)
        logging.debug(f"Sent username: {self.username_}")

        try:
            while True:
                # IO-multiplexing. Using select here because it performs better when the 
                # number of file descriptor is small
                # For the server, we should use epoll for performance reasons
                readable, _, _ = select.select([client_socket, stdin_fd], [], [], 0.1)

                for sock in readable:
                    if sock == client_socket:
                        # Message from the server
                        logging.debug("[TCPClient::Start] client socket readable")
                        while True:
                            message = SCRMessage.read(self.recv_buffer_, read)
                            if message == "":
                                break
                            else:
                                print(f"{message}")

                    elif sock == stdin_fd:
                        # Message from the terminal
                        try:
                            message = sys.stdin.read()
                            if message:
                                message = message.strip()
                                if message.lower() == 'exit':
                                    SCRMessage.write("EXIT", write)
                                    time.sleep(1)
                                    print("Exiting...")
                                    client_socket.close()
                                    return
                                SCRMessage.write(message, write)
                                logging.debug(f"[TCPClient::start] write message {message}")
                        except IOError:
                            pass 

        except KeyboardInterrupt:
            print("\nCaught KeyboardInterrupt. Closing socket...")
        finally:
            SCRMessage.write("EXIT", write)
            time.sleep(1)
            client_socket.close()
            print("Socket closed.")

if __name__ == "__main__":
    username = input("Enter your username: ") 
    TCPClient(username = username, server_ip = "10.0.0.4", server_port = 12345).start()
