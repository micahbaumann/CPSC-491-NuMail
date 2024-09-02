from datetime import datetime
from pathlib import Path

class NuMailLogger:
    def __init__(self, file, path: Path | None = None) -> None:
        if path is None:
            self.path = Path(__file__).parent.parent.parent / "logs"
        else:
            self.path = path
        self.path.mkdir(parents=True, exist_ok=True)
        self.file = file
    
    def log(self, msg: str) -> None:
        abs_file = self.path / self.file
        with open(abs_file.resolve(), "a") as file:
            file.write(f"[{datetime.now()}] {msg}\n")

server_log = NuMailLogger("server.log")