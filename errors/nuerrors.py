from logger.logger import NuMailLogger, server_log

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
NuMail Request Errors
    7.6.0 NuMail request error
    7.6.1 Cannot connect to server
    7.6.2 Another connection already open
    7.6.3 Connection not open
    7.6.4 Connection reset
    7.6.5 Connection timeout
NuMail DNS Resolver Errors
    7.7.0 NuMail DNS resolver error
    7.7.1 AIODNS Error
    7.7.2 DNS server not available
    7.7.3 DNS server returned answer with no data
    7.7.4 Connection timed out
"""

"""
NuMail Protocol Errors:
    6.0.0 Catch all error
Network Error:
    6.5.1 Delivery status successful
    6.5.2 Error connecting to server
"""

error_log = NuMailLogger("error.log")

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
        error_log.log(str(self), "error")
    
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
    
    @staticmethod
    def codeParts(code: str):
        return code.split(".")