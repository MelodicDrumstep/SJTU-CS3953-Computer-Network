from enum import Enum

class MessageType(Enum):
    Client2Server = 1
    Server2Client = 2

class Message:
    def __init__(self, message_type, hostname, content):
        self.message_type_ = message_type
        self.hostname_ = hostname
        self.content_ = content

    def getHostname(self):
        return self.hostname_

    def getContent(self)
        return self.content_

    def serialize(self)
        return str(self.message_type_) + hostname + ":" + content

    @classmethod
    def from_serialized(cls, serialized_str):
        if len(serialized_str) < 2:
            raise ValueError("Invalid serialized string format")
        message_type_value = int(serialized_str[0])
        if (message_type_value != 1) and (message_type_value != 2):
            raise ValueError("Invalid message type value")
        hostname_end_index = serialized_str.find(':', 1)
        if hostname_end_index == -1:
            raise ValueError("Invalid serialized string format")

        message_type = MessageType(message_type_value)
        hostname = serialized_str[1:hostname_end_index]
        content = serialized_str[hostname_end_index + 1:]
        return cls(message_type, hostname, content)