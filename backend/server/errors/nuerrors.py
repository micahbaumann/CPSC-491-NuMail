"""
NuMail Server Errors:
    7.0.0: catch all error
Config Errors:
    7.1.0: Config Error
    7.1.1: Error opening config file
    7.1.2: Syntax error in Config File
Server Errors
    7.2.0 Server Error
    7.2.1 Error starting server
    7.2.2 Port and/or address in use
"""

class NuMailError(Exception):
    def __init__(self, code="7.0.0", message="", other=None, line=None, file=None):
        self.code = code
        self.message = message
        self.other = other
        self.line = line
        self.file = file
        super().__init__(f"NuMail Error {self.code}: {self.message}")
    
    def __str__(self):
        return f"NuMail Server Error {self.code}: {self.message}"
    
    def info(self):
        return {
            "code": self.code,
            "message": self.message,
            "line": self.line,
            "file": self.file,
            "other": self.other,
        }