
"""
Formats a line for transport
"""
class MessageLine:
    """
    Initializes the object
    Arguments:
    line (default ""): the line to format
    """
    def __init__(self, line:str|None = "") -> None:
        self.line = line
    
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