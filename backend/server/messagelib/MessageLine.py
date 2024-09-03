class MessageLine:
    def __init__(self, line:str|None = "") -> None:
        self.line = line
    
    def __bytes__(self) -> bytes:
        return f"{self.line}\r\n".encode('ascii', 'replace')
    
    def __str__(self) -> str:
        return f"{self.line}\r\n".encode('ascii', 'replace')
    
    def bytes(self) -> bytes:
        return f"{self.line}\r\n".encode('ascii', 'replace')