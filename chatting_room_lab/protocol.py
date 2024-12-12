class MutableString:
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
    SCR is for simple chatting room
    """
    def __init__(self, content):
        self.content_ = content
        self.size_ = len(content)

    def serialize(self):
        """
        Serialize the message by adding a length header followed by the content.
        Returns the serialized message (length:content).
        """
        return f"{self.size_}:{self.content_}"
    
    def write(message, write, debug_mode = False):
        write(SCRMessage(message).serialize().encode('utf-8'))

    def read(buffer, read, debug_mode = False):
        """
        read a message from the provided read function.
        This function reads the size of the message first, and then the content.
        
        The `read` function should return data in chunks, and should be callable.
        It will be repeatedly called until the entire message is read.

        Args:
        read (function): A function that returns the next chunk of data from the socket.

        Returns:
        str: The readd content of the message.
        """
        
        if debug_mode:
            print(f"[SCRMessage::read] The input buffer is {buffer}")

        # Step 1: Read the size header (which ends with a colon ":")
        while ':' not in buffer:
            try:
                chunk = read()  # read one chunk
                if not chunk:
                    if debug_mode:
                        print("not chunk")
                    return ""
                buffer += chunk.decode('utf-8')
                if debug_mode:
                    print(f"[SCRMessage::read] chunk is {chunk}, buffer is {buffer}")
            except BlockingIOError:
                print("[SCRMessage::read] BlockingIOError")
                return ""
        
        if debug_mode:
            print(f"[SCRMessage::read] After receiving colon, buffer is {buffer}")

        size_str, remainder = str(buffer).split(":", 1)
        message_size = int(size_str)

        # Step 2: Read the message content based on the size
        while len(buffer) < message_size:
            try:
                chunk = read()
                if not chunk:
                    raise ValueError("Insufficient data received, expected more content.")
                buffer += chunk.decode('utf-8')
            except BlockingIOError:
                return ""

        if debug_mode:
            print(f"[SCRMessage::read] before slicing, buffer is {buffer}")

        content = remainder[:message_size]
        buffer.assign(remainder[message_size:])

        if debug_mode:
            print(f"[SCRMessage::read] After slicing, buffer is {buffer}")

        return content