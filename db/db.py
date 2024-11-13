import sqlite3
import contextlib
import bcrypt
import uuid

from logger.logger import server_log
from errors.nuerrors import NuMailError

# def get_db():
#     with contextlib.closing(sqlite3.connect("./sqlite/numail.db")) as db:
#         try:
#             db.row_factory = sqlite3.Row
#             yield db
#         finally:
#             db.close()

@contextlib.contextmanager
def get_db():
    db = sqlite3.connect("./db/sqlite/numail.db")
    try:
        db.row_factory = sqlite3.Row
        yield db
    finally:
        db.close()

def createUser(user_name: str, display_name: str, password: str, isAdmin: bool = False, first_name: str | None = None, last_name: str | None = None, company: str | None = None):
    with get_db() as db:
        user_exists = db.execute("SELECT * FROM Users WHERE userName = ?", (user_name,)).fetchone()
        if user_exists:
            raise NuMailError(code="7.4.1", message=f"User \"{user_name}\" already exists")
        else:
            pwd = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            db.execute("INSERT INTO Users(userName, firstName, lastName, displayName, company, password, isAdmin) VALUES (?, ?, ?, ?, ?, ?, ?)", (user_name, first_name, last_name, display_name, company, pwd, isAdmin))

            db.commit()
            user = db.execute("SELECT * FROM Users WHERE userName = ?", (user_name,)).fetchone()
            return {
                "user_id": user["userId"],
                "user_name": user["userName"],
                "first_name": user["firstName"],
                "last_name": user["lastName"],
                "display_name": user["displayName"],
                "company": user["company"],
                "is_admin": user["isAdmin"],

            }

def check_user_pwd(user_name: str, password: str) -> bool:
    with get_db() as db:
        user_exists = db.execute("SELECT * FROM Users WHERE userName = ?", (user_name,)).fetchone()
        if not user_exists:
            return False
        else:
            user_pwd = db.execute("SELECT password FROM Users WHERE userName = ?", (user_name,)).fetchone()
            return bcrypt.checkpw(password.encode('utf-8'), user_pwd[0])


def create_mailbox(mb_name: str, user_name: str, mb_type: int = 0, mb_send: bool = False, mb_receive: bool = False) -> None:
    with get_db() as db:
        user_exists = db.execute("SELECT * FROM Users WHERE userName = ?", (user_name,)).fetchone()
        if not user_exists:
            raise NuMailError(code="7.4.2", message=f"User \"{user_name}\" does not exists")
        else:
            mb_exists = db.execute("SELECT * FROM Mailboxes WHERE mbName = ?", (mb_name,)).fetchone()
            if not mb_exists:
                db.execute("INSERT INTO Mailboxes(mbUser, mbName, mbType, mbSend, mbReceive) VALUES (?, ?, ?, ?, ?)", (user_exists["userId"], mb_name, mb_type, mb_send, mb_receive))
                db.commit()
            else:
                raise NuMailError(code="7.5.1", message=f"Mailbox \"{mb_name}\" already exists")

def get_mailbox(mb_name: str, user_name: str) -> dict | bool:
    with get_db() as db:
        user_exists = db.execute("SELECT * FROM Users WHERE userName = ?", (user_name,)).fetchone()
        if not user_exists:
            return False
        else:
            mb_exists = db.execute("SELECT * FROM Mailboxes WHERE mbUser = ? AND mbName = ?", (user_exists["userId"], mb_name)).fetchone()
            if mb_exists:
                return dict(mb_exists)
            else:
                return False

def search_mailbox(mb_name: str) -> dict | bool:
    with get_db() as db:
        mb_exists = db.execute("SELECT * FROM Mailboxes WHERE mbName = ?", (mb_name,)).fetchone()
        if mb_exists:
            return dict(mb_exists)
        else:
            return False

def receive_message(from_addr: str, to_addr: str, msgt: str, data: str, deliveryConfirm: bool = True, readConfirm: bool = False) -> bool:
    with get_db() as db:
        unique = False
        while not unique:
            msgid = uuid.uuid1().hex
            msg_exists = db.execute("SELECT * FROM Messages WHERE messageId = ?", (msgid,)).fetchone()
            if not msg_exists:
                unique = True
        
        
        