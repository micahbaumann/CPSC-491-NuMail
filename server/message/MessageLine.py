
"""
Formats a line for transport
"""
class MessageLine:
    """
    Initializes the object
    Arguments:
    line (default ""): the line to format
    msg_stack (optional): the message object
    """
    def __init__(self, line:str|None = "", msg_stack=None, is_client=False) -> None:
        self.line = line
        if is_client:
            msg_stack.append("client", f"{self.line}\r\n".encode('ascii', 'replace').decode("ascii"))
        else:
            msg_stack.append("server", f"{self.line}\r\n".encode('ascii', 'replace').decode("ascii"))

    
    """
    Returns a formated byte string
    """
    def __bytes__(self) -> bytes:
        return f"{self.line}\r\n".encode('ascii', 'replace')
    
    """
    Returns a formated string
    """
    def __str__(self) -> str:
        return f"{self.line}\r\n".encode('ascii', 'replace')
    
    """
    Returns a formated byte string
    """
    def bytes(self) -> bytes:
        return f"{self.line}\r\n".encode('ascii', 'replace')