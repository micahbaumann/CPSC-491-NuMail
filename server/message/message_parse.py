import asyncio
import re
import time

from server.message.MessageLine import MessageLine
from server.message.NuMailMessage import NuMailMessage
from errors.nuerrors import NuMailError
from logger.logger import server_log
from config.config import server_settings
from server.message.modules.auth import mod_auth
from server.message.modules.chck import mod_chck
from db.db import get_mailbox, send_message, msg_db_type, update_receiver, retreive_attachment, update_sent, retreive_attachment_file, update_retrieve, receive_message
from server.message.modules.data import mod_data
from server.client.dns import resolve_dns, is_ip, decode_txt
from server.client.reader import read_numail, init_numail, NuMailRequest
from server.message.modules.atch import mod_atch
from server.message.Attachment import Attachment


DEBUG_VARS = {
    # "to_port": "7777",
}


"""
Checks if commands are valid compared to a string
Arguments:
string: The command
equals: The string to compare the command to
commands: Controls how arguments are treated. 0 = Optional arguments. 1 = Must have arguments. 2 = No arguments.
"""
def check_command(string:str, equals:str, commands=2) -> bool:
    retn = None
    if commands == 0:
        retn = string == equals or (len(string) > 4 and string[:5] == equals + " ")
    elif commands == 1:
        retn = len(string) > 4 and string[:5] == equals + " "
    else:
        retn = string == equals
    return retn

def parse_address(address: str) -> list:
    full_email = re.search(r"^\s*([a-zA-Z0-9.!#$%&'*+\-\/=?^_`{|}~]+)@([a-zA-Z0-9._\-]+)\s*$", address.lower(), re.MULTILINE)
    if full_email:
        return [full_email.group(1), full_email.group(2)]

