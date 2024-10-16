import re

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