import sqlite3
import contextlib
import bcrypt
import uuid
import base64
import json

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


def create_mailbox(mb_name: str, user_name: str, mb_type: int = 0, mb_send: bool = False, mb_receive: bool = False, read_confirm: bool = False) -> None:
    with get_db() as db:
        user_exists = db.execute("SELECT * FROM Users WHERE userName = ?", (user_name,)).fetchone()
        if not user_exists:
            raise NuMailError(code="7.4.2", message=f"User \"{user_name}\" does not exists")
        else:
            mb_exists = db.execute("SELECT * FROM Mailboxes WHERE mbName = ?", (mb_name,)).fetchone()
            if not mb_exists:
                db.execute("INSERT INTO Mailboxes(mbUser, mbName, mbType, mbSend, mbReceive, mbReadConf) VALUES (?, ?, ?, ?, ?, ?)", (user_exists["userId"], mb_name, mb_type, mb_send, mb_receive, read_confirm))
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

def get_user_mailboxes(user_name: str) -> dict | bool:
    with get_db() as db:
        username_exists = db.execute("SELECT * FROM Users WHERE userName = ?", (user_name,)).fetchone()
        if not username_exists:
            return False
        else:
            user_exists = db.execute("SELECT * FROM Mailboxes WHERE mbUser = ?", (dict(username_exists)["userId"],)).fetchall()
            if not user_exists:
                return False
        return [dict(row) for row in user_exists]

def get_message(message_id: str) -> dict | bool:
    with get_db() as db:
        message_exists = db.execute("SELECT * FROM Messages WHERE messageId = ?", (message_id,)).fetchone()
        if not message_exists:
            return False
        else:
            return dict(message_exists)

def get_user_messages(user_id: int | None = None, user_name: str = "") -> dict | bool:
    with get_db() as db:
        if user_id != None:
            user_exists = db.execute("SELECT * FROM Mailboxes WHERE mbUser = ? AND mbReceive = TRUE", (user_id,)).fetchall()
            if not user_exists:
                return False
        elif user_name:
            username_exists = db.execute("SELECT * FROM Users WHERE userName = ?", (user_name,)).fetchone()
            if not username_exists:
                return False
            else:
                user_exists = db.execute("SELECT * FROM Mailboxes WHERE mbUser = ? AND mbReceive = TRUE", (dict(username_exists)["userId"],)).fetchall()
                if not user_exists:
                    return False
        else:
            return False
        
        mailboxes = [dict(row) for row in user_exists]
        messages = []
        for box in mailboxes:
            message_exists = db.execute("SELECT * FROM Messages WHERE messageMailbox = ?", (box["mailboxId"],)).fetchall()
            if message_exists:
                messages += [dict(row) for row in message_exists]
        
        if len(messages) > 0:
            return messages
        else:
            return False


def search_mailbox(mb_name: str) -> dict | bool:
    with get_db() as db:
        mb_exists = db.execute("SELECT * FROM Mailboxes WHERE mbName = ?", (mb_name,)).fetchone()
        if mb_exists:
            return dict(mb_exists)
        else:
            return False

