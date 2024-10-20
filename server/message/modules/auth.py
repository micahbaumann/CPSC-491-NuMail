import base64

from server.message.MessageLine import MessageLine
from server.message.server_parser import numail_server_parser
from db.db import check_user_pwd
from errors.nuerrors import NuMailError

@numail_server_parser
async def mod_auth(reader, writer, message, local_stack, state, loop, method="LOGIN"):
    if method == "LOGIN":
        if not state or state["mode"] == None:
            writer.write(MessageLine(f"334 {base64.b64encode(b'Username:').decode('ascii')}", message).bytes())
            await writer.drain()
            state["mode"] = 0
        elif state["mode"] == 0:
            try:
                state["username"] = base64.b64decode(local_stack[-1].encode('ascii')).decode('ascii')
            except:
                state["username"] = ""
            state["mode"] = 1
            writer.write(MessageLine(f"334 {base64.b64encode(b'Password:').decode('ascii')}", message).bytes())
            await writer.drain()
        elif state["mode"] == 1:
            try:
                state["password"] = base64.b64decode(local_stack[-1].encode('ascii')).decode('ascii')
            except:
                state["password"] = ""
            state["mode"] = 2
            result = [None, None]
            if check_user_pwd(state["username"], state["password"]):
                writer.write(MessageLine(f"235 2.7.0 Authentication successful", message).bytes())
                result = [True, state["username"]]
            else:
                writer.write(MessageLine(f"535 5.7.8 Authentication credentials invalid", message).bytes())
                result = [False, None]
            await writer.drain()
            loop.returnLoop()
            return result
    else:
        raise NuMailError(code="7.3.0", message="Module Error")
