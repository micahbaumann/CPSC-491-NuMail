import asyncio

from message.MessageLine import MessageLine
from message.NuMailMessage import NuMailMessage
from logger.logger import server_log
from config import server_settings

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
            elif trim_message == "EHLO" or (len(trim_message) > 4 and trim_message[:5] == "EHLO "):
                writer.write(MessageLine(f"250 NUMAIL Hello {message_stack.get_client_self_id()}", message_stack).bytes())
                await writer.drain()

            elif trim_message == "HELO" or (len(trim_message) > 4 and trim_message[:5] == "HELO "):
                writer.write(MessageLine(f"250 Hello {message_stack.get_client_self_id()}", message_stack).bytes())
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
        except Exception as e:
            writer.write(MessageLine("500 Unexpected error", message_stack).bytes())
            await writer.drain()
            server_log.log(f"Connection {addr[0]} port {addr[1]}:\n{e}", type="request_error")
            break

async def email_parse(reader, writer, message_stack):
    writer.write(b"email\r\n")
    await writer.drain()
    msg = await reader.read(1024)
    writer.write(f"{msg.strip()}\r\n".encode("ascii"))
    await writer.drain()