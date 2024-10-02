import asyncio

from server.message.MessageLine import MessageLine
from server.message.NuMailMessage import NuMailMessage
from errors.nuerrors import NuMailError
from logger.logger import server_log
from config.config import server_settings
from server.message.modules.auth import mod_auth
from db.db import get_db


def check_command(string:str, equals:str, commands=2) -> bool:
    retn = None
    if commands == 0:
        retn = string == equals or (len(string) > 4 and string[:5] == equals + " ")
    elif commands == 1:
        retn = len(string) > 4 and string[:5] == equals + " "
    else:
        retn = string == equals
    return retn

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
                else:
                    writer.write(MessageLine(f"504 \"{trim_message[5:]}\" not implemented", message_stack).bytes())
                    await writer.drain()
            else:
                writer.write(MessageLine("500 Command unrecognized", message_stack).bytes())
                await writer.drain()

            
        except TimeoutError:
            writer.write(MessageLine("500 Connection timed out", message_stack).bytes())
            await writer.drain()
            server_log.log(f"Connection {addr[0]} port {addr[1]} timeout", type="request_warning")
            break
        except UnicodeDecodeError as e:
            writer.write(MessageLine("500 Invalid character", message_stack).bytes())
            await writer.drain()
            server_log.log(f"Connection {addr[0]} port {addr[1]} invalid character", type="request_error")
            break
        except NuMailError as e:
            writer.write(MessageLine("500 Unexpected error", message_stack).bytes())
            await writer.drain()
            server_log.log(f"Connection {addr[0]} port {addr[1]}:\n{e}", type="request_error")
            if e.shutdown == True:
                raise e
            break
        except Exception as e:
            writer.write(MessageLine("500 Unexpected error", message_stack).bytes())
            await writer.drain()
            server_log.log(f"Connection {addr[0]} port {addr[1]}:\n{e}", type="request_error")
            break
    return "exit"

async def email_parse(reader, writer, message_stack):
    writer.write(b"email\r\n")
    await writer.drain()
    msg = await reader.read(1024)
    writer.write(f"{msg.strip()}\r\n".encode("ascii"))
    await writer.drain()