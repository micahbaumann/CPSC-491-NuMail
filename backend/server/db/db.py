import sqlite3
import contextlib
import secrets
import hashlib
import base64

from logger.logger import NuMailLogger

def get_db():
    with contextlib.closing(sqlite3.connect("./sqlite/numail.db")) as db:
        try:
            db.row_factory = sqlite3.Row
            yield db
        finally:
            db.close()

def hash_password(pwd):
    iterations = 600000
    salt = secrets.token_hex(16)
    while '$' not in salt:
        salt = secrets.token_hex(16)
    return "{}${}${}${}".format("pbkdf2_sha256", iterations, salt, base64.b64encode(hashlib.pbkdf2_hmac("sha256", pwd.encode("utf-8"), salt.encode("utf-8"), iterations)).decode("ascii").strip())

def createUser(user_name: str, display_name: str, password: str, isAdmin: bool = False, first_name: str | None = None, last_name: str | None = None, company: str | None = None):
    with get_db() as db:
        user_exists = db.execute("SELECT * FROM Users WHERE userName = ?", (user_name,)).fetchone()
        if user_exists:
            raise NuMailLogger(code="7.4.1", message=f"User \"{user_name}\" already exists")
        else:
            pwd = hash_password(password)
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