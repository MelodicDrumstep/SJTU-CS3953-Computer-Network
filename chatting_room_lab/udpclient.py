import socket
import threading
import sys
import fcntl
import os
import select
import logging
import struct
import uuid

logging.basicConfig(level=logging.INFO)

sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
from protocol import SCRMessage, MutableString

class UDPClient:
    """
    The UDPClient class for simple chatting room communication.
    Once it's launched, the user can send messages to the broadcast address,
    and also listen to messages from the broadcast address.
    """
    def __init__(self, broadcast_ip='224.0.0.1', broadcast_port=12345):
        self.broadcast_ip_ = broadcast_ip
        self.broadcast_port_ = broadcast_port
        self.recv_buffer_ = MutableString()
        self.client_id = str(uuid.uuid4()) # This uuid will be used to filter out the message that the client itself sent
        logging.debug("[UDPClient::__init__] Finish construction")

    def start(self):
        logging.debug("[UDPClient::start] Beginning of start")
        
        # Create a UDP socket for sending messages
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        send_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Enable broadcasting

        # Create a UDP socket for receiving messages
        recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        recv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reusing the address
        recv_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)  # Set TTL for multicast
        recv_socket.bind(('', self.broadcast_port_))  # Bind to the specified multicast port
        recv_socket.setblocking(False)

        # Join the multicast group
        group = socket.inet_aton(self.broadcast_ip_)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        recv_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        stdin_fd = sys.stdin.fileno()       
        old_flags = fcntl.fcntl(stdin_fd, fcntl.F_GETFL)
        fcntl.fcntl(stdin_fd, fcntl.F_SETFL, old_flags | os.O_NONBLOCK)

        def write(message):
            send_socket.sendto(message, (self.broadcast_ip_, self.broadcast_port_))

        def read():
            return recv_socket.recv(1024)

        try:
            while True:
                # IO-multiplexing. Using select here because it performs better when the 
                # number of file descriptor is small
                readable, _, _ = select.select([recv_socket, stdin_fd], [], [], 0.1)

                for sock in readable:
                    if sock == recv_socket:
                        # Message from the multicast address
                        logging.debug("[UDPClient::start] recv socket readable")
                        try:
                            message = SCRMessage.read(self.recv_buffer_, read)
                            if message:
                                if message.startswith("["):
                                    client_id, message_body = message.split("] ", 1)
                                    client_id = client_id[1:]  
                                    if client_id != self.client_id:
                                        print(f"{message_body}") 
                        except BlockingIOError:
                            pass  # No data available

                    elif sock == stdin_fd:
                        # Message from the terminal
                        try:
                            message = sys.stdin.read()
                            if message:
                                message = message.strip()
                                if message.lower() == 'exit':
                                    print("Exiting...")
                                    return
                                message = f"[{self.client_id}] {message}"
                                SCRMessage.write(message, write)
                                logging.debug(f"[UDPClient::start] write message {message}")
                        except IOError:
                            pass 

        except KeyboardInterrupt:
            print("\nCaught KeyboardInterrupt. Closing sockets...")
        finally:
            send_socket.close()
            recv_socket.close()
            print("Sockets closed.")

if __name__ == "__main__":
    UDPClient().start()