import logging

class MutableString:
    """
    Since python does not support mutable string by language default,
    I implement this MutableString class to store a mutable string (using list as the backend)
    """
    def __init__(self, string = ""):
        self.string_ = list(string)

    def append(self, string):
        self.string_.extend(list(string))

    def __str__(self):
        return ''.join(self.string_)

    def __len__(self):
        return len(self.string_)

    def __getitem__(self, index):
        return self.string_[index]

    def __setitem__(self, index, value):
        if isinstance(value, str) and len(value) == 1:
            self.string_[index] = value
        else:
            raise ValueError("Value must be a single character string.")

    def __iadd__(self, other):
        if isinstance(other, str):
            self.append(other)
        else:
            raise ValueError("You can only append strings.")
        return self

    def __contains__(self, item):
        return item in self.string_

    def __eq__(self, other):
        if isinstance(other, str):
            return ''.join(self.string_) == other
        elif isinstance(other, MutableString):
            return self.string_ == other.string_
        return False
    
    def assign(self, value):
        if isinstance(value, str):
            self.string_ = list(value)
        elif isinstance(value, MutableString):
            self.string_ = value.string_
        else:
            raise ValueError("Assigned value must be a string or another MutableString.")

class SCRMessage:
    """
    This class implements a customized application level protocol: SCR protocol
    (SCR is for Simple Chatting Room)
    Currently this protocol is a minimal one : the header only contains the size of the message
    And it's used for preventing TCP packets concatenation
    """
    def __init__(self, content):
        self.size_ = len(content)
        self.content_ = content

    def pack(self):
        """
        Pack the message by adding a length header followed by the content.
        Returns the packd message (length:content).
        """
        return f"{self.size_}:{self.content_}"
    
    def write(message, write):
        """
        Write the message using the provided write function.
        It will do SCRMessage packing and encoding
        """
        write(SCRMessage(message).pack().encode('utf-8'))

    def read(buffer, read):
        """
        Read a message using the provided read function. 
        And it uses the provided buffer to store some redundant message parts
        (Due to TCP streaming feature, and due to non-blocking network programming,
        we may receive a part of the next message, and we don't want to lose it
        for the next turn, therefore we have to store it in a reusable buffer)

        This function reads the size of the message first, and then the content.
        This prevents TCP packets concatenation.

        Args:
        read (function): A function that returns the next chunk of data from the socket.
        Non-blocking read function supported.

        Returns:
        str: The content of the message.
        """
        
        logging.debug(f"[SCRMessage::read] The input buffer is {buffer}")

        # Step 1: Read the size header (which ends with a colon ":")
        while ':' not in buffer:
            try:
                chunk = read()  # read one chunk
                if not chunk:
                    return ""
                buffer += chunk.decode('utf-8')
                logging.debug(f"[SCRMessage::read] chunk is {chunk}, buffer is {buffer}")
            except BlockingIOError:
                logging.debug("[SCRMessage::read] BlockingIOError")
                return ""
        
        logging.debug(f"[SCRMessage::read] After receiving colon, buffer is {buffer}")

        size_str, remainder = str(buffer).split(":", 1)
        message_size = int(size_str) + len(size_str) + 1

        # Step 2: Read the message content based on the size
        while len(buffer) < message_size:
            try:
                chunk = read()
                if not chunk:
                    raise ValueError("Insufficient data received, expected more content.")
                buffer += chunk.decode('utf-8')
            except BlockingIOError:
                return ""

        logging.debug(f"[SCRMessage::read] before slicing, buffer is {buffer}")
        logging.debug(f"[SCRMessage::read] message_size is {message_size}")

        content = str(buffer)[:message_size]
        _, content = content.split(':', 1)
        buffer.assign(str(buffer)[message_size:])

        logging.debug(f"[SCRMessage::read] After slicing, buffer is {buffer}")

        return content