import re

from server.client.client import NuMailRequest
from config.config import server_settings
from errors.nuerrors import NuMailError

"""
Attempts to initializes a NuMail connection. Returns a if it's NuMail (True/False)
Arguments:
request: A NuMailRequest object
self_id: An ID overide
"""
async def init_numail(request: NuMailRequest, self_id=None) -> bool:
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
    message_split = message_send.split("\r\n")
    message_split = [i for i in message_split if i]
    message_list = []
    try:
        for message in message_split:
            message_list.append(read_numail(message))
    except NuMailError as e:
        raise NuMailError(code="7.8.0", message=f"NuMail init error, \"{e}\"" )
    except Exception as e:
        raise NuMailError(code="7.8.0", message=f"NuMail init error, \"{e}\"" )

    if len(message_list) > 0:
        if message_list[0][0] == "250":
            if len(message_list[0][2]) >= 6 and message_list[0][2][:6] == "NUMAIL":
                message_send = await request.send(f"NUML")
                message_split = message_send.split("\r\n")
                message_split = [i for i in message_split if i]
                message_list_numl = []
                try:
                    for message in message_split:
                        message_list_numl.append(read_numail(message))
                except NuMailError as e:
                    raise NuMailError(code="7.8.0", message=f"NuMail init error, \"{e}\"" )
                except Exception as e:
                    raise NuMailError(code="7.8.0", message=f"NuMail init error, \"{e}\"" )
                if len(message_list_numl) > 0:
                    if message_list_numl[0][0] == "650":
                        ret = True
                else:
                    raise NuMailError(code="7.8.0", message=f"NuMail init error1" )

            else:
                ret = False
        else:
            raise NuMailError(code="7.8.0", message=f"NuMail init error2" )
    else:
        raise NuMailError(code="7.8.0", message=f"NuMail init error3" )

    mods = []
    first = True
    for message in message_list:
        if first:
            first = False
            continue
        mods.append(message[2])
    
    request.message_info.set_mods(mods)

    return ret

"""
Reads a message from NuMail and returns a list of the message parts
Arguments:
message: The NuMail message
"""
def read_numail(message: str) -> list:
    ret = []
    matches = re.search(r"^([23456][012345][0-9])([\ \-])([2456]\.[0-9][0-9]?[0-9]?\.[0-9][0-9]?[0-9]?)?(.*)$", message, re.MULTILINE)
    if matches:
        ret.append(matches.group(1))
        ret.append(matches.group(3))
        ret.append(matches.group(4))
        if matches.group(2) == "-":
            ret.append(True)
        else:
            ret.append(False)
        # Finish this (get other groups)
    else:
        raise NuMailError(code="7.8.1", message=f"NuMail reader error, \"invalid NuMail line\"" )
    return ret


def read_email():
    pass