import re

from server.message.server_parser import numail_server_parser
from errors.nuerrors import NuMailError
from server.message.MessageLine import MessageLine
from config.config import server_settings
from db.db import search_mailbox
from server.client.client import NuMailRequest
from server.client.reader import read_numail, init_numail
from server.client.dns import resolve_dns, is_ip
from logger.logger import server_log

DEBUG_VARS = {
    "dns_addr": "rutstech.com",
    "server_addr": "localhost",
    "server_port": 7778,
    "chck_addr": "127.0.0.1",
    }

@numail_server_parser
async def mod_chck(reader, writer, message, local_stack, state, loop, action="", what="", params=""):
    if action == "RECEIVE":
        if what == "MAIL":
            full_email = re.search(r"^\s*<\s*([a-zA-Z0-9.!#$%&'*+\-/=?^_`{|}~]+)@([a-zA-Z0-9._\-]+)\s*>\s*$", params, re.MULTILINE)
            if full_email:
                email_domain = full_email.group(2)
                if email_domain == server_settings["domain"] or email_domain == server_settings["public_ip"] or email_domain == server_settings["ip"]:
                    mailbox = search_mailbox(full_email.group(1))
                    if mailbox:
                        if mailbox["mbReceive"]:
                            writer.write(MessageLine(f"250 6.2.1 {full_email.group(1)}@{email_domain}... Recipient ok and receiving", message).bytes())
                            await writer.drain()
                        else:
                            writer.write(MessageLine(f"500 6.2.2 {full_email.group(1)}@{email_domain}... Recipient not ok and not receiving", message).bytes())
                            await writer.drain()
                    else:
                        writer.write(MessageLine(f"550 Invalid mailbox", message).bytes())
                        await writer.drain()
                else:
                    try:
                        mx = []
                        numail_dns_settings = {}
                        if not is_ip(email_domain):
                            try:
                                dns_domain = email_domain
                                if "dns_addr" in DEBUG_VARS.keys():
                                    dns_domain = DEBUG_VARS["dns_addr"]

                                dns_rec = await resolve_dns(dns_domain, ["MX"])
                                mx = sorted(dns_rec["MX"], key=lambda x: x["priority"])
                            except:
                                pass

                            try:
                                dns_txt = await resolve_dns(f"_numail.{dns_domain}", ["TXT"], 10)

                                for record in dns_txt["TXT"]:
                                    matches = re.finditer(r"\s*([a-z\-0-9]+)\s*=\s*([0-9a-zA-Z\-@!#$%^&*\(\)_+*/.<>\\?`~:'\"\[\]{}|]+)\s*;", record["text"])
                                    for match in matches:
                                        numail_dns_settings[match.group(1)] = match.group(2)
                            except:
                                pass

                        if "server_port" in DEBUG_VARS.keys():
                            port = DEBUG_VARS["server_port"]
                        elif "port" in numail_dns_settings.keys() and numail_dns_settings["port"].isdigit():
                            port = int(numail_dns_settings["port"])
                        else:
                            port = 25

                        request_addr = email_domain
                        if "server_addr" in DEBUG_VARS.keys():
                            request_addr = DEBUG_VARS["server_addr"]
                        
                        loop_range = [request_addr]
                        if len(mx) > 0 and "server_addr" not in DEBUG_VARS.keys():
                            loop_range = [domn["host"] for domn in mx]
                        
                        i = 1
                        loop_range_size = len(loop_range)
                        for domain in loop_range:
                            # request = NuMailRequest(full_email.group(2), 7777)
                            request = NuMailRequest(domain, port)
                            
                            try:
                                await request.connect()
                            except NuMailError as e:
                                if i == loop_range_size:
                                    raise e
                                else:
                                    i += 1
                                    continue
                            
                            init = await init_numail(request)
                            if init:
                                chck_address = email_domain
                                if "chck_addr" in DEBUG_VARS.keys():
                                    chck_address = DEBUG_VARS["chck_addr"]
                                message_send = await request.send(f"CHCK RECEIVE MAIL: <{full_email.group(1)}@{chck_address}>")
                                message_split = message_send.split("\r\n")
                                message_split = [i for i in message_split if i]
                                message_list = []
                                for message_part in message_split:
                                    message_list.append(read_numail(message_part))
                                
                                if len(message_list) > 0:
                                    if message_list[0][1] == "6.2.1":
                                        writer.write(MessageLine(f"250 6.2.1 {full_email.group(1)}@{email_domain}... Recipient ok and receiving", message).bytes())
                                        await writer.drain()
                                    else:
                                        writer.write(MessageLine(f"500 6.2.2 {full_email.group(1)}@{email_domain}... Recipient not ok and not receiving", message).bytes())
                                        await writer.drain()
                                else:
                                    writer.write(MessageLine(f"451 Requested action aborted: local error in processing", message).bytes())
                                    await writer.drain()
                            else:
                                writer.write(MessageLine(f"500 6.2.3 {full_email.group(1)}@{email_domain}... Recipient not using NuMail", message).bytes())
                                await writer.drain()
                            await request.close()
                            
                            break

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
                        server_log.log(e, "error")
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