"""
Handels NuMail requests
Arguments:
reader: An asyncio reader object
writer: An asyncio writer object
message_stack: The message stack
"""
async def numail_parse(reader, writer, message_stack):
    # writer.write(b"numail\r\n")
    # await writer.drain()
    # message = await reader.read(1024)
    # writer.write(f"{message.strip()}\r\n".encode("ascii"))
    # await writer.drain()

    addr = message_stack.get_client_ip()
    while True:
        try:
            data = await asyncio.wait_for(reader.read(int(server_settings["buffer"])), float(server_settings["read_timeout"]))
            message = data.decode("ascii")
            message_stack.append("client", message)
            trim_message = message.strip()
            if not message:
                print(f"Connection from {addr[0]} port {addr[1]} closed")
                break

            if trim_message == "QUIT":
                return "exit"
            elif check_command(trim_message, "EHLO", 0):
                writer.write(MessageLine(f"503 Bad sequence of commands", message_stack).bytes())
                await writer.drain()
            elif check_command(trim_message, "HELO", 0):
                writer.write(MessageLine(f"503 Bad sequence of commands", message_stack).bytes())
                await writer.drain()
            elif check_command(trim_message, "RSET", 0):
                writer.write(MessageLine(f"250 Ok", message_stack).bytes())
                await writer.drain()
                return "continue"
            elif check_command(trim_message, "NOOP", 0):
                writer.write(MessageLine(f"250 Ok", message_stack).bytes())
                await writer.drain()
            elif check_command(trim_message, "AUTH", 1):
                if trim_message[5:] == "LOGIN":
                    login, username = await mod_auth(reader=reader, writer=writer, message=message_stack, method="LOGIN")
                    if login:
                        message_stack.set_client_username(username)
                        message_stack.set_is_send(True)
                else:
                    writer.write(MessageLine(f"504 \"{trim_message[5:]}\" not implemented", message_stack).bytes())
                    await writer.drain()
            elif check_command(trim_message, "MAIL", 1):
                if len(trim_message) > 9 and trim_message[5:10] == "FROM:":
                    
                    if len(message_stack.get_client_username()) > 0 or message_stack.get_is_send():
                        full_email = re.search(r"^\s*<\s*([a-zA-Z0-9.!#$%&'*+\-/=?^_`{|}~]+)@([a-zA-Z0-9._\-]+)\s*>\s*$", trim_message[10:], re.MULTILINE)
                        part_email = re.search(r"^\s*<\s*([a-zA-Z0-9.!#$%&'*+\-/=?^_`{|}~]+)\s*>\s*$", trim_message[10:], re.MULTILINE)

                        server_self = ""
                        if "visible_domain" in server_settings and server_settings["visible_domain"]:
                            server_self = server_settings["visible_domain"]
                        elif "domain" in server_settings and server_settings["domain"]:
                            server_self = server_settings["domain"]
                        elif "public_ip" in server_settings and server_settings["public_ip"]:
                            server_self = server_settings["public_ip"]
                        else:
                            server_self = server_settings["ip"]
                        
                        if full_email:
                            mailbox = get_mailbox(user_name=message_stack.get_client_username(), mb_name=full_email.group(1))
                            if mailbox and server_self == full_email.group(2).lower():
                                message_stack.set_from_addr(f"{full_email.group(1).lower()}@{full_email.group(2).lower()}")
                                writer.write(MessageLine(f"250 2.1.0 {full_email.group(1).lower()}@{full_email.group(2).lower()}... Sender ok", message_stack).bytes())
                                await writer.drain()
                            else:
                                writer.write(MessageLine(f"550 Invalid mailbox", message_stack).bytes())
                                await writer.drain()
                        elif part_email:
                            mailbox = get_mailbox(user_name=message_stack.get_client_username().lower(), mb_name=part_email.group(1))
                            if mailbox:
                                message_stack.set_from_addr(f"{part_email.group(1).lower()}@{server_self.lower()}")
                                writer.write(MessageLine(f"250 2.1.0 {part_email.group(1).lower()}@{server_self}... Sender ok", message_stack).bytes())
                                await writer.drain()
                            else:
                                writer.write(MessageLine(f"550 Invalid mailbox", message_stack).bytes())
                                await writer.drain()
                        else:
                            writer.write(MessageLine(f"501 Invalid parameters", message_stack).bytes())
                            await writer.drain()
                    else:
                        full_email = re.search(r"^\s*<\s*([a-zA-Z0-9.!#$%&'*+\-/=?^_`{|}~]+)@([a-zA-Z0-9._\-]+)\s*>\s*$", trim_message[10:], re.MULTILINE)
                        email_domain = full_email.group(2).lower()
                        self_id_client = message_stack.get_client_self_id().lower()

                        client_self_true = False
                        if email_domain != self_id_client:
                            to_mx = []
                            try:
                                to_dns_results = await resolve_dns(email_domain, ["MX"])
                                to_mx = sorted(to_dns_results["MX"], key=lambda x: x["priority"])
                            except:
                                pass

                            for domain in to_mx:
                                if domain["host"] == self_id_client:
                                    client_self_true = True
                                    break
                        if full_email and (client_self_true or full_email.group(2).lower() == self_id_client):
                            message_stack.set_from_addr(f"{email_domain}@{full_email.group(2).lower()}")
                            writer.write(MessageLine(f"250 2.1.0 {email_domain}@{full_email.group(2).lower()}... Sender ok", message_stack).bytes())
                            await writer.drain()
                        else:
                            writer.write(MessageLine(f"501 Invalid parameters", message_stack).bytes())
                            await writer.drain()
                else:
                    writer.write(MessageLine(f"504 \"{trim_message[5:]}\" not implemented", message_stack).bytes())
                    await writer.drain()
            elif check_command(trim_message, "CHCK", 1):
                confirm = re.search(r"^CHCK READ CONFIRM:(.+)$", trim_message, re.MULTILINE)
                if len(trim_message) > 17 and trim_message[5:18] == "RECEIVE MAIL:":
                    await mod_chck(reader=reader, writer=writer, message=message_stack, action="RECEIVE", what="MAIL", params=trim_message[18:])
                elif confirm:
                    await mod_chck(reader=reader, writer=writer, message=message_stack, action="RDCF", what="", params=confirm.group(1).strip())
                else:
                    writer.write(MessageLine(f"504 \"{trim_message[5:]}\" not implemented", message_stack).bytes())
                    await writer.drain()
            elif check_command(trim_message, "RCPT", 1):
                if len(trim_message) > 7 and trim_message[5:8] == "TO:":
                    message_stack.to_addr = trim_message[8:].strip().lower()
                    writer.write(MessageLine(f"250 2.1.5 {message_stack.get_to_addr().strip("<>").lower()}... Recipient ok", message_stack).bytes())
                    await writer.drain()
                else:
                    writer.write(MessageLine(f"504 \"{trim_message[5:]}\" not implemented", message_stack).bytes())
                    await writer.drain()
            elif check_command(trim_message, "MSGT", 1):
                if trim_message[5:] == "MAIL":
                    message_stack.numail["message_type"] = "mail"
                    writer.write(MessageLine(f"250 message type set to regular mail", message_stack).bytes())
                    await writer.drain()
                else:
                    writer.write(MessageLine(f"504 \"{trim_message[5:]}\" not implemented", message_stack).bytes())
                    await writer.drain()
            elif check_command(trim_message, "DATA", 2):
                writer.write(MessageLine(f"354 Enter mail, end with \".\" on a line by itself", message_stack).bytes())
                await writer.drain()
                await mod_data(reader=reader, writer=writer, message=message_stack)
            elif check_command(trim_message, "DLVR", 2):
                if message_stack.from_addr == "":
                    writer.write(MessageLine("400 6.5.1 No from address found or invalid from address", message_stack).bytes())
                    await writer.drain()
                elif message_stack.to_addr == "":
                    writer.write(MessageLine("400 6.5.2 No to address found or invalid to address", message_stack).bytes())
                    await writer.drain()
                elif message_stack.payload == "":
                    writer.write(MessageLine("400 6.5.3 No body address found or invalid body", message_stack).bytes())
                    await writer.drain()
                elif "message_type" not in message_stack.numail.keys() or not message_stack.numail["message_type"]:
                    writer.write(MessageLine("400 6.5.4 No message type found", message_stack).bytes())
                    await writer.drain()
                else:
                    to_parts = parse_address(message_stack.to_addr)
                    from_parts = parse_address(message_stack.from_addr)
                    if not from_parts:
                        writer.write(MessageLine("400 6.5.1 No from address found or invalid from address", message_stack).bytes())
                        await writer.drain()
                    elif not to_parts:
                        writer.write(MessageLine(f"400 6.5.2 No to address found or invalid to address", message_stack).bytes())
                        await writer.drain()
                    else:
                        to_mx = []
                        try:
                            to_dns_results = await resolve_dns(to_parts[1], ["MX"])
                            to_mx = sorted(to_dns_results["MX"], key=lambda x: x["priority"])
                        except:
                            pass
                        
                        numail_dns_settings = {}
                        try:
                            to_dns_results_txt = await resolve_dns(f"_numail.{to_parts[1]}", ["TXT"])
                            for record in to_dns_results_txt["TXT"]:
                                numail_dns_settings.update(decode_txt(record["text"]))
                        except:
                            pass
                            
                        if "to_port" in DEBUG_VARS.keys():
                            to_port = DEBUG_VARS["to_port"]
                        elif "port" in numail_dns_settings.keys() and numail_dns_settings["port"].isdigit():
                            to_port = int(numail_dns_settings["port"])
                        else:
                            to_port = 25
                        
                        def part_equals(domain: str, mx: list) -> bool:
                            for server in mx:
                                if server["host"] == domain:
                                    return True
                            return False
                        
                        if to_parts[1] == server_settings["visible_domain"] or part_equals(server_settings["domain"], to_mx) or to_parts[1] == server_settings["domain"] or to_parts[1] == server_settings["public_ip"] or to_parts[1] == server_settings["ip"]:
                            upload_status = receive_message(
                                from_addr = message_stack.from_addr,
                                to_addr = message_stack.to_addr,
                                msgt = int(msg_db_type(message_stack.numail["message_type"].upper())),
                                data = message_stack.payload,
                                readConfirm = message_stack.read_confirm,
                                attachments = message_stack.attachments
                            )

                            if upload_status:
                                writer.write(MessageLine(f"250 6.5.1 {upload_status["messageId"]} Message successfully delivered", message_stack).bytes())
                                await writer.drain()
                            else:
                                writer.write(MessageLine(f"550 Unable to deliver message", message_stack).bytes())
                                await writer.drain()
                        else:
                            # Being sent from this server
                            if message_stack.client_username:

                                # Upload to DB
                                upload_status = send_message(
                                    from_addr = message_stack.from_addr,
                                    to_addr = message_stack.to_addr,
                                    msgt = int(msg_db_type(message_stack.numail["message_type"].upper())),
                                    data = message_stack.payload,
                                    readConfirm = message_stack.read_confirm,
                                    receiver_id = None,
                                    attachments = message_stack.attachments
                                )
                                
                                if not upload_status:
                                    writer.write(MessageLine(f"451 Requested action aborted: local error in processing", message_stack).bytes())
                                    await writer.drain()
                                else:
                                    i = 1
                                    loop_range_size = len(to_mx)
                                    for domain in to_mx:
                                        request = NuMailRequest(domain["host"], to_port)
                                        try:
                                            await request.connect()
                                        except NuMailError as e:
                                            if i == loop_range_size:
                                                writer.write(MessageLine(f"550 Unable to connect to server", message_stack).bytes())
                                                await writer.drain()
                                                break
                                            else:
                                                i += 1
                                                continue
                                        init = await init_numail(request) # bool

                                        if init:
                                            try:
                                                chck = await request.send(f"CHCK RECEIVE {message_stack.numail["message_type"].upper()}: <{message_stack.to_addr}>")
                                                if read_numail(chck)[0] != "250":
                                                    raise

                                                from_adr = await request.send(f"MAIL FROM: <{message_stack.from_addr}>")
                                                if read_numail(from_adr)[0] != "250":
                                                    raise

                                                to_adr = await request.send(f"RCPT TO: {message_stack.to_addr}")
                                                if read_numail(to_adr)[0] != "250":
                                                    raise

                                                msgt = await request.send(f"MSGT {message_stack.numail["message_type"].upper()}")
                                                if read_numail(msgt)[0] != "250":
                                                    raise

                                                data = await request.send(f"DATA")
                                                if read_numail(data)[0] != "354":
                                                    raise

                                                message_split = message_stack.payload.split("\r\n")
                                                for line in message_split:
                                                    send_line = line
                                                    if len(send_line) > 0 and send_line[0] == ".":
                                                        send_line = f".{send_line}"
                                                    await request.push(send_line)

                                                payload = await request.send(".")
                                                if read_numail(payload)[0] != "250":
                                                    raise

                                                for attachment in message_stack.attachments:
                                                    # Send attachment
                                                    atch = await request.send(f"ATCH FILE: {attachment.id} {message_stack.from_addr.split('@')[1]}")
                                                    if read_numail(atch)[0] != "250":
                                                        raise

                                                dlvr = await request.send(f"DLVR")
                                                dlvr_parts = read_numail(dlvr)
                                                if dlvr_parts[0] != "250":
                                                    raise

                                                writer.write(MessageLine(f"250 6.5.1 {dlvr_parts[2].split()[0]} Message successfully delivered", message_stack).bytes())
                                                await writer.drain()
                                                
                                                update_receiver(upload_status["message"]["messageId"], dlvr_parts[2].split()[0])
                                                update_sent(upload_status["message"]["messageId"])
                                            except:
                                                writer.write(MessageLine(f"450 Unable to connect to \"{message_stack.to_addr}\"", message_stack).bytes())
                                                await writer.drain()
                                        else:
                                            # If sending SMTP email
                                            writer.write(MessageLine(f"500 6.0.0 SMTP not supported. Unable to connect to \"{message_stack.to_addr}\"", message_stack).bytes())
                                            await writer.drain()

                                        await request.close()
                                        break
                            else:
                                writer.write(MessageLine(f"550 Not authorized to send from this address", message_stack).bytes())
                                await writer.drain()
            elif check_command(trim_message, "ATCH", 1):
                params = re.search(r"^ATCH UPLOAD(:(.*))*$", trim_message, re.MULTILINE)
                params_attch = re.search(r"^ATCH FILE: *(\S+) +(\S+)$", trim_message, re.MULTILINE)
                params_info = re.search(r"^ATCH RETRIEVE INFO: *(\S+)$", trim_message, re.MULTILINE)
                params_retrieve = re.search(r"^ATCH RETRIEVE: *(\S+)$", trim_message, re.MULTILINE)
                if params:
                    if message_stack.client_username:
                        expire = expire_on_retrieve = None
                        notRead = False
                        if params.group(2):
                            params_list = params.group(2).strip().split(' ')
                            for param in params_list:
                                ex = re.search(r"^expire=([0-9]+)$", param, re.MULTILINE)
                                er = re.search(r"^expireOnRetrieve=((TRUE)|(FALSE))$", param, re.MULTILINE)
                                if ex:
                                    expire = ex.group(1)
                                elif er:
                                    expire_on_retrieve = er.group(1) == "TRUE"
                                else:
                                    notRead = True
                                    writer.write(MessageLine(f"501 Invalid parameters", message_stack).bytes())
                                    await writer.drain()
                        
                        if not notRead:
                            writer.write(MessageLine(f"354 Enter attachment, end with \".\" on a line by itself", message_stack).bytes())
                            await writer.drain()
                            if not expire_on_retrieve:
                                expire_on_retrieve = False
                            await mod_atch(reader=reader, writer=writer, message=message_stack, expire=expire, expire_on_retrieve=expire_on_retrieve)
                    else:
                        writer.write(MessageLine(f"550 Not authorized to add attachment", message_stack).bytes())
                        await writer.drain()
                elif params_attch:
                    attch_id = params_attch.group(1).strip()
                    attch_domain = params_attch.group(2).strip()
                    message_stack.attachments.append(Attachment(id=attch_id, from_server=attch_domain))
                    writer.write(MessageLine(f"250 Attachment {attch_id} attached", message_stack).bytes())
                    await writer.drain()
                elif params_info:
                    attch_id = params_info.group(1).strip()
                    attch_info = retreive_attachment(attch_id)
                    if attch_info:
                        writer.write(MessageLine(f"250-Info retrieved", message_stack).bytes())
                        if attch_info["attachmentExpire"]:
                            attch_expr = attch_info["attachmentExpire"]
                        else:
                            attch_expr = ""
                        writer.write(MessageLine(f"250-expire={attch_expr}", message_stack).bytes())
                        if attch_info["attachmentExpireRet"]:
                            attch_delete = "TRUE"
                        else:
                            attch_delete = "FALSE"
                        writer.write(MessageLine(f"250 expireOnRetrieve={attch_delete}", message_stack).bytes())
                        await writer.drain()
                    else:
                        writer.write(MessageLine(f"500 6.6.1 Unable to retreive attachment", message_stack).bytes())
                        await writer.drain()
                elif params_retrieve:
                    attch_id = params_retrieve.group(1).strip()
                    attch_info = retreive_attachment(attch_id)
                    if attch_info:
                        if attch_info["attachmentExpire"] and int(attch_info["attachmentExpire"]) <= int(time.time()):
                            writer.write(MessageLine(f"500 6.6.2 Attachment Expired", message_stack).bytes())
                            await writer.drain()
                        elif attch_info["attachmentRetrieved"]:
                            writer.write(MessageLine(f"500 6.6.1 Unable to retreive attachment", message_stack).bytes())
                            await writer.drain()
                        else:
                            attch_file = retreive_attachment_file(attch_id)
                            if attch_file != False:
                                if len(attch_file) > 0:
                                    writer.write(MessageLine(f"250-Attachment retrieved", message_stack).bytes())
                                    writer.write(MessageLine(f"250-Content-Type: image/jpeg; name=\"{attch_info["attachmentName"]}\"", message_stack).bytes())
                                    writer.write(MessageLine(f"250-Content-Disposition: attachment; filename=\"{attch_info["attachmentName"]}\"", message_stack).bytes())
                                    writer.write(MessageLine(f"250-Content-Transfer-Encoding: base64", message_stack).bytes())
                                    writer.write(MessageLine(f"250-", message_stack).bytes())
                                    await writer.drain()
                                    writer.write(MessageLine(f"250 {attch_file}", message_stack).bytes())
                                    await writer.drain()
                                else:
                                    writer.write(MessageLine(f"250 Attachment retrieved", message_stack).bytes())
                                    await writer.drain()
                                
                                if attch_info["attachmentExpireRet"]:
                                    update_retrieve(attch_id)
                            else:
                                writer.write(MessageLine(f"500 6.6.1 Unable to retreive attachment", message_stack).bytes())
                                await writer.drain()
                    else:
                        writer.write(MessageLine(f"500 6.6.1 Unable to retreive attachment", message_stack).bytes())
                        await writer.drain()
                else:
                    writer.write(MessageLine(f"504 \"{trim_message[5:]}\" not implemented", message_stack).bytes())
                    await writer.drain()
            elif check_command(trim_message, "RDCF", 2):
                message_stack.read_confirm = True
                writer.write(MessageLine(f"250 6.2.1 Read confirmation set", message_stack).bytes())
                await writer.drain()
            else:
                writer.write(MessageLine("500 Command unrecognized", message_stack).bytes())
                await writer.drain()

            
        except TimeoutError:
            server_log.log(f"Connection {addr[0]} port {addr[1]} timeout", type="request_warning")
            writer.write(MessageLine("500 Connection timed out", message_stack).bytes())
            await writer.drain()
            break
        except UnicodeDecodeError as e:
            server_log.log(f"Connection {addr[0]} port {addr[1]} invalid character", type="request_error")
            writer.write(MessageLine("500 Invalid character", message_stack).bytes())
            await writer.drain()
            break
        except NuMailError as e:
            server_log.log(f"Connection {addr[0]} port {addr[1]}:\n{e}", type="request_error")
            writer.write(MessageLine("500 Unexpected error", message_stack).bytes())
            await writer.drain()
            if e.shutdown == True:
                raise e
            break
        except Exception as e:
            server_log.log(f"Connection {addr[0]} port {addr[1]}:\n{e}", type="request_error")
            writer.write(MessageLine("500 Unexpected error", message_stack).bytes())
            await writer.drain()
            break
    return "exit"

"""
Handels SMTP requests
Arguments:
reader: An asyncio reader object
writer: An asyncio writer object
message_stack: The message stack
"""
async def email_parse(reader, writer, message_stack):
    writer.write(b"email\r\n")
    await writer.drain()
    msg = await reader.read(1024)
    writer.write(f"{msg.strip()}\r\n".encode("ascii"))
    await writer.drain()