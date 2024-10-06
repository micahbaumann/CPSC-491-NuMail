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
Module Errors
    7.3.0 Module Error
    7.3.1 Required module parameters not found
User Errors
    7.4.0 User Error
    7.4.1 User already exsists
    7.4.2 User does not exsist
Mailbox Errors
    7.5.0 Mailbox Error
    7.5.1 Mailbox already exsists
    7.5.2 Mailbox does not exsist
"""

"""
Exception class for NuMail
"""
class NuMailError(Exception):
    """
    Initializes the object
    Arguments:
    code (default "7.0.0"): the NuMail Server error code
    message (default ""): The description of the error
    other (optional): a place to pass on prevous exceptions that may have triggered the current one
    line (optional): the line number the error occured on
    file (optional): the file the error occured in
    """
    def __init__(self, code="7.0.0", message="", other=None, line=None, file=None, shutdown=False):
        self.code = code
        self.message = message
        self.other = other
        self.line = line
        self.file = file
        self.shutdown = shutdown
        super().__init__(f"NuMail Error {self.code}: {self.message}")
    
    """
    Returns the full description and error code in a string
    """
    def __str__(self):
        return f"NuMail Server Error {self.code}: {self.message}"
    
    """
    Returns a dictionary with all the object data in it
    """
    def info(self):
        return {
            "code": self.code,
            "message": self.message,
            "line": self.line,
            "file": self.file,
            "other": self.other,
            "shutdown": self.shutdown,
        }