
"""
Formats a line for transport
"""
class MessageLine:
    """
    Initializes the object
    Arguments:
    line (default ""): the line to format
    msg_stack (optional): a list of recent messages
    """
    def __init__(self, line:str|None = "", msg_stack=None) -> None:
        self.line = line
        msg_stack.append(["server", f"{self.line}\r\n".encode('ascii', 'replace').decode("ascii")])

    
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