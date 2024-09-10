from datetime import datetime
from pathlib import Path
import logging.config

"""
Creates and updates NuMail Server logs
"""
class NuMailLogger:
    """
    Initializes the log file
    Arguments:
    file: the name of the file for the log
    path (default is in the logs folder of the backend directory): a path object to the directory where the log file is located
    """
    def __init__(self, file, path: Path | None = None) -> None:
        if path is None:
            self.path = Path(__file__).parent.parent.parent / "logs"
        else:
            self.path = path
        self.path.mkdir(parents=True, exist_ok=True)
        self.file = file
    
    """
    Appends the log file
    Arguments:
    msg: The message to log
    type (default "message"): The type of message (message, error, warning, etc.). None does not put any type
    """
    def log(self, msg: str, type: str | None = "message") -> None:
        abs_file = self.path / self.file
        with open(abs_file.resolve(), "a") as file:
            if type != None:
                file.write(f"[{datetime.now()}] [{type}] {msg}\n")
            else:
                file.write(f"[{datetime.now()}] {msg}\n")

# Initialize the main server log
server_log = NuMailLogger("server.log")