def receive_message(from_addr: str, to_addr: str, msgt: int, data: str, readConfirm: bool = False, attachments: list = [], unsubscribe: str = "") -> bool | dict:
    with get_db() as db:
        unique = False
        while not unique:
            msgid = uuid.uuid1().hex
            msg_exists = db.execute("SELECT * FROM Messages WHERE messageId = ?", (msgid,)).fetchone()
            if not msg_exists:
                unique = True
        
        to_mb = search_mailbox(to_addr.split('@')[0])
        if to_mb:
            attch = []
            for attachment in attachments:
                attch.append([attachment.id, attachment.from_server])
            db.execute("INSERT INTO Messages(messageId, messageMailbox, messageType, messageFrom, messageTo, messageContent, readConfirm, messageAttachments, messageUnsubscribe) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (msgid, to_mb["mailboxId"], msgt, from_addr, to_addr, data, readConfirm, json.dumps(attch), unsubscribe))
            db.commit()
            msg_exists = db.execute("SELECT * FROM Messages WHERE messageId = ?", (msgid,)).fetchone()
            if msg_exists:
                return dict(msg_exists)
            else:
                return False
        else:
            return False

def send_message(from_addr: str, to_addr: str, msgt: int, data: str, receiver_id: str | None = None, readConfirm: bool = False, attachments: list = [], unsubscribe: str = "") -> bool | dict:
    with get_db() as db:
        unique = False
        while not unique:
            msgid = uuid.uuid1().hex
            msg_exists = db.execute("SELECT * FROM Messages WHERE messageId = ?", (msgid,)).fetchone()
            if not msg_exists:
                unique = True
        
        from_mb = search_mailbox(from_addr.split('@')[0])
        if from_mb:
            db.execute("INSERT INTO Messages(messageId, receiverId, messageMailbox, messageType, messageFrom, messageTo, messageContent, readConfirm, isSent, messageUnsubscribe) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (msgid, receiver_id, from_mb["mailboxId"], msgt, from_addr, to_addr, data, readConfirm, True, unsubscribe))
            db.commit()
            msg_exists = db.execute("SELECT * FROM Messages WHERE messageId = ?", (msgid,)).fetchone()
            if msg_exists:
                attch_exists = []
                for attachment in attachments:
                    try:
                        db.execute("INSERT INTO Attachments(attachmentId, attachmentMessage, attachmentLocation, attachmentExpire, attachmentExpireRet, attachmentName) VALUES (?, ?, ?, ?, ?, ?)", (attachment.id, msgid, str(attachment.location), attachment.expire, attachment.expireOnRetrieve, attachment.name))
                        db.commit()

                        attchmt = db.execute("SELECT * FROM Attachments WHERE attachmentId = ?", (attachment.id,)).fetchone()
                        if not attchmt:
                            return False
                        
                        attch_exists.append(dict(attchmt))
                    except Exception as e:
                        print(e)
                        return False

                return {
                    "message": dict(msg_exists),
                    "attachments": attch_exists
                }
            else:
                return False
        else:
            return False

def update_receiver(message: str, receiver: str) -> bool:
    with get_db() as db:
        try:
            db.execute("UPDATE Messages SET receiverId = ? WHERE messageId = ?", (receiver, message))
            db.commit()
            return True
        except:
            return False

def update_sent(message: str, sent: bool = True) -> bool:
    with get_db() as db:
        try:
            db.execute("UPDATE Messages SET messageSent = ? WHERE messageId = ?", (sent, message))
            db.commit()
            return True
        except:
            return False

def msg_db_type(type: str) -> int | bool:
    if type.upper() == "MAIL":
        return 0
    else:
        return False

def retreive_attachment(id: str) -> bool | dict:
    with get_db() as db:
        try:
            attchmt = db.execute("SELECT * FROM Attachments WHERE attachmentId = ?", (id,)).fetchone()

            if not attchmt:
                return False
            else:
                return dict(attchmt)
        except:
            return False

def retreive_message_attachments(id: str) -> bool | dict:
    with get_db() as db:
        try:
            attchmt = db.execute("SELECT * FROM Attachments WHERE attachmentMessage = ?", (id,)).fetchall()

            if not attchmt:
                return False
            else:
                return [dict(row) for row in attchmt]
        except:
            return False

def retreive_attachment_file(id: str) -> bool | str:
    with get_db() as db:
        try:
            attchmt = db.execute("SELECT * FROM Attachments WHERE attachmentId = ?", (id,)).fetchone()

            if not attchmt:
                return False
            else:
                ret = ""
                path = attchmt["attachmentLocation"]
                with open(path, "rb") as file:
                    file_contents = file.read()
                    encoded = base64.b64encode(file_contents)
                    ret =  encoded.decode('utf-8')
                return ret
        except Exception as e:
            return False

def update_retrieve(id: str, status: bool = True) -> bool:
    with get_db() as db:
        try:
            db.execute("UPDATE Attachments SET attachmentRetrieved = ? WHERE attachmentId = ?", (status, id))
            db.commit()
            return True
        except:
            return False
        
def delete_message(id: str):
    with get_db() as db:
        try:
            db.execute("DELETE FROM Messages WHERE messageId = ?", (id,))
            db.commit()
            return True
        except:
            return False