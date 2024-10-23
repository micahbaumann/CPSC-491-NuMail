import re

from server.client.client import NuMailRequest
from config.config import server_settings

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
    code, excode, msg = read_numail(message_send)

    if code == 250:
        if len(msg) >= 6 and msg[:6] == "NUMAIL":
            message_send = await request.send(f"NUML")
            code, excode, msg = read_numail(message_send)


            #Finish

        else:
            pass # Handel error her
    else:
        pass # Handel error here

    return [ret, message_send]

def read_numail(message: str):
    ret = []
    # if len(message) >= 3:
    #     ret.append(message[:3])
    #     if len(message) >= 9:
    #         if message[4:]
    #     else:
    #         ret.append(None)
    # else:
    #     ret.append(None)
    matches = re.search(r"^([23456][012345][0-9])[\ \-]([2456]\.[0-9][0-9]?[0-9]?\.[0-9][0-9]?[0-9]?)?(.*)$", message, re.MULTILINE)
    if matches:
        ret.append(matches.group(1))
        ret.append(matches.group(2))
        ret.append(matches.group(3))
        # Finish this (get other groups)
    return ret


def read_email():
    pass