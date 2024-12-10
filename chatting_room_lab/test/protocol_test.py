import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from protocol import SCRMessage, MutableString

def create_read_function(data):
    """Create a read function that returns chunks of data from a given string."""
    data_iter = iter(data)  # Convert the string to an iterator of chars
    def read():
        # Return the next chunk (up to a size of 2)
        chunk = ''.join([next(data_iter, '') for _ in range(2)])
        return chunk.encode('utf-8') if chunk else b''
    return read

def test_protocol():
    # Create the read function with a test string
    test_str_list = [
                    "Hello, world! This is a test message.",
                    "ABCBCBC",
                    "Hi jack",
                    "大家好啊",
                    "进击の巨人"
                ]
    
    test_str_together = ""
    for str in test_str_list:
        test_str_together += SCRMessage(str).serialize()

    read_function = create_read_function(test_str_together)

    # Initialize the buffer
    buffer = MutableString()

    # Simulating receiving a message
    for i in range(5):
        content = SCRMessage.deserialize(buffer, read_function, True)
        print(f"Received message: {content}")
        print(f"After one turn, buffer becomes {buffer}")