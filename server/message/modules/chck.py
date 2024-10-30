import re

from server.message.server_parser import numail_server_parser
from errors.nuerrors import NuMailError
from server.message.MessageLine import MessageLine
from config.config import server_settings
from db.db import search_mailbox
from server.client.client import NuMailRequest
from server.client.reader import read_numail
from server.client.dns import resolve_dns
from logger.logger import server_log

@numail_server_parser
async def mod_chck(reader, writer, message, local_stack, state, loop, action="", what="", params=""):
    if action == "RECEIVE":
        if what == "MAIL":
            full_email = re.search(r"^\s*<\s*([a-zA-Z0-9.!#$%&'*+\-/=?^_`{|}~]+)@([a-zA-Z0-9._\-]+)\s*>\s*$", params, re.MULTILINE)
            if full_email:
                if full_email.group(2) == server_settings["domain"] or full_email.group(2) == server_settings["public_ip"] or full_email.group(2) == server_settings["ip"]:
                    mailbox = search_mailbox(full_email.group(1))
                    if mailbox:
                        if mailbox["mbReceive"]:
                            writer.write(MessageLine(f"250 6.2.1 {full_email.group(1)}@{full_email.group(2)}... Recipient ok and receiving", message).bytes())
                            await writer.drain()
                        else:
                            writer.write(MessageLine(f"500 6.2.2 {full_email.group(1)}@{full_email.group(2)}... Recipient not ok and not receiving", message).bytes())
                            await writer.drain()
                    else:
                        writer.write(MessageLine(f"550 Invalid mailbox", message).bytes())
                        await writer.drain()
                else:
                    try:
                        print("test")
                        dns_rec = await resolve_dns("rutstech.com", ["MX", "TXT"])
                        print(dns_rec)
                        # Sort list to order higher priority first
                        mx = sorted(dns_rec["MX"], key=lambda x: x[0])

                        for record in dns_rec["TXT"]:
                            pass

                        print(mx)
                        # request = NuMailRequest(full_email.group(2), 7777)
                        request = NuMailRequest("localhost", 7778)
                        print(await request.connect())
                        message_send = await request.send("EHLO example.com")
                        print(message_send)
                        

                        # Finish read_numail


                        code, excode, msg = read_numail(message_send)
                        print(code)
                        print(excode)
                        print(msg)
                        await request.close()
                        print("test2")
                        # Temp Output
                        writer.write(MessageLine(f"Done", message).bytes())
                        await writer.drain()
                    except NuMailError as e:
                        parts = NuMailError.codeParts(e.code)
                        if parts and parts[1] == "6":
                            # Implement errors for requests errors
                            writer.write(MessageLine(f"451 6.5.2 Error connecting to server", message).bytes())
                            await writer.drain()
                        elif parts and parts[1] == "7":
                            # Implement errors for DNS errors
                            if parts[2] == "3" or parts[2] == "2":
                                writer.write(MessageLine(f"520 6.5.2 Error connecting to server", message).bytes())
                                await writer.drain()
                            else:
                                writer.write(MessageLine(f"451 6.5.2 Error connecting to server", message).bytes())
                                await writer.drain()
                        else:
                            writer.write(MessageLine(f"451 Requested action aborted: local error in processing", message).bytes())
                            await writer.drain()
                        
                        server_log.log(e, "error")
                    except Exception as e:
                        writer.write(MessageLine(f"451 Requested action aborted: local error in processing", message).bytes())
                        await writer.drain()




                    # TEST THIS


            else:
                writer.write(MessageLine(f"501 Invalid parameters", message).bytes())
                await writer.drain()
            loop.returnLoop()
        else:
            raise NuMailError(code="7.3.0", message="Module Error")
    else:
        raise NuMailError(code="7.3.0", message="Module Error")