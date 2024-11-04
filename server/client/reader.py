import re

from server.client.client import NuMailRequest
from config.config import server_settings
from errors.nuerrors import NuMailError

"""
Attempts to initializes a NuMail connection. Returns a list of if it's NuMail (True) and TBD
Arguments:
request: A NuMailRequest object
self_id: An ID overide
"""
async def init_numail(request: NuMailRequest, self_id=None) -> list:
    ret = False
    this_server = ""
    if self_id:
        this_server = self_id
    elif server_settings["domain"] != None and server_settings["domain"] != "":
        this_server = server_settings["domain"]
    elif server_settings["public_ip"] != None and server_settings["public_ip"] != "":
        this_server = server_settings["public_ip"]
    else:
        this_server = server_settings["ip"]
    
    message_send = await request.send(f"EHLO {this_server}")
    try:
        code, excode, msg = read_numail(message_send)
    except:
        pass #finish

    if code == 250:
        if len(msg) >= 6 and msg[:6] == "NUMAIL":
            message_send = await request.send(f"NUML")
            code, excode, msg = read_numail(message_send)
            if code == 650:
                ret = True

        else:
            pass # Handel error here
    else:
        pass # Handel error here

    return [ret, message_send]

"""
Reads a message from NuMail and returns a list of the message parts
Arguments:
message: The NuMail message
"""
def read_numail(message: str) -> list:
    ret = []
    matches = re.search(r"^([23456][012345][0-9])[\ \-]([2456]\.[0-9][0-9]?[0-9]?\.[0-9][0-9]?[0-9]?)?(.*)$", message, re.MULTILINE)
    if matches:
        ret.append(matches.group(1))
        ret.append(matches.group(2))
        ret.append(matches.group(3))
        # Finish this (get other groups)
    else:
        raise NuMailError(code="7.8.1", message=f"NuMail reader error, \"invalid NuMail line\"" )
    return ret


def read_email():
    pass